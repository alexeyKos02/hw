from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .config import Config
import logging.config
from flasgger import Swagger

db = SQLAlchemy()
jwt = JWTManager()


def create_app():

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'app.log',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    })

    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SWAGGER'] = {
        'title': 'My App API', 
        'uiversion': 3,
        'swagger_ui': True,
        'doc_expansion': 'none'
    }
    Swagger(app)
    db.init_app(app)
    jwt.init_app(app)
    from .routes import routes
    app.register_blueprint(routes)
    
    with app.app_context():
        db.create_all()
    return app
