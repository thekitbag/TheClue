import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY= os.environ.get('APP_SECRET_KEY')

class DevelopmentConfig(Config):
	SECRET_KEY = 'supersecurepw'

class ProductionConfig(Config):
	CORS_ORIGINS = 'https://www.hedgehog.fyi'



