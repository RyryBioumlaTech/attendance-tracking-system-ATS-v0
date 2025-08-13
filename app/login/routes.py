from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user
from app.models import Admin, Employee
from app.models import db
from app.login import login_bp

@login_bp.route('/')
def show():
    return render_template('login.html')

@login_bp.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    user = Employee.query.filter_by(email = email).first()
    admin = Admin.query.filter_by(login = email).first()

    if (user and user.verify_pass(password)):

        login_user(user)
        session['user_type'] = 'employee'
        return redirect(url_for('dashboard.user_dash'))
    elif (admin and admin.verify_pass(password)):

        login_user(admin)
        session['user_type'] = 'admin'
        return redirect(url_for('dashboard.admin_dash'))
    else:
        flash('identifiants invalides !')
    return redirect(url_for('login.show'))


@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logout !')
    return redirect(url_for('login.show'))