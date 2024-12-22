from flask import Blueprint

bp = Blueprint('quiz', __name__,)

from webapp.quiz import routes, events