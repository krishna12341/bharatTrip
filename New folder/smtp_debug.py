from app import app
from models import Setting
import smtplib


def get_setting(key, default=None):
    s = Setting.query.filter_by(key=key).first()
    if s and s.value is not None:
        return s.value
    return app.config.get(key, default)


def get_bool(key, default=False):
    v = get_setting(key, default)
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def get_int(key, default=0):
    v = get_setting(key, default)
    try:
        return int(v)
    except Exception:
        return default


with app.app_context():
    server = get_setting("SMTP_SERVER", "smtp.gmail.com")
    port = get_int("SMTP_PORT", 587)
    username = get_setting("SMTP_USERNAME", "")
    password = get_setting("SMTP_PASSWORD", "")
    use_ssl = get_bool("SMTP_USE_SSL", False)
    use_tls = get_bool("SMTP_USE_TLS", True)

    print("Using SMTP settings:")
    print("  server:", server)
    print("  port:", port)
    print("  username:", username)
    print("  use_ssl:", use_ssl)
    print("  use_tls:", use_tls)
    print("  password set:", bool(password))

    try:
        if use_ssl:
            smtp = smtplib.SMTP_SSL(server, port, timeout=10)
        else:
            smtp = smtplib.SMTP(server, port, timeout=10)
            if use_tls:
                smtp.starttls()
        print("Connecting to SMTP server...")
        smtp.login(username, password)
        print("Login succeeded")
        smtp.quit()
    except Exception as e:
        print("Login failed:", repr(e))
        # If the exception has .smtp_code and .smtp_error, print them
        try:
            code = getattr(e, 'smtp_code', None)
            err = getattr(e, 'smtp_error', None)
            if code or err:
                print('smtp_code:', code)
                print('smtp_error:', err)
        except Exception:
            pass
