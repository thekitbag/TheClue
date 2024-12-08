from webapp import db 

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(64), index=True, unique=True)
    quiz_name = db.Column(db.String(128))
    num_questions = db.Column(db.Integer)
    # ... other quiz attributes ...

    def __repr__(self):
        return f'<Quiz {self.quiz_name}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(64), db.ForeignKey('quiz.quiz_id'), index=True)  # Foreign key to Quiz
    question_text = db.Column(db.Text)  # Store the question text
    answer = db.Column(db.String(255))  # Store the correct answer
    options = db.Column(db.String(512))  # Store the answer options (you might need to adjust the type based on how you store them)

    quiz = db.relationship('Quiz', backref='questions')  # Define the relationship

    def __repr__(self):
        return f'<Question {self.question_text}>'
    
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    quiz_id = db.Column(db.String(64), db.ForeignKey('quiz.quiz_id'), index=True)

    quiz = db.relationship('Quiz', backref='players')

    def __repr__(self):
        return f'<Player {self.name}>'