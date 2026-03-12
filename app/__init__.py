from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import pymysql
pymysql.install_as_MySQLdb()
from app.qr_code import qr_code_bp
from app.login import login_bp
from app.dashboard import dash_bp
from app.models import db, User
from flask_migrate import Migrate
from dotenv import load_dotenv
from app.utils import create_default_admin
import os

load_dotenv()

login_manager = LoginManager()

socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()  # Crée les tables si elles n'existent pas
        create_default_admin()

    login_manager.init_app(app)
    login_manager.login_view = 'login.show'  # type: ignore

    socketio.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # flask-login only needs id lookup; role-specific behavior is handled elsewhere
        return User.query.get(int(user_id))

    app.register_blueprint(qr_code_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(dash_bp)

    migrate = Migrate(app, db)

    return app