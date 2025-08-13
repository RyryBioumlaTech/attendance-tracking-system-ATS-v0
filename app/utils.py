from functools import wraps
from flask import redirect, url_for, session, abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            abort(403)  # ou redirect vers une page interdite
        return f(*args, **kwargs)
    return decorated_function

def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'employee':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
