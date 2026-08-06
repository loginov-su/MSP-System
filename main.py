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


# --- ВРЕМЕННЫЕ (ТЕСТОВЫЕ) МАРШРУТЫ — удалить позже ---
@app.route("/create_exit")
def test_create_exit():
    return render_template("test_app/create_exit.html")


@app.route("/guard/application/all")
def test_guard_application():
    return render_template("test_app/guard_application.html", campus="Mytishchi")


@app.route("/student/application")
def test_student_application():
    application = {
        'id': 1,
        'student_name': 'Иванов Иван Иванович',
        'group': '5А',
        'cause': 'По состоянию здоровья',
        'allowed_exit_time': '2026-08-06T14:00',
        'campus': 'Mytishchi',
    }
    return render_template("test_app/student_application.html",
                           application=application, code='123456')



































if __name__ == "__main__":
    app.run(debug=True, port=3090, host='0.0.0.0')