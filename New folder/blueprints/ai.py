from flask import Blueprint, render_template, request, current_app
from flask_login import login_required

ai_bp = Blueprint("ai", __name__, template_folder="../templates")


@ai_bp.route("/ai-chat", methods=("GET", "POST"))
@login_required
def chat():
    answer = None
    prompt = None
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            response = current_app.ai_service.query(prompt)
            answer = response.get("answer") if isinstance(response, dict) else None
    return render_template("ai_chat.html", prompt=prompt, answer=answer)
