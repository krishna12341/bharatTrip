import sqlite3
import os

path = os.path.join(os.getcwd(), 'app.db')
print('db path:', path)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print('tables:', cur.fetchall())
for table in ['refund_tickets', 'tickets', 'users', 'email_logs', 'audit_logs', 'settings']:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(table, cur.fetchone()[0])
    except Exception as e:
        print(table, 'error', e)
conn.close()
