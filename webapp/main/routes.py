from webapp.main import bp
from flask import render_template

@bp.route('/')
@bp.route('/home', methods=['GET'])
def home():
    return render_template('main/index.html') 