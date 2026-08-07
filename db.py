import os
import time
import config
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# DATABASE_URL для SQLAlchemy
DATABASE_URL = (
    f"postgresql+psycopg2://{config.POSTGRESQL_USER}:{config.POSTGRESQL_PASSWORD}"
    f"@{config.POSTGRESQL_HOST}:{config.POSTGRESQL_PORT}/{config.POSTGRESQL_DBNAME}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)


def get_db():
    """Возвращает подключение к БД."""
    return engine.connect()


# -------------------- Инициализация схемы --------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    role            VARCHAR(20)  NOT NULL DEFAULT 'student',
    surname         VARCHAR(100) NOT NULL,
    name            VARCHAR(100) NOT NULL,
    lastname        VARCHAR(100),
    phone           VARCHAR(20),
    group_number    INTEGER,
    group_letter    VARCHAR(1),
    campus          VARCHAR(20),
    login           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    is_approved     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invite_codes (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20) NOT NULL UNIQUE,
    role        VARCHAR(20) NOT NULL DEFAULT 'teacher',
    used        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""


def init_db():
    """Создаёт таблицы, если их нет."""
    with engine.begin() as conn:
        for statement in SCHEMA.split(";"):
            if statement.strip():
                conn.execute(text(statement))

    # Тестовый код приглашения для учителей/охраны, если таблица пуста
    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM invite_codes")).scalar()
        if count == 0:
            conn.execute(
                text(
                    "INSERT INTO invite_codes (code, role) VALUES "
                    "(:c1, 'teacher'), (:c2, 'guard')"
                ),
                {"c1": "TEACHER2026", "c2": "GUARD2026"},
            )
