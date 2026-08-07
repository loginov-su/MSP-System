import requests
import config
from flask import Flask, render_template, jsonify, request
from datetime import timedelta
from db import init_db




# Инцилизация Flask приложения #
app = Flask(__name__)
app.config.update(SECRET_KEY=config.SECRET_KEY)
app.permanent_session_lifetime = timedelta(days=365)




@app.route("/")
def login():
    return render_template("login.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/exit/new")
def exit_new():
    return render_template("exit/new.html")


@app.route("/exit/history")
def exit_history():
    return render_template("not_dostup.html")


@app.route("/guard")
def guard_stub():
    return render_template("not_dostup.html")


@app.route("/guest")
def guest_stub():
    return render_template("not_dostup.html")


# Сервисы (пока заглушки)
@app.route("/news")
def news_stub():
    return render_template("not_dostup.html")


@app.route("/events")
def events_stub():
    return render_template("not_dostup.html")


@app.route("/schedule")
def schedule_stub():
    return render_template("not_dostup.html")


@app.route("/campus-map")
def campus_map_stub():
    return render_template("not_dostup.html")


@app.route("/smartstop")
def smartstop_stub():
    return render_template("not_dostup.html")


@app.route("/profile")
def profile_stub():
    return render_template("not_dostup.html")


@app.route("/api/exit/my_application", methods=["POST"])
def test_create_application_api():
    data = request.get_json(silent=True) or {}
    required = ['fio', 'group_number', 'group_letter', 'cause', 'time']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'status': 'error',
                        'message': 'Отсутствуют обязательные поля: ' + ", ".join(missing)}), 400
    return jsonify({'status': 'success', 'application_id': 1, 'code': '123456'}), 200


# Регистрация маршрутов из API-модулей
import sys
# Модуль API делает "from main import app". При запуске "python main.py"
# модуль называется __main__, поэтому алиасим его как main, чтобы импорт
# ссылался на тот же экземпляр приложения.
sys.modules['main'] = sys.modules['__main__']
from api import teacher  # noqa: E402
from api import auth  # noqa: E402


# Инициализация базы данных (создание таблиц)
init_db()



































if __name__ == "__main__":
    app.run(debug=True, port=3090, host='0.0.0.0')