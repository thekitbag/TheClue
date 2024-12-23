import time
from flask import render_template, request, redirect, url_for, session, jsonify
from .utils import generate_quiz_id, store_quiz_configuration, generate_questions, emit_next_question
from webapp.models import Quiz, Player, CurrentQuestion, Answer
from webapp.quiz import bp  
from webapp import socketio
from webapp import db


@bp.route('/quiz') 
def home():
    return render_template('quiz/quiz_home.html')

@bp.route('/join_quiz')
def join_a_quiz():
    quizzes = Quiz.query.all()
    if quizzes is None:
        return "No quizes have been started. Please go back and start one"
    return render_template('quiz/join_quiz.html', quizzes=quizzes)

@bp.route('/start_quiz', methods=['GET', 'POST'])
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

        #questions = generate_questions('General Knowledge', num_questions)
        
        store_quiz_configuration(quiz_id, quiz_name, num_questions, num_players, example_questions)  

        return redirect(url_for('quiz.host_quiz', quiz_id=quiz_id))

    return render_template('quiz/start_quiz.html') 

@bp.route('/play/<quiz_id>')
def play_quiz(quiz_id):
    quiz_data = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if quiz_data is None:
        return "Quiz not found"

    return render_template('quiz/play_quiz.html', quiz_data=quiz_data)

@bp.route('/join/<quiz_id>', methods=['POST'])
def join_quiz(quiz_id):
    player_name = request.form.get('player_name')
    if not player_name:
        return jsonify({'error': 'Player name is required'}), 400

    quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if len(quiz.players) >= quiz.num_players:
        return jsonify({'error': 'Quiz is full'}), 

    player = Player(name=player_name, quiz_id=quiz_id)

    db.session.add(player)
    db.session.commit()

    socketio.emit('player_joined', {'quiz_id': quiz_id, 'player_name': player_name}, namespace='/quiz')

    if len(quiz.players) == quiz.num_players:
        socketio.emit('quiz_start', {'quiz_id': quiz_id}, namespace='/quiz')
        time.sleep(3)
        question = quiz.questions[0].question_text
        options = quiz.questions[0].options.split(', ')
        print(options)
        socketio.emit('question', {'quiz_id': quiz_id, 'question': question, 'options': options}, namespace='/quiz')


    return jsonify({'message': 'Joined quiz successfully', 'player_id': player.id}), 200

@bp.route('/host/<quiz_id>')
def host_quiz(quiz_id):
    quiz_data = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if quiz_data is None:
        return "Quiz not found"
    
    return render_template('quiz/host_quiz.html', quiz_data=quiz_data)

@bp.route('/players/<quiz_id>')
def get_players(quiz_id):
    players = Player.query.filter_by(quiz_id=quiz_id).all()
    players_and_points = [{'name':player.name, 'points':player.score} for player in players]
    return jsonify(players_and_points)

@bp.route('/answer', methods=['POST'])
def handle_answer():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    player_id = data.get('player_id')
    answer = data.get('answer')

    player = Player.query.filter_by(id=player_id, quiz_id=quiz_id).first()
    current_question_relationship = CurrentQuestion.query.filter_by(quiz_id=quiz_id).first()
    question = current_question_relationship.question

    answer_record = Answer(player_id=player.id, question_id=question.id, answer_text=answer)
    db.session.add(answer_record)
    db.session.commit()

    if player is None or question is None:
        return jsonify({'error': 'Player or question not found'}), 400

    is_correct = answer == question.answer

    if is_correct:
        player.score = (player.score or 0) + 1 
        db.session.commit()

    socketio.emit('answer_submitted', {
        'quiz_id': quiz_id,
        'player_name': player.name,
        'is_correct': is_correct
    }, namespace='/quiz')

    quiz_players = Player.query.filter_by(quiz_id=quiz_id).all()
    current_question_id = CurrentQuestion.query.filter_by(quiz_id=quiz_id).first().question_id

    if all(any(answer.question_id == current_question_id for answer in player.answers) for player in quiz_players):
        socketio.emit('all_players_answered', {'quiz_id': quiz_id}, namespace='/quiz')
        quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
        current_question_index = quiz.questions.index(quiz.current_question_relationship.question)
        if current_question_index < len(quiz.questions):
            quiz.current_question_relationship.question = quiz.questions[current_question_index + 1]
        db.session.commit()
        time.sleep(5)
        emit_next_question(quiz_id)

    return jsonify({'message': 'Answer received'}), 200

 
    







        