from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Class, ClassMembership, User
from . import db
from flask_login import login_required, current_user

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
    """Create a new class (teacher)"""
    if request.method == "POST":
        class_name = request.form.get("class_name")
        description = request.form.get("description")
        
        if not class_name:
            flash("Class name cannot be empty.", category="error")
        else:
            # Create the class
            new_class = Class(
                name=class_name,
                description=description,
                code=Class.generate_code(),
                teacher_id=current_user.id
            )
            db.session.add(new_class)
            db.session.commit()
            
            flash(f"Class '{class_name}' created successfully! Class code: {new_class.code}", category="success")
            return redirect(url_for("classes.class_detail", class_id=new_class.id))
    
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
    
    return render_template(
        "class_detail.html",
        user=current_user,
        class_obj=class_obj,
        is_teacher=is_teacher,
        students=students
    )