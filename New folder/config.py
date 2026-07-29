import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=False)
load_dotenv(BASE_DIR / ".env.example", override=False)

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-for-production")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", SMTP_USERNAME)
    EMAIL_SENDER_NAME = os.getenv("EMAIL_SENDER_NAME", "BharatTrip Support")

    DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "INR")
    SLA_DAYS = int(os.getenv("SLA_DAYS", "3"))
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PASSWORD_RESET_EXPIRES = int(os.getenv("PASSWORD_RESET_EXPIRES", "3600"))
