from functools import wraps
from flask import session, abort
from flask_login import current_user
from app.models import Admin, db
import os

def create_default_admin():
    if Admin.query.first() is None:  # Vérifie si la table est vide
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_password:
            raise ValueError("Le mot de passe admin doit être défini dans la variable d'environnement ADMIN_PASSWORD")

        admin = Admin(
            login=admin_email,
            role='superAd'
        )
        admin.create_pass(admin_password)
        db.session.add(admin)
        db.session.commit()
        print("Admin par défaut créé avec succès")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Prefer checking the logged-in user (flask-login). Fall back to session.
        if getattr(current_user, 'is_authenticated', False):
            role = getattr(current_user, 'role', None)
            if role in ('admin', 'superAd'):
                return f(*args, **kwargs)
            abort(403)

        # Fallback for older session-based auth
        if session.get('user_type') in ('admin', 'superAd'):
            return f(*args, **kwargs)

        abort(403)

    return decorated_function


def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if getattr(current_user, 'is_authenticated', False):
            role = getattr(current_user, 'role', None)
            if role == 'employee':
                return f(*args, **kwargs)
            abort(403)

        # Fallback for older session-based auth
        if session.get('user_type') == 'employee':
            return f(*args, **kwargs)

        abort(403)

    return decorated_function
