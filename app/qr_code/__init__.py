from flask import Blueprint

qr_code_bp = Blueprint('qr_code', __name__, template_folder='../templates')

from app.qr_code import routes

