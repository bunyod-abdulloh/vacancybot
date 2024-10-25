from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

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

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False,
    ):

        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    # ======================= TABLE | USERS =======================
    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,        
        telegram_id BIGINT NOT NULL UNIQUE,               
        );
        """
        await self.execute(sql, execute=True)

    async def add_user(self, username, telegram_id):
        sql = "INSERT INTO users (username, telegram_id) VALUES($1, $2)"
        return await self.execute(sql, username, telegram_id, fetchrow=True)

    async def update_user_fullname(self, fullname, telegram_id):
        sql = "UPDATE users SET full_name=$1 WHERE telegram_id=$2"
        return await self.execute(sql, fullname, telegram_id, fetchrow=True)

    async def update_user_phone(self, phone, telegram_id):
        sql = "UPDATE users SET phone=$1 WHERE telegram_id=$2"
        return await self.execute(sql, phone, telegram_id, fetchrow=True)

    async def update_user_address(self, address, telegram_id):
        sql = "UPDATE users SET address=$1 WHERE telegram_id=$2"
        return await self.execute(sql, address, telegram_id, fetchrow=True)

    async def update_user_passport_a_side(self, passport_a_side, telegram_id):
        sql = "UPDATE users SET passport_a_side=$1 WHERE telegram_id=$2"
        return await self.execute(sql, passport_a_side, telegram_id, fetchrow=True)

    async def update_user_passport_b_side(self, passport_b_side, telegram_id):
        sql = "UPDATE users SET passport_b_side=$1 WHERE telegram_id=$2"
        return await self.execute(sql, passport_b_side, telegram_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, telegram_id):
        sql = f"SELECT * FROM users WHERE telegram_id='{telegram_id}'"
        return await self.execute(sql, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.execute(sql, fetchval=True)

    async def delete_users(self):
        await self.execute("DELETE FROM users WHERE TRUE", execute=True)

    async def delete_user(self, telegram_id):
        await self.execute(f"DELETE FROM users WHERE telegram_id='{telegram_id}'", execute=True)

    async def drop_table_users(self):
        await self.execute("DROP TABLE users", execute=True)

    # ======================= REGIONS =======================
    async def create_table_regions(self):
        sql = """
        CREATE TABLE IF NOT EXISTS regions (
        id SERIAL PRIMARY KEY,
        region_name VARCHAR(500) NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    async def add_region(self, region_name):
        sql = "INSERT INTO regions (region_name) VALUES($1) returning id"
        return await self.execute(sql, region_name, fetchrow=True)

    # ======================= PROFESSIONS =======================
    async def create_table_professions(self):
        sql = """
        CREATE TABLE IF NOT EXISTS professions (
        id SERIAL PRIMARY KEY,
        profession_name VARCHAR(255) NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    async def add_profession(self, profession_name):
        sql = "INSERT INTO professions (profession_name) VALUES($1) returning id"
        return await self.execute(sql, profession_name, fetchrow=True)

    # ======================= PARTNER_TECHNOLOGIES =======================
    async def create_table_technologies(self):
        sql = """
        CREATE TABLE IF NOT EXISTS technologies (
        id SERIAL PRIMARY KEY,
        technology_name VARCHAR(500) NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    async def add_technology(self, technology_name):
        sql = "INSERT INTO technologies (technology_name) VALUES($1)"
        return await self.execute(sql, technology_name, fetchrow=True)

    async def create_table_partner_technologies(self):
        sql = """
        CREATE TABLE IF NOT EXISTS partner_technologies (        
        partner_id BIGINT NOT NULL REFERENCES srch_partner(telegram_id),
        technology_id INTEGER NOT NULL REFERENCES technologies(id),
        PRIMARY KEY (partner_id, technology_id)
        );
        """
        await self.execute(sql, execute=True)

    async def add_partner_technologies(self, partner_id, technology_id):
        sql = "INSERT INTO partner_technologies (partner_id, technology_id) VALUES($1, $2)"
        return await self.execute(sql, partner_id, technology_id, fetchrow=True)

    # ======================= TABLE | SEARCH PARTNER =======================
    async def search_partner(self):
        sql = """
        CREATE TABLE IF NOT EXISTS srch_partner (
        telegram_id BIGINT NOT NULL UNIQUE,
        full_name VARCHAR(255) NULL,
        username VARCHAR(255) NULL,
        phone VARCHAR(50) NULL, 
        region_id INT NULL REFERENCES regions(id),
        cost VARCHAR(60) NULL,
        profession_id INT NULL REFERENCES professions(id),
        apply_time VARCHAR(60) NULL, 
        maqsad VARCHAR(1000) NULL
        );
        """
        await self.execute(sql, execute=True)

    async def add_srch_partner(self, telegram_id, full_name, username, phone, region_id, cost, profession_id,
                               apply_time, maqsad):
        sql = ("INSERT INTO srch_partner (telegram_id, full_name, username, phone, region_id, cost, profession_id, "
               "apply_time, maqsad) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)")
        return await self.execute(sql, telegram_id, full_name, username, phone, region_id, cost, profession_id,
                                  apply_time, maqsad, fetchrow=True)


    async def select_all_tables(self, table_type):
        sql = f"SELECT * FROM medialar_tables WHERE table_type='{table_type}' ORDER BY table_number ASC"
        return await self.execute(sql, fetch=True)

    async def select_table_tables(self):
        sql = "SELECT * FROM medialar_tables"
        return await self.execute(sql, fetch=True)

    async def get_channel_id(self, table_number):
        sql = f"SELECT channel_id FROM medialar_tables WHERE table_number='{table_number}'"
        return await self.execute(sql, fetchrow=True)

    async def select_media_by_id(self, table_number):
        sql = f"SELECT * FROM medialar_tables WHERE table_number='{table_number}'"
        return await self.execute(sql, fetchrow=True)

    async def delete_table_tables(self, table_number):
        await self.execute(f"DELETE FROM medialar_tables WHERE table_number='{table_number}'", execute=True)

    async def drop_table_tables(self):
        await self.execute(f"DROP TABLE medialar_tables", execute=True)
