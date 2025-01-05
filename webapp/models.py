from webapp import db, login
from flask_login import UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(64), index=True, unique=True)
    quiz_name = db.Column(db.String(128))
    num_questions = db.Column(db.Integer)
    num_players = db.Column(db.Integer)
    state = db.Column(db.String(64))

    def __repr__(self):
        return f'<Quiz {self.quiz_name}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(64), db.ForeignKey('quiz.quiz_id'), index=True)
    question_text = db.Column(db.Text)  # Store the question text
    answer = db.Column(db.String(255))  # Store the correct answer
    options = db.Column(db.String(512))  # Store the answer options (you might need to adjust the type based on how you store them)

    quiz = db.relationship('Quiz', backref='questions', foreign_keys=[quiz_id])  # Specify foreign_keys

    def __repr__(self):
        return f'<Question {self.question_text}>'

class CurrentQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(64), db.ForeignKey('quiz.quiz_id'), unique=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    quiz = db.relationship('Quiz', backref=db.backref('current_question_relationship', uselist=False)) # Use uselist=False for one-to-one
    question = db.relationship('Question')

    def __repr__(self):
        return f'<CurrentQuestion for Quiz {self.quiz_id}>'
    
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    quiz_id = db.Column(db.String(64), db.ForeignKey('quiz.quiz_id'), index=True)
    score = db.Column(db.Integer, default=0)  # Add the score attribute with a default value of 0


    quiz = db.relationship('Quiz', backref='players')

    def __repr__(self):
        return f'<Player {self.name}>'


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), index=True)
    answer_text = db.Column(db.String(255))  # Store the player's answer

    player = db.relationship('Player', backref='answers')
    question = db.relationship('Question', backref='answers')

    def __repr__(self):
        return f'<Answer by {self.player.name} to {self.question.question_text}>'
