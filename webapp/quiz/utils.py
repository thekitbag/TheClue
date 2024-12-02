import uuid
from webapp import db  
from webapp.models import Quiz
import openai
import os
from flask import current_app

def store_quiz_configuration(quiz_id, quiz_name, num_questions):
    quiz = Quiz(quiz_id=quiz_id, quiz_name=quiz_name, num_questions=num_questions)
    db.session.add(quiz)
    db.session.commit()

def generate_quiz_id():
    return str(uuid.uuid4())

def generate_questions(topic, num_questions):
    openai.api_key = current_app.config['GPT_API_KEY']


    system_message = "You are quizGPT, you will receive a topic and a number of questions. \
    Provide the questions and answers in json format. The players will be british and of slightly \
    above average intelligence"

    user_message = f"{num_questions} about {topic}"
                
    response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": user_message}
                        ]
                    )
    
    print(response)

    questions = response.choices[0].text.strip().split("\n")

    print(questions)
    return questions