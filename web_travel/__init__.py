import os
import sys
import logging

from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from instance.config import *

# configure root logging
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
# logging.getLogger('sqlalchemy').setLevel('INFO')
# initial db setup
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base) # sets up the engine and the scoped_session automatically

mail = Mail()

def create_app(test_app=False):
    app = Flask(__name__)
    app.config.from_object(TestingConfig if test_app else Config)

    # connect Flask with the SQLAlchemy db
    db.init_app(app)
    with app.app_context():
        db.reflect() # get existing tables

    mail.init_app(app) # set up at configuration time

    # blueprints
    from .views import auth # deferred import (moves the import from module load time -> call time)
    app.register_blueprint(auth.bluepr)
    from .views import routes
    app.register_blueprint(routes.bluepr)
    from .views import admin
    app.register_blueprint(admin.bluepr)

    with app.app_context(): # models need to be loaded by now
        db.create_all()

    return app
