from webapp import db 

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(64), index=True, unique=True)
    quiz_name = db.Column(db.String(128))
    num_questions = db.Column(db.Integer)
    # ... other quiz attributes ...

    def __repr__(self):
        return f'<Quiz {self.quiz_name}>'