from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import pymysql
pymysql.install_as_MySQLdb()
from app.qr_code import qr_code_bp
from app.login import login_bp
from app.dashboard import dash_bp
from app.models import db, Employee, Admin
from flask_migrate import Migrate

login_manager = LoginManager()

socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    
    app.secret_key = 'bpsr15Dieu@' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ats_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login.show'  # type: ignore

    socketio.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user_type = session.get('user_type')
        if user_type == 'admin':
            return Admin.query.get(int(user_id))
        elif user_type == 'employee':
            return Employee.query.get(int(user_id))
        return None

    app.register_blueprint(qr_code_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(dash_bp)

    migrate = Migrate(app, db)

    return app