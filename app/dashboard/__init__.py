from flask import Blueprint

dash_bp = Blueprint('dashboard', __name__, template_folder='../templates')

from app.dashboard import routes