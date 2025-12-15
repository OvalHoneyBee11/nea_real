from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint("auth", __name__)


# Login route
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash("Login successful!", category="success")
            login_user(user, remember=True)
            return redirect(url_for("views.home"))
        else:
            flash("Login failed. Check your username and password.", category="error")
    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# Sign-up route
@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        role = request.form.get("role", "student")

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists!", category="error")
            return render_template("sign_up.html")
        # Validation checks
        if password1 != password2:
            flash("Passwords do not match!", category="error")
        if len(username) < 3:
            flash("Username must be at least 4 characters long!", category="error")
        if len(password1) < 7:
            flash("Password must be at least 8 characters long!", category="error")
        if len(username) >= 4 and len(password1) >= 8 and password1 == password2:
            new_user = User(
                username=username,
                password=generate_password_hash(password1, method="pbkdf2:sha256"),
                role=role,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully!", category="success")
            return redirect(url_for("auth.login"))

    return render_template("sign_up.html", user=current_user)
