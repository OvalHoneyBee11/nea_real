from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Questions
from . import db
from flask_login import login_required, current_user

tests = Blueprint("tests", __name__)


@tests.route("/questions", methods=["GET", "POST"])
@login_required
def questions():
    if request.method == "POST":
        question_text = request.form.get("question")
        if question_text:
            new_question = Questions(question=question_text, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            flash("Question added successfully!", category="success")
        else:
            flash("Question cannot be empty!", category="error")
    questions = Questions.query.all()
    return render_template("questions.html", questions=questions, user=current_user)
