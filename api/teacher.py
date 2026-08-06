import os
from main import app
from flask import jsonify, render_template, request
from flask_login import login_required


# -------------------- FRONTEND ROUTES --------------------

@app.route("/create_accounts/new")
def create_account_page():
    """Страница регистрации аккаунта."""
    return render_template("registration.html")


# -------------------- BACKEND API ROUTES --------------------

@app.route("/api/teacher/create_account", methods=["POST"])
def create_account():
    """API создания аккаунта."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'Некорректные данные запроса'}), 400

    required = ['surname', 'name', 'role', 'login', 'password']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({
            'status': 'error',
            'message': 'Отсутствуют обязательные поля: ' + ", ".join(missing)
        }), 400

    if len(data.get('password', '')) < 6:
        return jsonify({'status': 'error', 'message': 'Пароль должен быть не короче 6 символов'}), 400

    # TODO: подключить базу данных и реальное создание пользователя
    return jsonify({
        'status': 'success',
        'message': 'Аккаунт создан. Дождитесь подтверждения администратором.'
    }), 200
