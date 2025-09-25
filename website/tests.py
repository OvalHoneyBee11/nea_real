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
        answer_text = request.form.get("answer")
        question_set_id = request.form.get("question_set_id")
        
        if not question_text:
            flash("Question cannot be empty.", category="error")
        elif not answer_text:
            flash("Answer cannot be empty.", category="error")
        else:
            new_question = Question(
                question=question_text, 
                user_id=current_user.id,
                question_set_id=question_set_id if question_set_id else None
            )
            db.session.add(new_question)
            db.session.flush()  # Get the question ID
            
            # Add the answer
            new_answer = Answer(answer=answer_text, question_id=new_question.id)
            db.session.add(new_answer)
            db.session.commit()
            
            flash("Question and answer created successfully!", category="success")
            return redirect(url_for("tests.questions"))

    questions = Question.query.filter_by(user_id=current_user.id).all()
    question_sets = QuestionSet.query.filter_by(user_id=current_user.id).all()
    return render_template("questions.html", user=current_user, questions=questions, question_sets=question_sets)


@tests.route("/question_sets", methods=["GET"])
@login_required
def question_sets():
    selected_set_id = request.args.get("selected_set")
    selected_set = None
    
    if selected_set_id:
        selected_set = QuestionSet.query.filter_by(
            id=selected_set_id, 
            user_id=current_user.id
        ).first()

    question_sets = QuestionSet.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "question_sets.html", 
        user=current_user, 
        question_sets=question_sets,
        selected_set=selected_set
    )


@tests.route("/create_question_set", methods=["GET", "POST"])
@login_required
def create_question_set():
    if request.method == "POST":
        set_name = request.form.get("set_name")
        set_description = request.form.get("set_description")
        
        if not set_name:
            flash("Set name cannot be empty.", category="error")
        else:
            # Check if set name already exists for this user
            existing_set = QuestionSet.query.filter_by(
                name=set_name, 
                user_id=current_user.id
            ).first()
            
            if existing_set:
                flash("A question set with this name already exists.", category="error")
            else:
                new_set = QuestionSet(
                    name=set_name, 
                    description=set_description, 
                    user_id=current_user.id
                )
                db.session.add(new_set)
                db.session.commit()
                flash("Question set created successfully!", category="success")
                return redirect(url_for("tests.question_sets"))

    return render_template("create_question_set.html", user=current_user)