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



































if __name__ == "__main__":
    app.run(debug=True, port=3090, host='0.0.0.0')