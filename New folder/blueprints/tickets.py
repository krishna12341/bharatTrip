import json
import os
from datetime import datetime, date
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_file,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from io import BytesIO
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from helpers import role_required
from models import RefundTicket, User
from repositories import AuditRepository, EmailRepository, TicketRepository, UserRepository

TICKET_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")

if not os.path.isdir(TICKET_UPLOAD_FOLDER):
    os.makedirs(TICKET_UPLOAD_FOLDER, exist_ok=True)


tickets_bp = Blueprint("tickets", __name__, template_folder="../templates")


def parse_date_value(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@tickets_bp.route("/tickets")
@login_required
def list_tickets():
    filters = {
        "status": request.args.get("status"),
        "priority": request.args.get("priority"),
        "ticket_number": request.args.get("ticket_number"),
        "booking_id": request.args.get("booking_id"),
        "customer_name": request.args.get("customer_name"),
    }
    tickets = TicketRepository.search(filters)
    return render_template("ticket_list.html", user=current_user, tickets=tickets, filters=filters)


@tickets_bp.route("/tickets/new", methods=("GET", "POST"))
@login_required
@role_required("support", "admin")
def create_ticket():
    if request.method == "POST":
        fields = {
            "customer_name": request.form.get("customer_name", "").strip(),
            "agent_name": request.form.get("agent_name", "").strip(),
            "customer_email": request.form.get("customer_email", "").strip(),
            "customer_phone": request.form.get("customer_phone", "").strip(),
            "booking_id": request.form.get("booking_id", "").strip(),
            "booking_date": parse_date_value(request.form.get("booking_date")),
            "cancellation_date": parse_date_value(request.form.get("cancellation_date")),
            "refund_amount": float(request.form.get("refund_amount", 0) or 0),
            "approved_amount": float(request.form.get("approved_amount", 0) or 0),
            "currency": request.form.get("currency", current_app.config.get("DEFAULT_CURRENCY", "INR")),
            "priority": request.form.get("priority", "Medium"),
            "reason": request.form.get("reason", "").strip(),
            "status": "New",
            "assigned_user_id": request.form.get("assigned_user_id") or None,
            "support_notes": request.form.get("support_notes", "").strip(),
            "finance_notes": request.form.get("finance_notes", "").strip(),
            "created_by_id": current_user.id,
        }
        ticket = TicketRepository.create_ticket(**fields)
        attachments = request.files.getlist("attachments")
        for attachment in attachments:
            if attachment and attachment.filename:
                filename = secure_filename(attachment.filename)
                path = os.path.join(TICKET_UPLOAD_FOLDER, filename)
                attachment.save(path)
                ticket.add_attachment(filename)
        TicketRepository.update_ticket(ticket)
        AuditRepository.log(ticket.id, current_user.id, "Created refund ticket", None, ticket.status, request.form.get("support_notes"))
        email_sent = current_app.email_service.send_ticket_notification(ticket, "Ticket Created", ticket.customer_email)
        flash("Refund ticket created successfully.", "success")
        if not email_sent:
            flash("Email notification could not be delivered. Check SMTP settings.", "warning")
        return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))

    users = UserRepository.all_users()
    return render_template("ticket_form.html", user=current_user, users=users, priorities=["Low", "Medium", "High", "Critical"], statuses=RefundTicket.__table__.columns[0:0])


@tickets_bp.route("/tickets/<int:ticket_id>")
@login_required
def view_ticket(ticket_id):
    ticket = TicketRepository.get_by_id(ticket_id)
    if not ticket:
        flash("Ticket not found.", "danger")
        return redirect(url_for("tickets.list_tickets"))

    if current_user.role == "support" or current_user.role == "finance" or current_user.role == "admin" or ticket.created_by_id == current_user.id:
        audit_logs = AuditRepository.all_for_ticket(ticket.id)
        return render_template("ticket_detail.html", user=current_user, ticket=ticket, audit_logs=audit_logs)

    flash("Access denied.", "danger")
    return redirect(url_for("tickets.list_tickets"))


@tickets_bp.route("/tickets/<int:ticket_id>/update", methods=("POST",))
@login_required
def update_ticket(ticket_id):
    ticket = TicketRepository.get_by_id(ticket_id)
    if not ticket:
        flash("Ticket not found.", "danger")
        return redirect(url_for("tickets.list_tickets"))

    if current_user.role == "finance":
        old_status = ticket.status
        ticket.status = request.form.get("status", ticket.status)
        ticket.approved_amount = float(request.form.get("approved_amount", ticket.approved_amount or 0) or ticket.approved_amount or 0)
        ticket.payment_reference = request.form.get("payment_reference", ticket.payment_reference)
        ticket.payment_date = parse_date_value(request.form.get("payment_date")) or ticket.payment_date
        ticket.finance_notes = request.form.get("finance_notes", ticket.finance_notes)
        TicketRepository.update_ticket(ticket)
        AuditRepository.log(ticket.id, current_user.id, "Finance updated ticket", old_status, ticket.status, ticket.finance_notes)
        current_app.email_service.send_ticket_notification(ticket, f"Ticket {ticket.status}", ticket.customer_email)
        flash("Ticket updated successfully.", "success")
        return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))

    if current_user.role == "support":
        old_status = ticket.status
        ticket.customer_name = request.form.get("customer_name", ticket.customer_name)
        ticket.agent_name = request.form.get("agent_name", ticket.agent_name)
        ticket.customer_email = request.form.get("customer_email", ticket.customer_email)
        ticket.customer_phone = request.form.get("customer_phone", ticket.customer_phone)
        ticket.booking_id = request.form.get("booking_id", ticket.booking_id)
        ticket.booking_date = parse_date_value(request.form.get("booking_date")) or ticket.booking_date
        ticket.cancellation_date = parse_date_value(request.form.get("cancellation_date")) or ticket.cancellation_date
        ticket.refund_amount = float(request.form.get("refund_amount", ticket.refund_amount) or ticket.refund_amount)
        ticket.priority = request.form.get("priority", ticket.priority)
        ticket.reason = request.form.get("reason", ticket.reason)
        ticket.support_notes = request.form.get("support_notes", ticket.support_notes)
        TicketRepository.update_ticket(ticket)
        AuditRepository.log(ticket.id, current_user.id, "Support updated ticket", old_status, ticket.status, ticket.support_notes)
        flash("Ticket saved successfully.", "success")
        return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))

    flash("You do not have permission to update this ticket.", "danger")
    return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))


@tickets_bp.route("/tickets/export/csv")
@login_required
def export_csv():
    tickets = TicketRepository.search(request.args)
    output = [
        ",".join(
            [
                "Ticket Number",
                "Customer Name",
                "Booking ID",
                "Status",
                "Priority",
                "Refund Amount",
                "Approved Amount",
                "Payment Reference",
                "Created At",
            ]
        )
    ]
    for ticket in tickets:
        output.append(
            ",".join(
                [
                    ticket.ticket_number,
                    ticket.customer_name,
                    ticket.booking_id,
                    ticket.status,
                    ticket.priority,
                    str(ticket.refund_amount),
                    str(ticket.approved_amount or ""),
                    ticket.payment_reference or "",
                    ticket.created_at.isoformat(),
                ]
            )
        )
    return current_app.response_class("\n".join(output), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=refund_report.csv"})


@tickets_bp.route("/tickets/export/excel")
@login_required
def export_excel():
    tickets = TicketRepository.search(request.args)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append([
        "Ticket Number",
        "Customer Name",
        "Booking ID",
        "Status",
        "Priority",
        "Refund Amount",
        "Approved Amount",
        "Payment Reference",
        "Created At",
    ])
    for ticket in tickets:
        sheet.append(
            [
                ticket.ticket_number,
                ticket.customer_name,
                ticket.booking_id,
                ticket.status,
                ticket.priority,
                ticket.refund_amount,
                ticket.approved_amount or "",
                ticket.payment_reference or "",
                ticket.created_at.isoformat(),
            ]
        )
    stream = BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return send_file(stream, download_name="refund_report.xlsx", as_attachment=True)


@tickets_bp.route("/tickets/export/pdf")
@login_required
def export_pdf():
    tickets = TicketRepository.search(request.args)
    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(30, 750, "Refund Ticket Report")
    pdf.setFont("Helvetica", 10)
    y = 720
    headers = ["Ticket", "Customer", "Booking", "Status", "Amount"]
    pdf.drawString(30, y, " | ".join(headers))
    y -= 20
    for ticket in tickets:
        pdf.drawString(
            30,
            y,
            f"{ticket.ticket_number} | {ticket.customer_name} | {ticket.booking_id} | {ticket.status} | {ticket.refund_amount}",
        )
        y -= 16
        if y < 80:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = 750
    pdf.save()
    stream.seek(0)
    return send_file(stream, download_name="refund_report.pdf", as_attachment=True, mimetype="application/pdf")
