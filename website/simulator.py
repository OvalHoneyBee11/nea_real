from flask import Blueprint, render_template
from flask_login import login_required, current_user

sim = Blueprint("sim", __name__)


@sim.route("/simulator", methods=["GET", "POST"])
@login_required
def simulator():
    return render_template("simulator.html", user=current_user)


@sim.route("/portal/simulator")
@login_required
def simulator_portal():
    """Minimal preview for home page iframe"""
    return render_template("portals/simulator_portal.html")
