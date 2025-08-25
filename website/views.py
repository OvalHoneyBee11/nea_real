from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .sn import get_uk_economic_stats

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    user = current_user.username if current_user.is_authenticated else None
    return render_template("home.html", user=user)


@views.route("/economic-stats")
def economic_stats():
    stats = get_uk_economic_stats()
    return render_template("economic_stats.html", stats=stats)
