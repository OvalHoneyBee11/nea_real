from website import db
from flask_login import UserMixin


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1500))
    date = db.Column(db.DateTime(timezone=True), default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    tasks = db.relationship("Tasks")


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    answers = db.relationship("Answers", backref="question", lazy=True)


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(500), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    # user = db.relationship("Questions", backref="answers")
