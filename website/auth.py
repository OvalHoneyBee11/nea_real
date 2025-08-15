from flask import Blueprint, render_template, request, flash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    return render_template(
        "login.html",
    )


@auth.route("/logout")
def logout():
    return "<p>Logout Page</p>"


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if password1 != password2:
            flash("Passwords do not match!", category="error")
        if len(username) < 3:
            flash("Username must be at least 3 characters long!", category="error")
        if len(password1) < 6:
            flash("Password must be at least 6 characters long!", category="error")
        else:
            flash("Account created successfully!", category="success")

    return render_template("sign_up.html")
