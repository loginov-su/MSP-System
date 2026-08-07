import config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, send_from_directory
from flask_bcrypt import Bcrypt
from flask_login import current_user, login_manager, login_required


app = Flask(__name__)


@app.route("/app")
@app.route("/app/")
def app_page():
    return send_from_directory("static/app", "index.html")


@app.route("/system-prompt")
@app.route("/system-prompt/")
def system_prompt_page():
    return render_template("system-screens/sysem-promt.html")




# Подключение API-модулей (blueprints)
from api import ai_api

app.register_blueprint(ai_api.ai_api_bp)




if __name__ == "__main__":
    app.run(debug=True, port=9000)