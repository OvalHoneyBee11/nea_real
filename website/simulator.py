from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Questions
from . import db
from flask_login import login_required, current_user

sim = Blueprint("sim", __name__)


@sim.route("/simulator", methods=["GET", "POST"])
@login_required
def simulator():
    return render_template("simulator.html", user=current_user)
