from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Questions
from . import db
from flask_login import login_required, current_user

cls = Blueprint("cls", __name__)


@cls.route("/class_info", methods=["GET", "POST"])
@login_required
def class_info():
    return render_template("class.html", user=current_user)
