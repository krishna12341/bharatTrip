from app import create_app
from models import db, RefundTicket

app = create_app()
from sqlalchemy import inspect

with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    print('db uri:', app.config['SQLALCHEMY_DATABASE_URI'])
    print('tables:', inspector.get_table_names())
    print('refund_tickets count:', db.session.query(RefundTicket).count())
