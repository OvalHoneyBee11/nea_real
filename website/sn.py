from flask import Blueprint, render_template
from flask_login import login_required, current_user

sn = Blueprint("sn", __name__)


@sn.route("/news", methods=["GET", "POST"])
@login_required
def news():
    return render_template("news.html", user=current_user)


@sn.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    return render_template("stats.html", user=current_user)
