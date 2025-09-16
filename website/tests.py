from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Question, Answer, QuestionSet
from . import db
from flask_login import login_required, current_user

tests = Blueprint("tests", __name__)


@tests.route("/questions", methods=["GET", "POST"])
@login_required
def questions():
    if request.method == "POST":
        question_text = request.form.get("question")
        if not question_text:
            flash("Question cannot be empty.", category="error")
        else:
            new_question = Question(question=question_text, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            flash("Question created successfully!", category="success")
            return redirect(url_for("tests.questions"))

    questions = Question.query.filter_by(user_id=current_user.id).all()
    return render_template("questions.html", user=current_user, questions=questions)

@tests.route("/question_sets", methods=["GET", "POST"])
@login_required
def question_sets():
    if request.method == "POST":
        set_name = request.form.get("set_name")
        set_description = request.form.get("set_description")
        if not set_name:
            flash("Set name cannot be empty.", category="error")
        else:
            new_set = QuestionSet(name=set_name, description=set_description, user_id=current_user.id)
            db.session.add(new_set)
            db.session.commit()
            flash("Question set created successfully!", category="success")
            return redirect(url_for("tests.question_sets"))

    question_sets = QuestionSet.query.filter_by(user_id=current_user.id).all()
    return render_template("question_sets.html", user=current_user, question_sets=question_sets)

@tests.route("/create_question_set", methods=["GET"])
@login_required
def create_question_set():
    # You can add logic to create a new set here if needed
    return redirect(url_for('tests.questions'))