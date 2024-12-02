import os
from webapp import create_app
from config import DevelopmentConfig, ProductionConfig

if os.environ['FLASK_ENV'] == 'development':
    app = create_app(DevelopmentConfig)
elif os.environ['FLASK_ENV'] == 'prod':
    app = create_app(ProductionConfig)
else:
    print('ENV NOT SET TO dev, staging or prod')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)