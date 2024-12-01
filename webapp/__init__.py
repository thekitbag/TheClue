from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from webapp.main import bp as main_bp
    app.register_blueprint(main_bp)

    from webapp.auth import bp as account_bp
    app.register_blueprint(account_bp)

    from webapp.quiz import bp as quiz_bp
    app.register_blueprint(quiz_bp)

    return app





