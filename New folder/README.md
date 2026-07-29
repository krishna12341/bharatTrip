# BharatTrip Refund Management

A Flask-based refund ticket management app with login, support/finance roles, ticket management, AI assistant, and SMTP email notifications.

## Local run

```bash
pip install -r requirements.txt
python app.py
```

## PythonAnywhere deployment

1. Upload the project files to PythonAnywhere.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
pip install gunicorn
```

4. In the PythonAnywhere Web tab, create a web app and set the WSGI file to:

```python
import sys

path = '/home/yourusername/bharattrip'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

5. Set environment variables for SMTP and app secrets.
6. Reload the web app.
