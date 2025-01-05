import uuid
from webapp import db
from webapp import socketio
from webapp.models import Quiz, Question, CurrentQuestion
from openai import OpenAI
import os
import json
from flask import current_app

def store_quiz_configuration(quiz_id, quiz_name, num_questions, num_players, questions):

    quiz = Quiz(quiz_id=quiz_id, quiz_name=quiz_name, num_players=num_players, num_questions=num_questions, state='registering')
    db.session.add(quiz)


    for question_data in questions:
        question = Question(quiz_id=quiz_id, 
                            question_text=question_data['question'], 
                            answer=question_data['answer'],
                            options=", ".join(question_data['options'])) 
        db.session.add(question)
    
    first_question = Question.query.filter_by(quiz_id=quiz_id).first() 
    current_question_entry = CurrentQuestion(quiz_id=quiz.quiz_id, question=first_question)
    db.session.add(current_question_entry)    
    db.session.commit()

def generate_quiz_id():
    return str(uuid.uuid4())

def generate_questions(topic, num_questions):
    client = OpenAI(api_key=current_app.config['GPT_API_KEY'])



    system_message = "You are quizGPT, you will receive a topic and a number of questions. \
    Provide the questions and answers in json format. The players will be british and of significantly \
    above average intelligence, but not genius level. You should always provide four options and indicate which one is correct.\
    The response should be JSON which consists of a list of dictionaries. Each list has 3 keys: 'question', \
    'options' and 'answer'. 'question' should have a value thas is a string containing a question. 'options' \
    should be a list of strings containing the possible answers', 'answer' should contain a string matching one of \
    the options and be the one that is the correct answer to the question."

    user_message = f"{num_questions} questions about {topic}"
                
    response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                        "role": "system",
                        "content": [
                            {
                            "type": "text",
                            "text": system_message
                            }
                        ]
                        },
                        {
                        "role": "user",
                        "content": [
                            {
                            "type": "text",
                            "text": user_message
                            }
                        ]
                        }
                    ],
                    response_format={
                        "type": "json_object"
                    },
                    temperature=1,
                    max_tokens=2048,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                    )
    content = response.choices[0].message.content
    content_dict = json.loads(content)  
    questions = content_dict['questions']
    print(questions)
    
    return questions


def emit_next_question(quiz_id):
    quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
    if quiz:
        current_question_index = quiz.questions.index(quiz.current_question_relationship.question)
        if current_question_index <= len(quiz.questions) - 1:
            next_question = quiz.questions[current_question_index]
            options = next_question.options.split(', ')
            socketio.emit('question', {'quiz_id': quiz_id, 'question': next_question.question_text, 'options': options}, namespace='/quiz')
        else:
            socketio.emit('quiz_ended', {'quiz_id': quiz_id}, namespace='/quiz')