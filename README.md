# 🚀 BharatTrip Refund Management System

A modern **Refund Management System** built with **Flask** that allows Support and Finance teams to manage refund requests from a single platform.

## ✨ Features

- 🔐 User Authentication (Login & Logout)
- 👥 Role-Based Access Control (Admin, Support, Finance)
- 🎫 Refund Ticket Management
- 📊 Dashboard with Refund Statistics
- 📧 SMTP Email Notifications
- 🤖 AI Assistant (OpenAI Integration)
- 📁 CSV-Based Data Storage
- 📝 Activity Logs
- 📎 File Upload Support
- 🔍 Search & Filters
- 📈 Reports & Analytics

---

# 📁 Project Structure

```
bharattrip-refund-management/
│
├── app.py
├── requirements.txt
├── config.py
├── .env.example
│
├── data/
│   ├── tickets.csv
│   ├── users.csv
│   ├── activity_logs.csv
│   ├── email_logs.csv
│   └── settings.csv
│
├── templates/
├── static/
├── uploads/
└── README.md
```

---

# 📋 Prerequisites

Before running the project, install:

- Python 3.10 or later
- pip
- Git

Verify installation:

```bash
python --version
pip --version
git --version
```

---

# ⬇️ Clone the Repository

```bash
git clone https://github.com/your-username/bharattrip-refund-management.git

cd bharattrip-refund-management
```

---

# 🐍 Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

---

# 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ⚙️ Environment Variables

Create a file named

```
.env
```

Copy the contents from

```
.env.example
```

Example

```env
SECRET_KEY=your-secret-key

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

OPENAI_API_KEY=your-openai-api-key
```

---

# 📂 Data Files

The application stores data in CSV files inside the **data/** directory.

Required files:

```
data/
├── tickets.csv
├── users.csv
├── activity_logs.csv
├── email_logs.csv
└── settings.csv
```

If these files don't exist, create empty CSV files with the required headers.

---

# 👤 Default Admin User

Create the first admin user by adding it to

```
data/users.csv
```

Example

```csv
id,name,email,password,role
1,Admin,admin@example.com,admin123,admin
```

> **Note:** Change the default password after the first login.

---

# ▶️ Run the Application

```bash
python app.py
```

or

```bash
flask run
```

---

# 🌐 Open in Browser

Visit

```
http://127.0.0.1:5000
```

or

```
http://localhost:5000
```

---

# 📧 SMTP Email Configuration

This project uses **Nodemailer-compatible SMTP settings** via Flask.

Example Gmail configuration:

```
SMTP Host:
smtp.gmail.com

Port:
587

Username:
your-email@gmail.com

Password:
Google App Password
```

---

# 🤖 OpenAI Integration

Add your OpenAI API Key inside

```
.env
```

```env
OPENAI_API_KEY=xxxxxxxxxxxxxxxx
```

The AI Assistant can:

- Summarize refund activity
- Detect pending refunds
- Explain escalation trends
- Generate operational insights

---

# 📊 Available Roles

### Admin

- Manage Users
- Configure SMTP
- View Reports
- Manage Settings

### Support

- Create Tickets
- Update Customer Details
- Upload Documents
- Send Customer Updates

### Finance

- Approve Refunds
- Reject Refunds
- Update Payment Status
- Add Payment Reference

---

# 📁 CSV Storage

This application uses CSV files as the local database.

Advantages

- No database installation required
- Easy to inspect and modify
- Ideal for demos and small teams

The architecture is designed so CSV storage can later be replaced with PostgreSQL or MySQL with minimal code changes.

---

# 🚀 Deploy on PythonAnywhere

1. Upload the project to PythonAnywhere.
2. Create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
pip install gunicorn
```

4. Configure the WSGI file:

```python
import sys

path = '/home/yourusername/bharattrip-refund-management'

if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

5. Add environment variables.
6. Reload the application.

---

# 🛠 Troubleshooting

### ModuleNotFoundError

```bash
pip install -r requirements.txt
```

---

### SMTP Authentication Failed

- Verify SMTP credentials.
- Use a Gmail App Password instead of your account password.
- Confirm SMTP settings in `.env`.

---

### Port Already in Use

Run on another port:

```bash
python app.py --port 8000
```

---

# 📄 License

This project is intended for educational and demonstration purposes.

---

# 👨‍💻 Author

Developed as part of the **BharatTrip AI Operations Associate Take-Home Assignment**.

```

This README is suitable for a public GitHub repository and gives anyone enough information to clone the project, configure it, and run it locally with minimal setup.
