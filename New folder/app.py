import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from config import BaseConfig
from models import db, User
from services.email_service import EmailService
from services.ai_service import AIService


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(BaseConfig)

    load_dotenv(os.path.join(app.root_path, ".env"))
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    app.email_service = EmailService(app)
    app.ai_service = AIService(app.config.get("OPENAI_API_KEY", ""))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.tickets import tickets_bp
    from blueprints.admin import admin_bp
    from blueprints.ai import ai_bp
    from blueprints.support import support_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(support_bp)

    with app.app_context():
        db.create_all()
        seed_default_users()

    return app


def seed_default_users():
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin",
            email="admin@bharattrip.com",
        )
        support = User(
            username="support",
            password=generate_password_hash("support123"),
            role="support",
            email="support@bharattrip.com",
        )
        finance = User(
            username="finance",
            password=generate_password_hash("finance123"),
            role="finance",
            email="finance@bharattrip.com",
        )
        db.session.add_all([admin, support, finance])
        db.session.commit()


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
