from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Question, Answer, QuestionSet
from . import db
from flask_login import login_required, current_user

tests = Blueprint("tests", __name__)


@tests.route("/questions/<int:set_id>", methods=["GET", "POST"])
@login_required
def questions(set_id):
    # Get the question set
    question_set = QuestionSet.query.filter_by(
        id=set_id, 
        user_id=current_user.id
    ).first()
    
    if not question_set:
        flash("Question set not found.", category="error")
        return redirect(url_for("tests.question_sets"))
    
    if request.method == "POST":
        question_text = request.form.get("question")
        answer_text = request.form.get("answer")
        
        if not question_text:
            flash("Question cannot be empty.", category="error")
        elif not answer_text:
            flash("Answer cannot be empty.", category="error")
        else:
            new_question = Question(
                question=question_text, 
                user_id=current_user.id,
                question_set_id=set_id
            )
            db.session.add(new_question)
            db.session.flush()  # Get the question ID
            
            # Add the answer
            new_answer = Answer(answer=answer_text, question_id=new_question.id)
            db.session.add(new_answer)
            db.session.commit()
            
            flash("Question and answer added successfully!", category="success")
            return redirect(url_for("tests.questions", set_id=set_id))

    return render_template("questions.html", user=current_user, question_set=question_set)


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
        
        if not set_name:
            flash("Question set name is required.", "warning")
            return render_template("create_question_set.html")
        
        # Check if question set with same name already exists for this user
        existing_set = QuestionSet.query.filter_by(
            name=set_name,
            user_id=current_user.id
        ).first()
        
        if existing_set:
            flash(f"You already have a question set named '{set_name}'. Please choose a different name.", "warning")
            return render_template("create_question_set.html", set_name=set_name)
        
        new_set = QuestionSet(
            name=set_name,
            user_id=current_user.id
        )
        db.session.add(new_set)
        db.session.commit()
        flash(f"Question set '{set_name}' created successfully!", "success")
        return redirect(url_for("tests.question_sets"))
    
    return render_template("create_question_set.html")


@tests.route("/flashcards/<int:set_id>", methods=["GET"])
@login_required
def flashcards(set_id):
    # Get the question set
    question_set = QuestionSet.query.filter_by(
        id=set_id, 
        user_id=current_user.id
    ).first()
    
    if not question_set:
        flash("Question set not found.", category="error")
        return redirect(url_for("tests.question_sets"))
    
    if not question_set.questions:
        flash("This question set has no questions yet.", category="error")
        return redirect(url_for("tests.question_sets"))
    
    # Convert questions to dictionary format for JSON serialization
    questions_data = []
    for q in question_set.questions:
        questions_data.append({
            'question': q.question,
            'answer': q.answers[0].answer if q.answers else 'No answer'
        })
    
    return render_template("flashcards.html", user=current_user, question_set=question_set, questions_data=questions_data)