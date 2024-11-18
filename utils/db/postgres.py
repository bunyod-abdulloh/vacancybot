from typing import Union

import asyncpg
from asyncpg import Connection, Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(self, command, *args, fetch=False, fetchval=False, fetchrow=False, execute=False):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    return await connection.fetch(command, *args)
                elif fetchval:
                    return await connection.fetchval(command, *args)
                elif fetchrow:
                    return await connection.fetchrow(command, *args)
                elif execute:
                    return await connection.execute(command, *args)

    # ======================= TABLE CREATION =======================
    async def create_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS users_data (
                user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                full_name VARCHAR(255),
                username VARCHAR(255),
                age VARCHAR(2),
                phone VARCHAR(50)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS regions (
                id SERIAL PRIMARY KEY,
                region_name VARCHAR(255) NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS professions (
                id SERIAL PRIMARY KEY,
                profession VARCHAR(255) NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS technologies (
                id SERIAL PRIMARY KEY,
                technology_name VARCHAR(100) NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS user_techs (
                user_id INTEGER,
                id INTEGER NOT NULL REFERENCES technologies(id),
                table_name VARCHAR(20)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS need_partner (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                profession_id INTEGER REFERENCES professions(id) ON DELETE CASCADE,
                apply_time VARCHAR(60),
                cost VARCHAR(60),
                maqsad VARCHAR(2000),
                region_id INTEGER REFERENCES regions(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS need_job (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                profession_id INTEGER REFERENCES professions(id) ON DELETE CASCADE,
                apply_time VARCHAR(60),
                cost VARCHAR(60),
                maqsad VARCHAR(2000),
                region_id INTEGER REFERENCES regions(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS need_teacher (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                profession_id INTEGER REFERENCES professions(id) ON DELETE CASCADE,
                apply_time VARCHAR(60),
                cost VARCHAR(60),
                maqsad VARCHAR(2000),
                region_id INTEGER REFERENCES regions(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS need_apprentice (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                profession_id INTEGER REFERENCES professions(id) ON DELETE CASCADE,
                apply_time VARCHAR(60),
                cost VARCHAR(60),
                maqsad VARCHAR(2000),
                region_id INTEGER REFERENCES regions(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS idoralar (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                idora_nomi VARCHAR(255),
                masul VARCHAR(255),
                qoshimcha VARCHAR(2000),
                region_id INTEGER REFERENCES regions(id) ON DELETE CASCADE              
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS need_worker (
                id SERIAL PRIMARY KEY,
                idora_id INTEGER NOT NULL REFERENCES idoralar(id) ON DELETE CASCADE,
                m_vaqti VARCHAR(60),
                i_vaqti VARCHAR(60),
                maosh VARCHAR(60)                
            );
            """
        ]

        for query in queries:
            await self.execute(query, execute=True)

    # ======================= USERS CRUD =======================
    async def add_user(self, telegram_id):
        sql_insert = """
        INSERT INTO users (telegram_id) VALUES ($1) ON CONFLICT (telegram_id) DO NOTHING RETURNING id
        """
        user = await self.execute(sql_insert, telegram_id, fetchrow=True)
        if user:
            return user
        else:
            sql_select = "SELECT id FROM users WHERE telegram_id=$1"
            return await self.execute(sql_select, telegram_id, fetchrow=True)

    async def add_user_datas(self, user_id, full_name, username, age, phone):
        sql = """
        INSERT INTO users_data (user_id, full_name, username, age, phone)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id) DO UPDATE
        SET age = EXCLUDED.age
        WHERE users_data.age IS NULL
        """
        return await self.execute(sql, user_id, full_name, username, age, phone, fetchrow=True)

    async def get_user_data(self, telegram_id):
        sql = f"SELECT * FROM users_data INNER JOIN users ON users_data.user_id = users.id WHERE users.telegram_id = $1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def update_user(self, field, value):
        sql = f"UPDATE users SET {field}=$1 WHERE telegram_id=$2"
        return await self.execute(sql, value, fetchrow=True)

    async def delete_user(self, telegram_id):
        sql = "DELETE FROM users WHERE telegram_id=$1"
        await self.execute(sql, telegram_id, execute=True)

    # ======================= SRCH_PARTNER CRUD =======================
    # Umumiy CRUD yordamchi funksiya
    async def _add_entry_to_table(self, table, user_id, profession_id, apply_time, cost, maqsad, region_id):
        sql = f"""
            INSERT INTO {table} (user_id, profession_id, apply_time, cost, maqsad, region_id)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING id
        """
        return await self.execute(sql, user_id, profession_id, apply_time, cost, maqsad, region_id, fetchrow=True)

    async def add_srch_partner(self, user_id, profession_id, apply_time, cost, maqsad, region_id):
        return await self._add_entry_to_table(
            "need_partner", user_id, profession_id, apply_time, cost, maqsad, region_id
        )

    async def add_srch_job(self, user_id, profession_id, apply_time, cost, maqsad, region_id):
        return await self._add_entry_to_table(
            "need_job", user_id, profession_id, apply_time, cost, maqsad, region_id
        )

    async def add_need_teacher(self, user_id, profession_id, apply_time, cost, maqsad, region_id):
        return await self._add_entry_to_table(
            "need_teacher", user_id, profession_id, apply_time, cost, maqsad, region_id
        )

    async def add_apprentice(self, user_id, profession_id, apply_time, cost, maqsad, region_id):
        return await self._add_entry_to_table(
            "need_apprentice", user_id, profession_id, apply_time, cost, maqsad, region_id
        )

    async def add_idoralar(self, idora_nomi, masul, qoshimcha, region_id, user_id):
        sql = """
            INSERT INTO idoralar (idora_nomi, masul, qoshimcha, region_id, user_id)
            VALUES ($1, $2, $3, $4, $5) RETURNING id
        """
        return await self.execute(sql, idora_nomi, masul, qoshimcha, region_id, user_id, fetchrow=True)

    async def add_srch_worker(self, idora_id, m_vaqti, i_vaqti, maosh):
        sql = """
            INSERT INTO need_worker (idora_id, m_vaqti, i_vaqti, maosh)
            VALUES ($1, $2, $3, $4) RETURNING id
        """
        return await self.execute(sql, idora_id, m_vaqti, i_vaqti, maosh, fetchrow=True)

    async def add_technologies(self, user_id, technology_id, table_name):
        sql = f"""
                INSERT INTO user_techs (user_id, id, table_name)
                VALUES ($1, $2, $3) RETURNING user_id
            """
        await self.execute(sql, user_id, technology_id, table_name, fetchrow=True)

    async def get_idora(self, irow_id):
        sql = f"SELECT idr.idora_nomi, idr.masul, nw.m_vaqti, nw.i_vaqti, nw.maosh, idr.qoshimcha, idr.region_id FROM need_worker AS nw INNER JOIN idoralar AS idr ON nw.idora_id = idr.id WHERE idr.id = $1"
        return await self.execute(sql, irow_id, fetchrow=True)

    async def get_techs(self, user_id, table_name):
        sql = f"SELECT * FROM user_techs WHERE user_id=$1 AND table_name=$2"
        return await self.execute(sql, user_id, table_name, fetch=True)

    # ======================= GENERIC CRUD =======================
    async def add_entry(self, table, field, value):
        sql_insert = f"INSERT INTO {table} ({field}) VALUES($1) ON CONFLICT ({field}) DO NOTHING RETURNING id"
        entry = await self.execute(sql_insert, value, fetchrow=True)
        if entry:
            return entry
        else:
            sql_select = f"SELECT id FROM {table} WHERE {field} = $1"
            return await self.execute(sql_select, value, fetchrow=True)

    async def get_entry(self, table, field, value):
        sql = f"SELECT * FROM {table} WHERE {field}=$1"
        return await self.execute(sql, value, fetchrow=True)

    async def get_entries(self, table, field, value):
        sql = f"SELECT * FROM {table} WHERE {field}=$1"
        return await self.execute(sql, value, fetch=True)

    async def get_all_entries(self, table):
        sql = f"SELECT * FROM {table}"
        return await self.execute(sql, fetch=True)

    async def delete_from_table(self, table, field, value):
        sql = f"DELETE FROM {table} WHERE {field}=$1"
        await self.execute(sql, value, execute=True)

    async def drop_tables(self):
        tables = ['user_techs', 'need_partner', 'need_job', 'idoralar', 'need_worker', 'users', 'users_data', 'regions',
                  'professions', 'technologies']

        for table in tables:
            sql = f"DROP TABLE {table} CASCADE"
            await self.execute(sql, execute=True)
