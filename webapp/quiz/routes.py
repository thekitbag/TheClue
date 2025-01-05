import time
from flask import render_template, request, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
from .utils import generate_quiz_id, store_quiz_configuration, generate_questions, emit_next_question
from webapp.models import Quiz, CurrentQuestion, Answer, Question, UserQuizzes, User
from webapp.quiz import bp  
from webapp import socketio
from webapp import db


@bp.route('/quiz')
@login_required 
def home():
    return render_template('quiz/quiz_home.html')

@bp.route('/join_quiz')
@login_required 
def join_a_quiz():
    quizzes = Quiz.query.all()
    if quizzes is None:
        return "No quizes have been started. Please go back and start one"
    return render_template('quiz/join_quiz.html', quizzes=quizzes)

@bp.route('/start_quiz', methods=['GET', 'POST'])
@login_required 
def start_quiz():
    if request.method == 'POST':
        quiz_name = request.form['quiz_name']
        num_questions = int(request.form['num_questions'])
        num_players = int(request.form['num_players'])  

        quiz_id = generate_quiz_id()
        example_questions = [{'answer': 'O', 
                            'question': 'What is the chemical symbol for oxygen on the periodic table?',
                            'options': ['O', 'O2', 'Ox', 'V']
                            }, 
                            {'answer': 'Gustav Holst', 
                            'question': "Which British composer is known for his work titled 'The Planets Suite' that includes the movement 'Mars, the Bringer of War'?",
                            'options': ['Gustav Holst', 'Benjamin Britton', 'Edward Elgar']
                            }, 
                            {'answer': 'The River Thames', 
                            'question': 'What is the name of the river that flows through Oxford, England?',
                            'options': ['The River Thames', 'The Severn', 'The Seine']
                            }]

        #questions = generate_questions('The hertfordshire town of tring', num_questions)
        
        store_quiz_configuration(quiz_id, quiz_name, num_questions, num_players, example_questions)  

        return redirect(url_for('quiz.host_quiz', quiz_id=quiz_id))

    return render_template('quiz/start_quiz.html') 

@bp.route('/play/<quiz_id>')
@login_required 
def play_quiz(quiz_id):
    quiz_data = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if quiz_data is None:
        return "Quiz not found"

    return render_template('quiz/play_quiz.html', quiz_data=quiz_data)

@bp.route('/join/<quiz_id>', methods=['POST'])
@login_required 
def join_quiz(quiz_id):
    quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()

    if len(quiz.user_quizzes_rel.all()) >= quiz.num_players:  
        return jsonify({'error': 'Quiz is full'}), 401

    current_user.quizzes.append(quiz)
    db.session.commit()

    socketio.emit('player_joined', {'quiz_id': quiz_id, 'username': current_user.username}, namespace='/quiz')

    if len(quiz.user_quizzes_rel.all()) == quiz.num_players:
        quiz.state = 'started'
        db.session.commit()
        socketio.emit('quiz_start', {'quiz_id': quiz_id}, namespace='/quiz')
        time.sleep(3)

        # Get the first question using current_question_relationship
        first_question = quiz.current_question_relationship.question  
        question = first_question.question_text
        options = first_question.options.split(', ')

        socketio.emit('question', {'quiz_id': quiz_id, 'question': question, 'options': options}, namespace='/quiz')


    return jsonify({'message': 'Joined quiz successfully', 'user_id': current_user.id}), 200

@bp.route('/host/<quiz_id>')
@login_required 
def host_quiz(quiz_id):
    quiz_data = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if quiz_data is None:
        return "Quiz not found"
    print(quiz_data.id)
    current_question_id = CurrentQuestion.query.get(quiz_data.id).id
    print(current_question_id)
    current_question = Question.query.get(current_question_id)
    current_question_text = current_question.question_text

    
    return render_template('quiz/host_quiz.html',  quiz_data=quiz_data, current_question=current_question_text)

@bp.route('/players/<quiz_id>')
@login_required
def get_players(quiz_id):
    quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if quiz is None:
        return jsonify({'error': 'Quiz not found'}), 404

    # Get all UserQuizzes entries for the quiz
    user_quizzes = UserQuizzes.query.filter_by(quiz_id=quiz_id).all()  

    users_and_points = []
    for user_quiz in user_quizzes:
        users_and_points.append({
            'name': user_quiz.user.username,
            'points': user_quiz.score
        })

    return jsonify(users_and_points)


@bp.route('/answer', methods=['POST'])
@login_required
def handle_answer():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    answer = data.get('answer')

    current_question_rel = CurrentQuestion.query.filter_by(quiz_id=quiz_id).first()
    if not current_question_rel:
        return jsonify({'error': 'Quiz or question not found'}), 404
    question = current_question_rel.question

    answer_record = Answer(user_id=current_user.id, question_id=question.id, answer_text=answer)
    db.session.add(answer_record)
    db.session.commit()

    is_correct = answer == question.answer

    user_quiz = UserQuizzes.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if user_quiz:
        if is_correct:
            user_quiz.score += 1
        db.session.commit()

    socketio.emit('answer_submitted', {
        'quiz_id': quiz_id,
        'user_id': current_user.id, 
        'is_correct': is_correct
    }, namespace='/quiz')

    quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if quiz is None:
        return jsonify({'error': 'Quiz not found'}), 404

    quiz_users = User.query.join(UserQuizzes).filter(UserQuizzes.quiz_id == quiz_id).all()  

    current_question_id = current_question_rel.question_id

    if all(any(a.question_id == current_question_id for a in user.answers) for user in quiz_users):
        socketio.emit('all_players_answered', {'quiz_id': quiz_id, 'correct_answer': question.answer}, namespace='/quiz')

        current_question_index = quiz.questions.index(question)
        if current_question_index < len(quiz.questions) - 1:
            quiz.current_question_relationship.question = quiz.questions[current_question_index + 1]
            db.session.commit()
            time.sleep(5)
            emit_next_question(quiz_id)
        else:
            quiz.state = 'finished'
            db.session.commit()
            socketio.emit('quiz_finished', {'quiz_id': quiz_id}, namespace='/quiz')

    return jsonify({'message': 'Answer received'}), 200

 
    







        