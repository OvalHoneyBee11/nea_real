from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Class, ClassMembership, QuestionSet
from .sn import get_stats

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    if current_user.is_teacher:
        # Teachers see classes they teach
        user_classes = Class.query.filter_by(teacher_id=current_user.id).all()
    else:
        # Students see classes they're enrolled in
        user_classes = Class.query.join(ClassMembership).filter(
            ClassMembership.user_id == current_user.id
        ).all()
    
    # Get user's question sets
    user_question_sets = QuestionSet.query.filter_by(user_id=current_user.id).all()
    
    return render_template("home.html", user=current_user, user_classes=user_classes, user_question_sets=user_question_sets)
   
@views.route("/economic-stats")
def economic_stats():
    stats = get_stats()
    return render_template("economic_stats.html", stats=stats)

@views.route('/test-kg')
def test_kg():
    return render_template('test_kg.html')