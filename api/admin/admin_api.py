from flask import Blueprint, render_template
from flask_login import current_user, login_required


admin_api_bp = Blueprint("admin_api", __name__)


# ------------------------------- FRONTEND ------------------------------- #

@admin_api_bp.route("/admin/promt")
@login_required
def admin_ai_promt():
    if not getattr(current_user, "is_admin", False):
        return render_template("403.html")

    return render_template("system-screens/sysem-promt.html")


@admin_api_bp.route("/admin/people/accunts")
@login_required
def admin_people_accounts():
    if not getattr(current_user, "is_admin", False):
        return render_template("403.html")

    return render_template("system-screens/user_admin.html")