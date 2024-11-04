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
        user_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL UNIQUE,
            full_name VARCHAR(255) NULL,
            username VARCHAR(255) NULL,
            phone VARCHAR(50) NULL            
        );
        """
        region_table = """
        CREATE TABLE IF NOT EXISTS regions (
            id SERIAL PRIMARY KEY,
            region_name VARCHAR(500) NOT NULL UNIQUE
        );
        """
        profession_table = """
        CREATE TABLE IF NOT EXISTS professions (
            id SERIAL PRIMARY KEY,
            profession_name VARCHAR(255) NOT NULL UNIQUE
        );
        """
        technology_table = """
        CREATE TABLE IF NOT EXISTS technologies (
            id SERIAL PRIMARY KEY,
            technology_name VARCHAR(500) NOT NULL UNIQUE
        );
        """
        partner_technology_table = """
        CREATE TABLE IF NOT EXISTS partner_technologies (
            partner_id BIGINT NOT NULL REFERENCES users(id),
            technology_id INT NOT NULL REFERENCES technologies(id),            
            PRIMARY KEY (partner_id, technology_id)
        );
        """
        srch_partner_table = """
        CREATE TABLE IF NOT EXISTS srch_partner (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id),            
            region_id INT NULL REFERENCES regions(id),
            profession_id INT NULL REFERENCES professions(id),
            apply_time VARCHAR(60) NULL,
            cost VARCHAR(60) NULL,
            maqsad VARCHAR(2000) NULL              
        );
        """

        await self.execute(user_table, execute=True)
        await self.execute(region_table, execute=True)
        await self.execute(profession_table, execute=True)
        await self.execute(technology_table, execute=True)
        await self.execute(partner_technology_table, execute=True)
        await self.execute(srch_partner_table, execute=True)

    # ======================= USERS CRUD =======================
    async def add_user(self, telegram_id, username=None, full_name=None, phone=None):
        sql_insert = """
        INSERT INTO users (telegram_id, username, full_name, phone) 
        VALUES ($1, $2, $3, $4) 
        ON CONFLICT (telegram_id) DO NOTHING 
        RETURNING id
        """
        user = await self.execute(sql_insert, telegram_id, username, full_name, phone, fetchrow=True)

        if user:
            return user  # Yangi yozuv yaratildi
        else:
            sql_select = "SELECT id FROM users WHERE telegram_id=$1"
            return await self.execute(sql_select, telegram_id, fetchrow=True)

    async def update_user(self, telegram_id, field, value):
        sql = f"UPDATE users SET {field}=$1 WHERE telegram_id=$2"
        return await self.execute(sql, value, telegram_id, fetchrow=True)

    async def delete_user(self, telegram_id):
        sql = "DELETE FROM users WHERE telegram_id=$1"
        await self.execute(sql, telegram_id, execute=True)

    # ======================= SRCH_PARTNER CRUD =======================
    async def add_srch_partner(self, user_id, region_id, profession_id, apply_time, cost, maqsad):
        sql = """
        INSERT INTO srch_partner (user_id, region_id, profession_id, apply_time, cost, maqsad)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING id
        """
        return await self.execute(sql, user_id, region_id, profession_id, apply_time, cost, maqsad, fetchrow=True)

    async def add_partner_technologies(self, partner_id, technology_ids):
        for technology_id in technology_ids:
            sql = f"""
            INSERT INTO partner_technologies (partner_id, technology_id)
            VALUES ($1, $2)
            ON CONFLICT (partner_id, technology_id) DO NOTHING
            RETURNING partner_id
            """
            await self.execute(sql, partner_id, technology_id, fetchrow=True)

    async def update_srch_partner(self, user_id, field, value):
        sql = f"UPDATE srch_partner SET {field}=$1 WHERE user_id=$2"
        return await self.execute(sql, value, user_id, fetchrow=True)

    async def get_srch_partner(self, user_id):
        sql = "SELECT * FROM srch_partner WHERE user_id=$1"
        return await self.execute(sql, user_id, fetchrow=True)

    async def get_partner_technologies(self, partner_id):
        sql = "SELECT * FROM partner_technologies WHERE partner_id=$1"
        return await self.execute(sql, partner_id, fetch=True)

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

    async def drop_table(self, table):
        sql = f"DROP TABLE {table} CASCADE"
        await self.execute(sql, execute=True)
