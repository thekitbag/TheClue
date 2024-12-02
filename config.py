import os

class Config(object):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	GPT_API_KEY= os.environ.get('GPT_API_KEY')


class DevelopmentConfig(Config):
	SECRET_KEY = 'supersecurepw'

class ProductionConfig(Config):
	SECRET_KEY= os.environ.get('APP_SECRET_KEY')


