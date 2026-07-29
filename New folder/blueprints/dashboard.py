from flask import Blueprint, render_template, request, current_app, jsonify
from flask_login import login_required, current_user

from helpers import role_required
from repositories import TicketRepository


dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")


@dashboard_bp.route("/")
@login_required
def index():
    counts = TicketRepository.get_metrics()
    status_counts = {
        status: len([ticket for ticket in TicketRepository.search() if ticket.status == status])
        for status in ["New", "Support Review", "Finance Review", "Approved", "Payment Initiated", "Refund Paid", "Closed", "Rejected"]
    }
    return render_template(
        "dashboard.html",
        user=current_user,
        counts=counts,
        status_counts=status_counts,
    )


@dashboard_bp.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    filters = {}
    if query:
        filters.update(
            {
                "ticket_number": query,
                "booking_id": query,
                "customer_name": query,
            }
        )
    tickets = TicketRepository.search(filters)
    return render_template("ticket_list.html", user=current_user, tickets=tickets, query=query)


@dashboard_bp.route("/api/metrics")
@login_required
def metrics_api():
    return jsonify(TicketRepository.get_metrics())
