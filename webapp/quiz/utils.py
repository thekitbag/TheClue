import uuid
from webapp import db  
from webapp.models import Quiz
from openai import OpenAI
import os
import json
from flask import current_app

def store_quiz_configuration(quiz_id, quiz_name, num_questions):
    quiz = Quiz(quiz_id=quiz_id, quiz_name=quiz_name, num_questions=num_questions)
    db.session.add(quiz)
    db.session.commit()

def generate_quiz_id():
    return str(uuid.uuid4())

def generate_questions(topic, num_questions):
    client = OpenAI(api_key=current_app.config['GPT_API_KEY'])



    system_message = "You are quizGPT, you will receive a topic and a number of questions. \
    Provide the questions and answers in json format. The players will be british and of slightly \
    above average intelligence"

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
    
    return questions