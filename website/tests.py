from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Question, Answer
from . import db
from flask_login import login_required, current_user

tests = Blueprint("tests", __name__)


def insert_question_and_answer(question_text, answer_text, user_id):
    new_question = Question(
        question=question_text.strip(),
        user_id=user_id,
    )
    db.session.add(new_question)
    db.session.commit()

    if answer_text and len(answer_text.strip()) > 0:
        new_answer = Answer(answer=answer_text.strip(), question_id=new_question.id)
        db.session.add(new_answer)
        db.session.commit()


@tests.route("/questions", methods=["GET", "POST"])
@login_required
def questions():
    if request.method == "POST":
        question_text = request.form.get("question")
        answer_text = request.form.get("answer")
        if not question_text or len(question_text.strip()) < 1:
            flash("Question is too short!", category="error")
        else:
            new_question = Question(
                question=question_text.strip(),
                user_id=current_user.id,
            )
            db.session.add(new_question)

            db.session.commit()

            if answer_text and len(answer_text.strip()) > 0:
                new_answer = Answer(
                    answer=answer_text.strip(), question_id=new_question.id
                )
                db.session.add(new_answer)

            db.session.commit()
            flash("Question added!", category="success")
            return redirect(url_for("tests.questions"))
    return render_template("questions.html", user=current_user)
