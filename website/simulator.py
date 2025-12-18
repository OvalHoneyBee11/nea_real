from flask import Blueprint, render_template
from flask_login import login_required, current_user

sim = Blueprint("sim", __name__)


@sim.route("/graphing_tool", methods=["GET", "POST"])
@login_required
def graphing_tool():
    return render_template("simulator.html", user=current_user)
