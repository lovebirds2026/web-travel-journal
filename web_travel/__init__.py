import os
import sys
import logging

from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

log_path = os.path.join(os.path.dirname(__file__), 'logs', 'logfile.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
        handlers = [
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_path)
        ],
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARNING,
    )
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# initial db setup
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base) # sets up the engine and the scoped_session automatically

mail = Mail()

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

    # connect Flask with the SQLAlchemy db
    db.init_app(app)
    with app.app_context():
        db.reflect() # get existing tables

    mail.init_app(app) # set up at configuration time

    # blueprints
    from . import auth # deferred import (moves the import from module load time -> call time)
    app.register_blueprint(auth.bluepr)
    from . import routes
    app.register_blueprint(routes.bluepr)

    return app
