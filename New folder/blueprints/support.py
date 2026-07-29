from flask import Blueprint, render_template
from flask_login import login_required

support_bp = Blueprint("support", __name__, template_folder="../templates")


@support_bp.route("/support")
@login_required
def index():
    return render_template("support.html")
