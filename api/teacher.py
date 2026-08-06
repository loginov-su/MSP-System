import re
from main import app
from flask import jsonify, render_template, request
from sqlalchemy import text
from flask_bcrypt import Bcrypt
from db import engine

bcrypt = Bcrypt(app)


# -------------------- FRONTEND ROUTES --------------------

@app.route("/create_accounts/new")
def create_account_page():
    """Страница регистрации аккаунта."""
    return render_template("registration.html")


# -------------------- HELPERS --------------------

def validate_phone(phone):
    clean = re.sub(r"\D", "", phone or "")
    return clean.startswith("7") and len(clean) == 11


def validate_password(password):
    """Минимум 8 символов, заглавные и строчные буквы, цифра."""
    if not password or len(password) < 8:
        return False
    if not re.search(r"[a-zA-Zа-яА-ЯёЁ]", password):
        return False
    if not re.search(r"[A-ZА-ЯЁ]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


# -------------------- BACKEND API ROUTES --------------------

@app.route("/api/teacher/validate_invite_code", methods=["POST"])
def validate_invite_code():
    """Проверяет код приглашения для учителя/охраны."""
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()

    if not code:
        return jsonify({"valid": False, "message": "Введите код приглашения"}), 400

    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT role, used FROM invite_codes "
                "WHERE UPPER(code) = :code LIMIT 1"
            ),
            {"code": code},
        ).mappings().fetchone()

    if not row:
        return jsonify({"valid": False, "message": "Неверный код приглашения"}), 404
    if row["used"]:
        return jsonify({"valid": False, "message": "Код уже был использован"}), 409

    return jsonify({"valid": True, "role": row["role"]}), 200


@app.route("/api/teacher/create_account", methods=["POST"])
def create_account():
    """Создание ученика: без кода; учителя/охрана — с кодом приглашения."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Некорректные данные запроса"}), 400

    role = data.get("role")
    if role not in ("student", "teacher", "guard"):
        return jsonify({"status": "error", "message": "Неверная роль"}), 400

    surname = (data.get("surname") or "").strip()
    name = (data.get("name") or "").strip()
    lastname = (data.get("lastname") or "").strip()
    login = (data.get("login") or "").strip().lower()
    password = data.get("password", "")
    phone = (data.get("phone") or "").strip()

    required = ["surname", "name", "login", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({
            "status": "error",
            "message": "Отсутствуют обязательные поля: " + ", ".join(missing)
        }), 400

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", login):
        return jsonify({"status": "error", "message": "Логин должен быть email-адресом"}), 400

    if not validate_password(password):
        return jsonify({"status": "error", "message": "Пароль: минимум 8 символов, заглавные и строчные буквы, цифры"}), 400

    if phone and not validate_phone(phone):
        return jsonify({"status": "error", "message": "Номер должен начинаться с 7 и содержать 11 цифр"}), 400

    code = None
    if role in ("teacher", "guard"):
        invite_code = (data.get("invite_code") or "").strip().upper()
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT role, used FROM invite_codes WHERE UPPER(code) = :code LIMIT 1"),
                {"code": invite_code},
            ).mappings().fetchone()

        if not row or row["used"] or row["role"] != role:
            return jsonify({"status": "error", "message": "Неверный или использованный код приглашения"}), 400

        code = invite_code

    # Проверка уникальности логина
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT id FROM users WHERE login = :login"), {"login": login}
        ).fetchone()
    if exists:
        return jsonify({"status": "error", "message": "Пользователь с таким логином уже существует"}), 409

    group_number = data.get("group_number")
    group_letter = data.get("group_letter")
    if role == "student" and group_number:
        group_number = int(group_number) if str(group_number).isdigit() else None
        group_letter = (group_letter or "").strip().upper() or None

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    "INSERT INTO users "
                    "(role, surname, name, lastname, phone, group_number, group_letter, campus, login, password_hash, is_approved) "
                    "VALUES "
                    "(:role, :surname, :name, :lastname, :phone, :group_number, :group_letter, :campus, :login, :password_hash, :is_approved) "
                    "RETURNING id"
                ),
                {
                    "role": role,
                    "surname": surname,
                    "name": name,
                    "lastname": lastname or None,
                    "phone": phone or None,
                    "group_number": group_number,
                    "group_letter": group_letter,
                    "campus": (data.get("campus") or "modern").strip() or None,
                    "login": login,
                    "password_hash": password_hash,
                    "is_approved": False,
                },
            )
            user_id = result.fetchone()[0]

            # Помечаем код использованным
            if code:
                conn.execute(
                    text("UPDATE invite_codes SET used = TRUE WHERE code = :code"),
                    {"code": code},
                )
    except Exception:
        return jsonify({"status": "error", "message": "Ошибка при сохранении в базу данных"}), 500

    return jsonify({
        "status": "success",
        "user_id": user_id,
        "message": "Аккаунт создан. Дождитесь подтверждения администратором.",
        "redirect": "/",
    }), 200