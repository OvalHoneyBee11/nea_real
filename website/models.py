from website import db
from flask_login import UserMixin
import string
import random

# Association table for sharing question sets with classes
class_question_sets = db.Table(
    "class_question_sets",
    db.Column("class_id", db.Integer, db.ForeignKey("class.id")),
    db.Column("question_set_id", db.Integer, db.ForeignKey("question_set.id")),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    question_sets = db.relationship("QuestionSet", backref="user", lazy=True)
    taught_classes = db.relationship(
        "Class", backref="teacher", lazy=True, foreign_keys="Class.teacher_id"
    )

    @property
    def is_teacher(self):
        return self.role == "teacher"

    @property
    def is_student(self):
        return self.role == "student"


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
    memberships = db.relationship(
        "ClassMembership", backref="class_obj", lazy=True, cascade="all, delete-orphan"
    )
    # Question sets shared with this class
    question_sets = db.relationship(
        "QuestionSet",
        secondary=class_question_sets,
        backref=db.backref("classes", lazy="dynamic"),
        lazy="dynamic",
    )
    chat_messages = db.relationship(
        "ChatMessage", backref="class_obj", lazy=True, cascade="all, delete-orphan"
    )
    assignments = db.relationship(
        "Assignment", backref="class_obj", lazy=True, cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("teacher_id", "name", name="unique_class_name_per_teacher"),
    )

    @staticmethod
    def generate_code():
        """Generate a unique 8-character class code"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choices(chars, k=8))
            if not Class.query.filter_by(code=code).first():
                return code


class ClassMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"))
    joined_at = db.Column(db.DateTime(timezone=True), default=db.func.now())


class QuestionSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    questions = db.relationship("Question", backref="question_set", lazy=True)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "name", name="unique_question_set_name_per_user"
        ),
    )


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    question_set_id = db.Column(db.Integer, db.ForeignKey("question_set.id"))


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"), nullable=False)
    user = db.relationship("User", backref="chat_messages")


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    attachment_url = db.Column(db.String(500))
    creator = db.relationship("User", backref="created_assignments")
