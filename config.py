# config.py
import os
from dotenv import load_dotenv

load_dotenv()


# --- База данных ---
POSTGRESQL_HOST = os.environ["POSTGRESQL_HOST"]
POSTGRESQL_PORT = os.environ["POSTGRESQL_PORT"]
POSTGRESQL_USER = os.environ["POSTGRESQL_USER"]
POSTGRESQL_PASSWORD = os.environ["POSTGRESQL_PASSWORD"]
POSTGRESQL_DBNAME = os.environ["POSTGRESQL_DBNAME"]


# Секретный ключ Flask #
SECRET_KEY = os.getenv("SECRET_KEY")