import os
import config
from flask import Flask, render_template, send_from_directory

import db_system


app = Flask(__name__)
db_system.init_app(app)


@app.route("/app")
@app.route("/app/")
def app_page():
    return send_from_directory("static/app", "index.html")


@app.route("/system-prompt")
@app.route("/system-prompt/")
def system_prompt_page():
    return render_template("system-screens/sysem-promt.html")




# Подключение API-модулей (blueprints)
from api.ai import ai_api
from api.admin import admin_api

app.register_blueprint(ai_api.ai_api_bp)
app.register_blueprint(admin_api.admin_api_bp)




if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(
        host=os.environ.get("FLASK_HOST", "0.0.0.0"),
        port=int(os.environ.get("FLASK_PORT", "9000")),
        debug=debug,
    )