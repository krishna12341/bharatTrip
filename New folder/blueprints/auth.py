from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import check_password_hash

from models import User

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password, password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        login_user(user)
        return redirect(url_for("dashboard.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=("GET", "POST"))
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("If this email exists, a reset link has been sent.", "info")
            return redirect(url_for("auth.login"))

        token = get_serializer().dumps(user.email, salt="password-reset")
        reset_url = url_for("auth.reset_password", token=token, _external=True)
        current_app.email_service.send_password_reset(user.email, reset_url)
        flash("Password reset instructions have been sent to your email.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=("GET", "POST"))
def reset_password(token):
    try:
        email = get_serializer().loads(token, salt="password-reset", max_age=current_app.config["PASSWORD_RESET_EXPIRES"])
    except SignatureExpired:
        flash("The password reset link has expired.", "danger")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("Invalid password reset token.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Unable to locate the user account.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not password or password != confirm:
            flash("Passwords must match.", "danger")
            return render_template("reset_password.html")
        user.password = current_app.bcrypt.generate_password_hash(password).decode("utf-8") if hasattr(current_app, "bcrypt") else user.password
        from werkzeug.security import generate_password_hash

        user.password = generate_password_hash(password)
        from models import db

        db.session.commit()
        flash("Password updated successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")
