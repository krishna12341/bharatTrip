# BharatTrip Refund Management System

A Flask-based refund ticket management application for BharatTrip. It supports role-based access control for Admin, Support, and Finance users, tracks refund tickets in a shared workflow, stores audit logs, sends email notifications via SMTP, and includes AI integration points.

## Features

- Admin / Support / Finance roles
- Secure login and logout
- Refund ticket creation and tracking
- Shared single ticket workflow for Support and Finance
- Email notifications via SMTP when tickets are created
- Audit logs and email logs
- Configurable SMTP and application settings via environment variables
- SQLite storage with a repository-based structure
- Deployment-ready for PythonAnywhere

## Project Structure

- `app.py` — main Flask application
- `config.py` — application configuration using environment variables
- `models.py` — SQLAlchemy models for users, tickets, audit logs, email logs, and settings
- `repositories.py` — data access layer for users, tickets, audits, and email logs
- `helpers.py` — shared utilities like role-based access decorators
- `services/` — application services for email and AI
- `blueprints/` — Flask blueprints for auth, dashboard, tickets, admin, AI, and support
- `templates/` — Jinja2 templates for UI pages
- `static/` — static assets such as CSS and uploads
- `.env.example` — example environment variables for local setup

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Local Setup

1. Copy `.env.example` to `.env`.
2. Update `.env` with your SMTP and app configuration.
3. Run the app:

```bash
python app.py
```

4. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Sample Users

- `admin / admin123`
- `support / support123`
- `finance / finance123`

## Environment Variables

Use `.env` or platform environment variables to configure:

- `SECRET_KEY`
- `DATABASE_URL`
- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`
- `EMAIL_SENDER`
- `EMAIL_SENDER_NAME`
- `DEFAULT_CURRENCY`
- `SLA_DAYS`
- `DEFAULT_TIMEZONE`
- `OPENAI_API_KEY`
- `PASSWORD_RESET_EXPIRES`

## PythonAnywhere Deployment

1. Upload the project files to PythonAnywhere.
2. Create a virtual environment and install dependencies.
3. Configure the WSGI file to import the app:

```python
import sys

path = '/home/yourusername/bharattrip'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

4. Set the required environment variables in the PythonAnywhere Web tab.
5. Reload the web app.

## Notes

- Do not commit `.env` or `app.db` to source control.
- Add `.env` and `app.db` to `.gitignore`.
- For production, consider upgrading from SQLite to PostgreSQL or MySQL.

## Future Improvements

- Add CSV/Excel/PDF export reports
- Add admin-configurable email templates
- Add advanced ticket search and custom filters
- Add AI analytics and operational dashboards
- Add file attachment storage and secure uploads
- Add role management and admin settings
