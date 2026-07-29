from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from helpers import role_required
from models import User, Setting
from repositories import AuditRepository, UserRepository

admin_bp = Blueprint("admin", __name__, template_folder="../templates")


@admin_bp.route("/admin")
@login_required
def index():
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("dashboard.index"))
    users = UserRepository.all_users()
    return render_template("admin_dashboard.html", user=current_user, users=users)


@admin_bp.route("/admin/users/new", methods=("GET", "POST"))
@login_required
@role_required("admin")
def add_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "support")
        if not username or not password or not email:
            flash("All fields are required.", "danger")
            return render_template("admin_user_form.html", user=current_user)
        if UserRepository.get_by_username(username):
            flash("Username already exists.", "danger")
            return render_template("admin_user_form.html", user=current_user)
        hashed_password = generate_password_hash(password)
        UserRepository.create_user(username, hashed_password, role, email)
        flash("User created successfully.", "success")
        return redirect(url_for("admin.index"))
    return render_template("admin_user_form.html", user=current_user)


@admin_bp.route("/admin/settings", methods=("GET", "POST"))
@login_required
@role_required("admin")
def settings():
    if request.method == "POST":
        for key in [
            "SMTP_SERVER",
            "SMTP_PORT",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "EMAIL_SENDER",
            "EMAIL_SENDER_NAME",
            "DEFAULT_CURRENCY",
            "SLA_DAYS",
            "DEFAULT_TIMEZONE",
        ]:
            value = request.form.get(key, "")
            Setting.set_value(key, value)
        flash("Settings saved successfully.", "success")
        return redirect(url_for("admin.settings"))

    settings = {setting.key: setting.value for setting in Setting.query.all()}
    return render_template("admin_settings.html", user=current_user, settings=settings)


@admin_bp.route("/admin/audit-logs")
@login_required
@role_required("admin")
def audit_logs():
    audits = AuditRepository.all_for_ticket(request.args.get("ticket_id")) if request.args.get("ticket_id") else []
    return render_template("admin_audit_logs.html", user=current_user, audits=audits)


@admin_bp.route("/admin/send-test-email", methods=("POST",))
@login_required
@role_required("admin")
def send_test_email():
    recipient = request.form.get("test_recipient") or Setting.get("EMAIL_SENDER") or current_app.config.get("EMAIL_SENDER")
    if not recipient:
        flash("Please provide a recipient email address.", "danger")
        return redirect(url_for("admin.settings"))

    subject = "BharatTrip Test Email"
    html_body = "<p>This is a test email from BharatTrip Refund Management.</p>"
    text_body = "This is a test email from BharatTrip Refund Management."

    sent = current_app.email_service.send_message(recipient, subject, html_body, text_body)
    if sent:
        flash(f"Test email sent to {recipient}", "success")
    else:
        flash("Test email failed to send. Check SMTP credentials and logs.", "danger")
    return redirect(url_for("admin.settings"))
