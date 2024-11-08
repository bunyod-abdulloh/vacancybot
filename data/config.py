from environs import Env

env = Env()
env.read_env()

# TEST_GROUP = env.str("TEST_GROUP")
BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
ADMIN_GROUP = env.str("ADMIN_GROUP")

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")
