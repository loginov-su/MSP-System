from flask import jsonify, request, session, url_for
from sqlalchemy import text
from flask_bcrypt import Bcrypt
from main import app
from db import engine

bcrypt = Bcrypt(app)


@app.route("/api/portal/establish-session", methods=["POST"])
def establish_session():
    """Проверка логина/пароля в БД и установка сессии."""
    data = request.get_json(silent=True) or {}
    login = (data.get("email") or data.get("login") or "").strip().lower()
    password = data.get("password", "")

    if not login:
        return jsonify({"ok": False, "error": "invalid_email"}), 400
    if not password:
        return jsonify({"ok": False, "error": "invalid_password"}), 400

    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT id, role, surname, name, lastname, login, password_hash, "
                "is_approved FROM users WHERE login = :login LIMIT 1"
            ),
            {"login": login},
        ).mappings().fetchone()

    if not row or not bcrypt.check_password_hash(row["password_hash"], password):
        return jsonify({"ok": False, "error": "invalid_password"}), 401

    if not row["is_approved"]:
        return jsonify({"ok": False, "error": "awaiting_approval"}), 403

    display_name = " ".join(
        [row["surname"], row["name"], row["lastname"] or ""]
    ).strip()

    session.permanent = True
    session["user_id"] = row["id"]
    session["role"] = row["role"]
    session["login"] = row["login"]
    session["display_name"] = display_name

    next_url = request.args.get("next")
    redirect_url = url_for("home")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        redirect_url = next_url

    return jsonify({
        "ok": True,
        "display_name": display_name,
        "role": row["role"],
        "redirect": redirect_url,
    }), 200


@app.route("/api/portal/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True}), 200
