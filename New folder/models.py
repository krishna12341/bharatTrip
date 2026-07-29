import json
import uuid
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from config import BaseConfig

db = SQLAlchemy()

STATUS_CHOICES = [
    "New",
    "Support Review",
    "Finance Review",
    "Approved",
    "Payment Initiated",
    "Refund Paid",
    "Closed",
    "Rejected",
]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
ROLES = ["admin", "support", "finance"]


def generate_ticket_number():
    return f"RT-{uuid.uuid4().hex[:8].upper()}"


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_tickets = db.relationship("RefundTicket", back_populates="created_by", foreign_keys="RefundTicket.created_by_id")
    assigned_tickets = db.relationship("RefundTicket", back_populates="assigned_user", foreign_keys="RefundTicket.assigned_user_id")


class RefundTicket(db.Model):
    __tablename__ = "refund_tickets"

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(32), unique=True, nullable=False, default=generate_ticket_number)
    customer_name = db.Column(db.String(150), nullable=False)
    agent_name = db.Column(db.String(150), nullable=True)
    customer_email = db.Column(db.String(150), nullable=False)
    customer_phone = db.Column(db.String(50), nullable=True)
    booking_id = db.Column(db.String(100), nullable=False)
    booking_date = db.Column(db.Date, nullable=True)
    cancellation_date = db.Column(db.Date, nullable=True)
    refund_amount = db.Column(db.Float, nullable=False)
    approved_amount = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default=BaseConfig.DEFAULT_CURRENCY)
    priority = db.Column(db.String(20), default="Medium")
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="New")
    assigned_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    payment_reference = db.Column(db.String(120), nullable=True)
    payment_date = db.Column(db.Date, nullable=True)
    support_notes = db.Column(db.Text, nullable=True)
    finance_notes = db.Column(db.Text, nullable=True)
    attachments = db.Column(db.Text, default="[]")
    is_escalated = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = db.relationship("User", back_populates="created_tickets", foreign_keys=[created_by_id])
    assigned_user = db.relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_user_id])
    audit_logs = db.relationship("AuditLog", back_populates="ticket", order_by="AuditLog.created_at.desc()")
    email_logs = db.relationship("EmailLog", back_populates="ticket", order_by="EmailLog.sent_at.desc()")

    def add_attachment(self, filename):
        attachments = json.loads(self.attachments or "[]")
        attachments.append(filename)
        self.attachments = json.dumps(attachments)

    def get_attachments(self):
        return json.loads(self.attachments or "[]")

    def to_dict(self):
        return {
            "ticket_number": self.ticket_number,
            "customer_name": self.customer_name,
            "agent_name": self.agent_name,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "booking_id": self.booking_id,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "cancellation_date": self.cancellation_date.isoformat() if self.cancellation_date else None,
            "refund_amount": self.refund_amount,
            "approved_amount": self.approved_amount,
            "currency": self.currency,
            "priority": self.priority,
            "reason": self.reason,
            "status": self.status,
            "payment_reference": self.payment_reference,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "support_notes": self.support_notes,
            "finance_notes": self.finance_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("refund_tickets.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(150), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship("RefundTicket", back_populates="audit_logs")
    user = db.relationship("User")


class EmailLog(db.Model):
    __tablename__ = "email_logs"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("refund_tickets.id"), nullable=True)
    recipient = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship("RefundTicket", back_populates="email_logs")


class Setting(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    @staticmethod
    def get(key, default=None):
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set_value(key, value):
        setting = Setting.query.filter_by(key=key).first()
        if not setting:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
        else:
            setting.value = value
        db.session.commit()
