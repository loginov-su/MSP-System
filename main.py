import config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import current_user, login_manager, login_required


app = Flask(__name__)













if __name__ == "__main__":
    app.run(debug=True, port=93033)