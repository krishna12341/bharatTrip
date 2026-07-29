import smtplib
from email.message import EmailMessage
from flask import current_app, render_template
from models import Setting
from repositories import EmailRepository


class EmailService:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def get_setting(self, key, default=None):
        setting = Setting.query.filter_by(key=key).first()
        if setting and setting.value is not None:
            return setting.value
        return self.app.config.get(key, default)

    def get_bool(self, key, default=False):
        value = self.get_setting(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")

    def get_int(self, key, default=0):
        value = self.get_setting(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def send_message(self, recipient, subject, html_body, text_body):
        recipient = (recipient or "").strip()
        if not recipient:
            self.app.logger.error("Email delivery failed: recipient address is missing.")
            return False

        smtp_server = self.get_setting("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = self.get_int("SMTP_PORT", 587)
        smtp_username = self.get_setting("SMTP_USERNAME", "kaushikkrishnakumar424@gmail.com")
        smtp_password = self.get_setting("SMTP_PASSWORD", "hlfb jfyc jyye rwgo")
        smtp_use_ssl = self.get_bool("SMTP_USE_SSL", False)
        smtp_use_tls = self.get_bool("SMTP_USE_TLS", True)
        sender_email = self.get_setting("EMAIL_SENDER", smtp_username)
        sender_name = self.get_setting("EMAIL_SENDER_NAME", "KrishnaEmail")

        if not smtp_username or not smtp_password:
            self.app.logger.error("Email delivery failed: SMTP credentials are missing or incomplete.")
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = f"{sender_name} <{sender_email}>"
        message["To"] = recipient
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")

        try:
            if smtp_use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                if smtp_use_tls:
                    server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
            server.quit()
            return True
        except Exception as err:
            self.app.logger.error("Email delivery failed: %s", err)
            return False

    def send_ticket_notification(self, ticket, event, recipient):
        subject = f"[{ticket.ticket_number}] {event}"
        sender_name = self.get_setting("EMAIL_SENDER_NAME", "BharatTrip Support")
        html_body = render_template(
            "email/ticket_notification.html",
            ticket=ticket,
            event=event,
            support_contact=sender_name,
        )
        text_body = render_template(
            "email/ticket_notification.txt",
            ticket=ticket,
            event=event,
            support_contact=sender_name,
        )
        sent = self.send_message(recipient, subject, html_body, text_body)
        status = "Sent" if sent else "Failed"
        EmailRepository.log(ticket.id, recipient, subject, text_body, status)
        return sent

    def send_password_reset(self, recipient, reset_url):
        subject = "BharatTrip Password Reset"
        html_body = render_template(
            "email/password_reset.html",
            reset_url=reset_url,
            support_contact=self.app.config["EMAIL_SENDER_NAME"],
        )
        text_body = render_template(
            "email/password_reset.txt",
            reset_url=reset_url,
            support_contact=self.app.config["EMAIL_SENDER_NAME"],
        )
        return self.send_message(recipient, subject, html_body, text_body)
