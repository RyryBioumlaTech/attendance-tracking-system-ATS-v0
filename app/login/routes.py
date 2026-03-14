from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User, db
from app.login import login_bp
import os


DEFAULT_PASSWORD = os.getenv("DEFAULT_EMP_PASSWORD")


@login_bp.route("/")
def show():
    return render_template("login.html")


@login_bp.route("/login", methods=["POST"])
def login():

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    if not email or not password:
        flash("Please fill all fields", "warning")
        return redirect(url_for("login.show"))

    user = User.query.filter_by(email=email).first()
    print('this is user : ', user)
    print('password received : ', password)
    print('password hash in db : ', user.password_hash if user else 'no user found')
    print('current password hashed : ', user.set_password(password) or user.password_hash if user else 'no user found')
    print('password verified : ', user.verify_pass(password) if user else 'no user found')

    if not user or not user.verify_pass(password):
        flash("Invalid credentials", "danger")
        return redirect(url_for("login.show"))

    login_user(user)

    if user.is_admin() or user.is_super_admin():
        return redirect(url_for("dashboard.admin_dash"))

    if user.is_employee():

        # mot de passe par défaut → forcer changement
        if user.verify_pass(DEFAULT_PASSWORD):
            flash("You must change your default password", "warning")
            return redirect(url_for("login.changePass"))

        return redirect(url_for("login.scanner"))

    flash("Unauthorized account", "danger")
    return redirect(url_for("login.show"))


@login_bp.route("/changePass")
@login_required
def changePass():

    if not current_user.is_employee():
        return redirect(url_for("login.show"))

    return render_template("changepass.html", user=current_user)


@login_bp.route("/updatePass", methods=["POST"])
@login_required
def updatePass():

    if not current_user.is_employee():
        return redirect(url_for("login.show"))

    new_pass = request.form.get("password", "").strip()
    confirmed_pass = request.form.get("confirm_password", "").strip()

    if not new_pass or not confirmed_pass:
        flash("Please fill all fields", "warning")
        return redirect(url_for("login.changePass"))

    if new_pass != confirmed_pass:
        flash("Passwords do not match", "warning")
        return redirect(url_for("login.changePass"))

    if len(new_pass) < 8:
        flash("Password must be at least 8 characters", "warning")
        return redirect(url_for("login.changePass"))

    current_user.set_password(new_pass)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Error updating password", "danger")
        return redirect(url_for("login.changePass"))

    flash("Password updated successfully", "success")
    return redirect(url_for("login.scanner"))


@login_bp.route("/scanner")
@login_required
def scanner():

    if not current_user.is_employee():
        return redirect(url_for("login.show"))

    return render_template("scanner.html", user=current_user)


@login_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("You have been logged out", "info")

    return redirect(url_for("login.show"))