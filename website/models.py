from website import db
from flask_login import UserMixin
import string
import random

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1500))
    date = db.Column(db.DateTime(timezone=True), default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    tasks = db.relationship("Task", backref="user", lazy=True)
    questions = db.relationship("Question", backref="user", lazy=True)
    question_sets = db.relationship("QuestionSet", backref="user", lazy=True)   
    taught_classes = db.relationship("Class", backref="teacher", lazy=True, foreign_keys="Class.teacher_id")
    class_memberships = db.relationship("ClassMembership", backref="user", lazy=True)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(500))
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
    memberships = db.relationship("ClassMembership", backref="class_obj", lazy=True, cascade="all, delete-orphan")
    
    @staticmethod
    def generate_code():
        """Generate a unique 8-character class code"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=8))
            if not Class.query.filter_by(code=code).first():
                return code

class ClassMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"))
    joined_at = db.Column(db.DateTime(timezone=True), default=db.func.now())

class QuestionSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    questions = db.relationship("Question", backref="question_set", lazy=True)
    
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    question_set_id = db.Column(db.Integer, db.ForeignKey("question_set.id"))
    answers = db.relationship("Answer", backref="question", lazy=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(500), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))