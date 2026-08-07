from flask_login import LoginManager, UserMixin

import config
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine, DateTime, Enum, SmallInteger, func
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
import redis


load_dotenv()

redis_client = redis.from_url(config.REDIS_URL, decode_responses=True)



# Импортируем подключение к БД, и делаем так чтобы проект мог ее использовать #
DATABASE_URL = (
    f"postgresql+psycopg2://{config.POSTGRESQL_USER}:{config.POSTGRESQL_PASSWORD}"
    f"@{config.POSTGRESQL_HOST}:{config.POSTGRESQL_PORT}/{config.POSTGRESQL_DBNAME}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)


def get_db():
    """Возвращает подключение к БД."""
    return engine.connect()


# Создаём расширения БЕЗ привязки к app (паттерн "create once, init app later")
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=config.REDIS_URL,
    storage_options={"socket_connect_timeout": 1},
    default_limits=["200 per day", "60 per minute"],
)


def init_app(app):
    """Привязывает расширения к Flask-приложению и создаёт таблицы."""
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = config.SECRET_KEY

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    if os.environ.get("DB_CREATE_ALL", "1") == "1":
        with app.app_context():
            db.create_all()


def cache_get(key):
    """Читает значение из Redis."""
    try:
        return redis_client.get(key)
    except redis.RedisError:
        return None


def cache_set(key, value, ttl=300):
    """Сохраняет значение в Redis с TTL."""
    try:
        return redis_client.set(key, value, ex=ttl)
    except redis.RedisError:
        return None




# --------------- DataBase Models --------------- #


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.Index("ix_users_fio", "surname", "name", "lastname"),
        db.Index("ix_users_group", "group_number", "group_letter"),
    )

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(
        Enum("student", "teacher", "guard", "admin", name="user_role"),
        nullable=False,
        default="student",
    )
    surname = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    lastname = db.Column(db.String(60))
    phone = db.Column(db.String(20))
    group_number = db.Column(SmallInteger, index=True)
    group_letter = db.Column(db.String(1), index=True)
    campus = db.Column(Enum("pole", "mozaika", name="campus_type"))
    login = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now(), index=True)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_dostup(self):
        return self.role in ("admin", "guard", "teacher")

    @property
    def full_name(self):
        return f"{self.surname} {self.name} {self.lastname}".strip()

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# Более понятный псевдоним для студентов (используется в системе_выхода)
Student = User


class InviteCode(db.Model):
    __tablename__ = "invite_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False, default="teacher")
    used = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())


class ExitApplication(db.Model):
    __tablename__ = "exit_applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    student_name = db.Column(db.String(100))
    student_lastname = db.Column(db.String(100))
    student_group = db.Column(db.String(20))
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ExitApplication {self.id}>"



