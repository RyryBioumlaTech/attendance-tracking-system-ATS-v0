from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from app.models import Admin, Employee
from app.models import db
from app.login import login_bp
from app.utils import employee_required


@login_bp.route('/')
def show():
    return render_template('login.html')


@login_bp.route('/login', methods=['POST'])
def login():

    email = request.form.get('email')
    password = request.form.get('password')

    user = Employee.query.filter_by(email=email).first()
    admin = Admin.query.filter_by(login=email).first()

    # LOGIN EMPLOYEE
    if user and user.verify_pass(password):

        login_user(user)
        session['user_type'] = 'employee'

        # mot de passe par défaut → forcer changement
        if user.verify_pass("12345678"):
            return redirect(url_for('login.changePass'))

        return redirect(url_for('login.scanner'))

    # LOGIN ADMIN
    if admin and admin.verify_pass(password):

        login_user(admin)
        session['user_type'] = 'admin'
        return redirect(url_for('dashboard.admin_dash'))

    flash('Identifiants invalides !', 'danger')
    return redirect(url_for('login.show'))


@login_bp.route('/updatePass', methods=['POST'])
@login_required
@employee_required
def updatePass():

    new_pass = request.form.get('password', '').strip()
    confirmed_pass = request.form.get('confirm_password', '').strip()

    if not new_pass or not confirmed_pass:
        flash('Please fill all fields', 'warning')
        return redirect(url_for('login.changePass'))

    if new_pass != confirmed_pass:
        flash('Inputs must be the same', 'warning')
        return redirect(url_for('login.changePass'))

    # on modifie uniquement le mot de passe de l'utilisateur connecté
    user = current_user

    user.create_pass(new_pass)
    db.session.commit()

    flash("Password updated successfully", "success")

    return redirect(url_for('login.scanner'))


@login_bp.route('/scanner')
@login_required
@employee_required
def scanner():
    return render_template('scanner.html', user=current_user)


@login_bp.route('/changePass')
@login_required
@employee_required
def changePass():
    return render_template('changepass.html', user=current_user)


@login_bp.route('/logout')
@login_required
def logout():

    logout_user()
    session.clear()

    flash('You have been logged out!', 'info')
    return redirect(url_for('login.show'))