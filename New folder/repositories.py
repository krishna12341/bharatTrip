from datetime import datetime
from typing import List, Optional

from models import AuditLog, EmailLog, RefundTicket, Setting, User, db


class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create_user(username: str, password: str, role: str, email: str) -> User:
        user = User(username=username, password=password, role=role, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def all_users() -> List[User]:
        return User.query.order_by(User.username).all()


class TicketRepository:
    @staticmethod
    def get_by_id(ticket_id: int) -> Optional[RefundTicket]:
        return RefundTicket.query.get(ticket_id)

    @staticmethod
    def create_ticket(**kwargs) -> RefundTicket:
        ticket = RefundTicket(**kwargs)
        db.session.add(ticket)
        db.session.commit()
        return ticket

    @staticmethod
    def update_ticket(ticket: RefundTicket, **kwargs) -> RefundTicket:
        for key, value in kwargs.items():
            setattr(ticket, key, value)
        ticket.updated_at = datetime.utcnow()
        db.session.commit()
        return ticket

    @staticmethod
    def search(filters: dict = None):
        query = RefundTicket.query
        if not filters:
            return query.order_by(RefundTicket.updated_at.desc()).all()
        if filters.get("status"):
            query = query.filter_by(status=filters["status"])
        if filters.get("priority"):
            query = query.filter_by(priority=filters["priority"])
        if filters.get("ticket_number"):
            query = query.filter(RefundTicket.ticket_number.ilike(f"%{filters['ticket_number']}%"))
        if filters.get("booking_id"):
            query = query.filter(RefundTicket.booking_id.ilike(f"%{filters['booking_id']}%"))
        if filters.get("customer_name"):
            query = query.filter(RefundTicket.customer_name.ilike(f"%{filters['customer_name']}%"))
        if filters.get("assigned_user_id"):
            query = query.filter_by(assigned_user_id=filters["assigned_user_id"])
        return query.order_by(RefundTicket.updated_at.desc()).all()

    @staticmethod
    def get_metrics():
        total = RefundTicket.query.count()
        pending = RefundTicket.query.filter(RefundTicket.status.in_(["New", "Support Review", "Finance Review"])) .count()
        approved = RefundTicket.query.filter_by(status="Approved").count()
        rejected = RefundTicket.query.filter_by(status="Rejected").count()
        paid = RefundTicket.query.filter_by(status="Refund Paid").count()
        escalated = RefundTicket.query.filter_by(is_escalated=True).count()
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "paid": paid,
            "escalated": escalated,
        }


class AuditRepository:
    @staticmethod
    def log(ticket_id: int, user_id: int, action: str, old_value: str = None, new_value: str = None, comment: str = None):
        audit = AuditLog(
            ticket_id=ticket_id,
            user_id=user_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            comment=comment,
        )
        db.session.add(audit)
        db.session.commit()
        return audit

    @staticmethod
    def all_for_ticket(ticket_id: int):
        return AuditLog.query.filter_by(ticket_id=ticket_id).order_by(AuditLog.created_at.asc()).all()


class EmailRepository:
    @staticmethod
    def log(ticket_id: int, recipient: str, subject: str, body: str, status: str):
        email_log = EmailLog(
            ticket_id=ticket_id,
            recipient=recipient,
            subject=subject,
            body=body,
            status=status,
        )
        db.session.add(email_log)
        db.session.commit()
        return email_log


class SettingRepository:
    @staticmethod
    def get(key: str, default=None):
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set_value(key: str, value: str):
        Setting.set_value(key, value)
