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
                user_id BIGINT NOT NULL UNIQUE REFERENCES users(id),
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
                profession_name VARCHAR(255) NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS technologies (
                id SERIAL PRIMARY KEY,
                technology_name VARCHAR(100) NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS user_technologies (
                user_id BIGINT NOT NULL REFERENCES users(id),
                technology_id INTEGER NOT NULL REFERENCES technologies(id),
                table_name VARCHAR(10)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS srch_partner (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id),                
                profession_id INTEGER REFERENCES professions(id),
                apply_time VARCHAR(60),
                cost VARCHAR(60),
                maqsad VARCHAR(2000),
                region_id INTEGER REFERENCES regions(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS srch_job (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id),                
                profession_id INTEGER REFERENCES professions(id),
                apply_time VARCHAR(60),
                cost VARCHAR(60),
                maqsad VARCHAR(2000),
                region_id INTEGER REFERENCES regions(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS idoralar (                
                id SERIAL PRIMARY KEY,                
                idora_nomi VARCHAR(255),
                masul VARCHAR(255),                
                qoshimcha VARCHAR(2000),
                region_id INTEGER REFERENCES regions(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS srch_worker (
                id SERIAL PRIMARY KEY,                                
                idora_id INTEGER NOT NULL REFERENCES idoralar(id),                                              
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
            return user  # Yangi yozuv yaratildi yoki mavjud yozuv yangilandi
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

    async def update_user(self, field, value):
        sql = f"UPDATE users SET {field}=$1 WHERE telegram_id=$2"
        return await self.execute(sql, value, fetchrow=True)

    async def delete_user(self, telegram_id):
        sql = "DELETE FROM users WHERE telegram_id=$1"
        await self.execute(sql, telegram_id, execute=True)

    # ======================= SRCH_PARTNER CRUD =======================
    async def add_srch_partner(self, user_id, profession_id, apply_time, cost, maqsad, region_id):
        sql = """
            INSERT INTO srch_partner (user_id, profession_id, apply_time, cost, maqsad, region_id)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING id
            """
        return await self.execute(sql, user_id, profession_id, apply_time, cost, maqsad, region_id, fetchrow=True)

    async def add_srch_job(self, user_id, profession_id, apply_time, cost, maqsad, region_id):
        sql = """
            INSERT INTO srch_job (user_id, profession_id, apply_time, cost, maqsad, region_id)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING id
            """
        return await self.execute(sql, user_id, profession_id, apply_time, cost, maqsad, region_id, fetchrow=True)

    async def add_idoralar(self, idora_nomi, masul, qoshimcha, region_id):
        sql = """
            INSERT INTO idoralar (idora_nomi, masul, qoshimcha, region_id)
            VALUES ($1, $2, $3, $4) RETURNING id
            """
        return await self.execute(sql, idora_nomi, masul, qoshimcha, region_id, fetchrow=True)

    async def add_srch_worker(self, idora_id, m_vaqti, i_vaqti, maosh):
        sql = """
            INSERT INTO srch_worker (idora_id, m_vaqti, i_vaqti, maosh)
            VALUES ($1, $2, $3, $4) RETURNING id
            """
        return await self.execute(sql, idora_id, m_vaqti, i_vaqti, maosh, fetchrow=True)

    async def add_technologies(self, user_id, technology_ids, table_name):
        for technology_id in technology_ids:
            sql = f"""
                INSERT INTO user_technologies (user_id, technology_id, table_name)
                VALUES ($1, $2, $3) RETURNING user_id
            """
            await self.execute(sql, user_id, technology_id, table_name, fetchrow=True)

    # ON CONFLICT(user_id, technology_id) DO NOTHING
    async def update_srch_partner(self, user_id, field, value):
        sql = f"UPDATE srch_partner SET {field}=$1 WHERE user_id=$2"
        return await self.execute(sql, value, user_id, fetchrow=True)

    async def get_srch_partner(self, user_id):
        sql = "SELECT * FROM srch_partner WHERE user_id=$1"
        return await self.execute(sql, user_id, fetchrow=True)

    async def get_technologies(self, user_id):
        sql = "SELECT * FROM user_technologies WHERE user_id=$1"
        return await self.execute(sql, user_id, fetch=True)

    async def delete_srch_partner(self, user_id):
        sql = "DELETE FROM srch_partner WHERE user_id=$1"
        await self.execute(sql, user_id, execute=True)

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

    async def get_all_entries(self, table):
        sql = f"SELECT * FROM {table}"
        return await self.execute(sql, fetch=True)

    async def delete_from_table(self, table, field, value):
        sql = f"DELETE FROM {table} WHERE {field}=$1 CASCADE"
        await self.execute(sql, value, execute=True)

    async def drop_tables(self):
        tables = ['users', 'users_data', 'regions', 'professions', 'technologies', 'user_technologies', 'srch_partner',
                  'srch_job', 'idoralar', 'srch_worker']

        for table in tables:
            sql = f"DROP TABLE {table} CASCADE"
            await self.execute(sql, execute=True)
