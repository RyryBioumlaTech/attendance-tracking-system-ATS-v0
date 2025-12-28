from functools import wraps
from flask import session, abort
from flask_login import current_user


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
