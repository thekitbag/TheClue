from flask import render_template, request, redirect, url_for, session
from .utils import generate_quiz_id, store_quiz_configuration, generate_questions 
from webapp.models import Quiz
from webapp.quiz import bp  

@bp.route('/quiz') 
def home():
    return render_template('quiz/quiz_home.html')

@bp.route('/join_quiz')
def join_quiz():
    # Logic to display available quizzes (we'll add this later)
    quizzes = get_available_quizzes()  # You'll need to implement this
    return render_template('quiz/join_quiz.html', quizzes=quizzes)

@bp.route('/start_quiz', methods=['GET', 'POST'])
def start_quiz():
    if request.method == 'POST':
        quiz_name = request.form['quiz_name']
        num_questions = int(request.form['num_questions'])
        

        quiz_id = generate_quiz_id()
        store_quiz_configuration(quiz_id, quiz_name, num_questions)

        #questions = generate_questions(quiz_name, num_questions)
        #session['questions'] = questions 

        return redirect(url_for('quiz.play_quiz', quiz_id=quiz_id))

    return render_template('quiz/start_quiz.html') 

@bp.route('/play/<quiz_id>')
def play_quiz(quiz_id):
    quiz_data = Quiz.query.filter_by(quiz_id=quiz_id).first()
    #questions = session.get('questions', [])  # Retrieve questions from the session
    example_questions = [{'answer': 'O', 'question': 'What is the chemical symbol for oxygen on the periodic table?'}, {'answer': 'Gustav Holst', 'question': "Which British composer is known for his work titled 'The Planets Suite' that includes the movement 'Mars, the Bringer of War'?"}, {'answer': 'The River Thames', 'question': 'What is the name of the river that flows through Oxford, England?'}]
    if quiz_data is None:
        # Handle the case where the quiz is not found (e.g., show an error message)
        return "Quiz not found" 
    
    current_question = example_questions[0]  # Get the first question (for now)


    return render_template('quiz/play_quiz.html', quiz_data=quiz_data, questions=example_questions, current_question=current_question)





        