import os
import sys
import logging

from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

log_path = os.path.join(os.path.dirname(__file__), 'logs', 'logfile.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
        handlers = [
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_path)
        ],
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
    )
log = logging.getLogger(__name__)

# db setup
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base) # sets up the engine and the scoped_session automatically

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.config.update(SQLALCHEMY_DATABASE_URI = app.config.get('DATABASE_URL'))
    #log.info(app.config)

    db.init_app(app) # connect Flask with the SQLAlchemy db

    # blueprints
    from . import auth # deferred import (moves the import from module load time -> call time)
    app.register_blueprint(auth.bluepr)

    @app.route('/')
    def index():
        return 'Lovebirds® 2026 Dev domain on Flask 3.1.2 running on Python 3.13'

    return app


