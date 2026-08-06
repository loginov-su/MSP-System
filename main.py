import requests
import config
from flask_login import login_required, login_manager, current_user
from flask import Flask, render_template
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String
from openpyxl import Workbook
from io import BytesIO
from datetime import timedelta, datetime
from flask_bcrypt import Bcrypt




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


# Регистрация маршрутов из API-модулей
import sys
# Модуль API делает "from main import app". При запуске "python main.py"
# модуль называется __main__, поэтому алиасим его как main, чтобы импорт
# ссылался на тот же экземпляр приложения.
sys.modules['main'] = sys.modules['__main__']
from api import teacher  # noqa: E402



































if __name__ == "__main__":
    app.run(debug=True, port=3090, host='0.0.0.0')