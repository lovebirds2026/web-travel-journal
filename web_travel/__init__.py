import sys
import logging
import logging.handlers
import warnings
warnings.filterwarnings('ignore', module='flask_ckeditor') # silences WTFForms and bleach not installed

from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from instance.config import LOG_PATH, UPLOAD_PATH_PHOTOS, Config, TestingConfig

# initial db setup
class SABase(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=SABase) # sets up the engine and the scoped_session automatically

mail = Mail()
ckeditor = CKEditor()

def create_app(test_app=False):
    configure_logging()

    UPLOAD_PATH_PHOTOS.mkdir(mode=0o777, parents=True, exist_ok=True)

    app = Flask(__name__)
    app.config.from_object(TestingConfig if test_app else Config)

    # connect Flask with the SQLAlchemy db
    db.init_app(app)
    with app.app_context():
        db.reflect() # get existing tables

    mail.init_app(app) # set up at configuration time
    ckeditor.init_app(app)

    # blueprints
    from .views import auth # deferred import (moves the import from module load time -> call time)
    app.register_blueprint(auth.bluepr)
    from .views import routes_public
    app.register_blueprint(routes_public.bluepr)
    from .views import routes_logged
    app.register_blueprint(routes_logged.bluepr)
    from .views import admin
    app.register_blueprint(admin.bluepr)

    with app.app_context(): # models need to be loaded by now
        db.create_all()

    return app

def configure_logging():
    LOG_PATH.parent.mkdir(mode=0o777, exist_ok=True)
    logging.basicConfig(
        handlers = [
            logging.StreamHandler(sys.stderr),
            logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=1024 * 1024, backupCount=4)
        ],
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARNING,
    )
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)