import random
import string
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Class, ClassMembership, User, ChatMessage, Assignment
from . import db
from flask_login import login_required, current_user
from datetime import datetime


classes = Blueprint("classes", __name__)


@classes.route("/my_classes")
@login_required
def my_classes():
    """Display all classes where user is teacher or student"""
    # Classes where user is the teacher
    taught_classes = Class.query.filter_by(teacher_id=current_user.id).all()
    
    # Classes where user is a student
    memberships = ClassMembership.query.filter_by(user_id=current_user.id).all()
    enrolled_classes = [m.class_obj for m in memberships]
    
    return render_template(
        "my_classes.html",
        user=current_user,
        taught_classes=taught_classes,
        enrolled_classes=enrolled_classes
    )


@classes.route("/create_class", methods=["GET", "POST"])
@login_required
def create_class():
    # Only teachers can create classes
    if not current_user.is_teacher:
        flash("Only teachers can create classes.", "danger")
        return redirect(url_for("views.home"))
    
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        
        if not name:
            flash("Class name is required.", "warning")
        else:
            # Generate a unique 6-character class code
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            # Ensure code is unique
            while Class.query.filter_by(code=code).first():
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            new_class = Class(
                name=name,
                description=description,
                teacher_id=current_user.id,
                code=code
            )
            db.session.add(new_class)
            db.session.commit()
            flash(f"Class created successfully! Class code: {code}", "success")
            return redirect(url_for("classes.my_classes"))
    
    return render_template("create_class.html", user=current_user)


@classes.route("/join_class", methods=["GET", "POST"])
@login_required
def join_class():
    """Join a class using class code (student)"""
    if request.method == "POST":
        class_code = request.form.get("class_code").strip().upper()
        
        if not class_code:
            flash("Please enter a class code.", category="error")
        else:
            # Find the class
            class_obj = Class.query.filter_by(code=class_code).first()
            
            if not class_obj:
                flash("Invalid class code. Please check and try again.", category="error")
            elif class_obj.teacher_id == current_user.id:
                flash("You are the teacher of this class! You're already a member.", category="error")
            else:
                # Check if already in class
                existing = ClassMembership.query.filter_by(
                    user_id=current_user.id,
                    class_id=class_obj.id
                ).first()
                
                if existing:
                    flash("You are already enrolled in this class.", category="error")
                else:
                    # Join the class
                    membership = ClassMembership(
                        user_id=current_user.id,
                        class_id=class_obj.id
                    )
                    db.session.add(membership)
                    db.session.commit()
                    
                    flash(f"Successfully joined '{class_obj.name}'!", category="success")
                    return redirect(url_for("classes.class_detail", class_id=class_obj.id))
    
    return render_template("join_classes.html", user=current_user)


@classes.route("/class/<int:class_id>")
@login_required
def class_detail(class_id):
    """View class details and student list"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check if user has access to this class
    is_teacher = class_obj.teacher_id == current_user.id
    is_student = ClassMembership.query.filter_by(
        user_id=current_user.id,
        class_id=class_id
    ).first() is not None
    
    if not (is_teacher or is_student):
        flash("You don't have access to this class.", category="error")
        return redirect(url_for("classes.my_classes"))
    
    # Get all students in the class
    students = User.query.join(ClassMembership).filter(
        ClassMembership.class_id == class_id
    ).all()
    
    my_class = Class.query.get(class_id)
    return render_template(
        "class_detail.html",
        user=current_user,
        class_=my_class,       # changed: pass class_ not 'class'
        is_teacher=is_teacher,
        students=students
    )
@classes.route("/class/<int:class_id>/chat", methods=["GET", "POST"])
@login_required
def class_chat(class_id):
    """Class chat room for teachers and students"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check if user has access to this class
    is_teacher = class_obj.teacher_id == current_user.id
    is_student = ClassMembership.query.filter_by(
        user_id=current_user.id,
        class_id=class_id
    ).first() is not None
    
    if not (is_teacher or is_student):
        flash("You don't have access to this class.", category="error")
        return redirect(url_for("classes.my_classes"))
    
    # Handle new message submission
    if request.method == "POST":
        message_text = request.form.get("message")
        
        if not message_text or not message_text.strip():
            flash("Message cannot be empty.", category="error")
        else:
            new_message = ChatMessage(
                message=message_text.strip(),
                user_id=current_user.id,
                class_id=class_id
            )
            db.session.add(new_message)
            db.session.commit()
            flash("Message sent!", category="success")
            return redirect(url_for("classes.class_chat", class_id=class_id))
    
    # Get all messages for this class
    messages = ChatMessage.query.filter_by(class_id=class_id).order_by(ChatMessage.timestamp.asc()).all()
    
    return render_template(
        "class_chat.html",
        user=current_user,
        class_=class_obj,
        messages=messages,
        is_teacher=is_teacher
    )

@classes.route("/class/<int:class_id>/delete", methods=["POST"])
@login_required
def delete_class(class_id):
    """Delete a class (teacher only)"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Only the teacher who created the class can delete it
    if class_obj.teacher_id != current_user.id:
        flash("Only the class teacher can delete this class.", "danger")
        return redirect(url_for("classes.class_detail", class_id=class_id))
    
    # Delete all memberships first
    ClassMembership.query.filter_by(class_id=class_id).delete()
    
    # Delete all chat messages
    ChatMessage.query.filter_by(class_id=class_id).delete()
    
    # Delete all assignments
    Assignment.query.filter_by(class_id=class_id).delete()
    
    # Delete the class
    db.session.delete(class_obj)
    db.session.commit()
    
    flash(f"Class '{class_obj.name}' has been deleted.", "success")
    return redirect(url_for("classes.my_classes"))

@classes.route("/class/<int:class_id>/assignments")
@login_required
def view_assignments(class_id):
    """View all assignments for a class"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check access
    is_teacher = class_obj.teacher_id == current_user.id
    is_student = ClassMembership.query.filter_by(
        user_id=current_user.id,
        class_id=class_id
    ).first() is not None
    
    if not (is_teacher or is_student):
        flash("You don't have access to this class.", "error")
        return redirect(url_for("classes.my_classes"))
    
    assignments = Assignment.query.filter_by(class_id=class_id).order_by(Assignment.due_date).all()
    
    return render_template(
        "assignments.html",
        user=current_user,
        class_=class_obj,
        assignments=assignments,
        is_teacher=is_teacher
    )


@classes.route("/class/<int:class_id>/assignments/create", methods=["GET", "POST"])
@login_required
def create_assignment(class_id):
    """Create a new assignment (teacher only)"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Only teacher can create assignments
    if class_obj.teacher_id != current_user.id:
        flash("Only the teacher can create assignments.", "danger")
        return redirect(url_for("classes.view_assignments", class_id=class_id))
    
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        due_date_str = request.form.get("due_date")
        attachment_url = request.form.get("attachment_url")
        
        if not title:
            flash("Assignment title is required.", "warning")
        else:
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                except ValueError:
                    flash("Invalid date format. Use YYYY-MM-DD.", "warning")
                    return render_template("create_assignment.html", user=current_user, class_=class_obj)
            
            new_assignment = Assignment(
                title=title,
                description=description,
                due_date=due_date,
                class_id=class_id,
                creator_id=current_user.id,
                attachment_url=attachment_url
            )
            db.session.add(new_assignment)
            db.session.commit()
            flash("Assignment created successfully!", "success")
            return redirect(url_for("classes.view_assignments", class_id=class_id))
    
    return render_template("create_assignment.html", user=current_user, class_=class_obj)


@classes.route("/class/<int:class_id>/assignments/<int:assignment_id>/delete", methods=["POST"])
@login_required
def delete_assignment(class_id, assignment_id):
    """Delete an assignment (teacher only)"""
    assignment = Assignment.query.get_or_404(assignment_id)
    class_obj = Class.query.get_or_404(class_id)
    
    if class_obj.teacher_id != current_user.id:
        flash("Only the teacher can delete assignments.", "danger")
        return redirect(url_for("classes.view_assignments", class_id=class_id))
    
    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted.", "success")
    return redirect(url_for("classes.view_assignments", class_id=class_id))