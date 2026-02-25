from flask import Flask
from sqlalchemy import MetaData
#from .db import db

def create_app(test_config=None):
    """Create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.logger.debug('?')

    # db.init_app(app) # register the current Flask app with this SQLAlchemy instance

    # metadata_obj = MetaData(schema="public")
    # metadata_obj.reflect(db)
    # print(metadata_obj)

    # with app.app_context():
    #     db.reflect() # not working
    # From the default bind key
    # class User(db.Model):
    #     __table__ = db.metadata.tables["user"]
    # print(User.__table__)


    @app.route('/')
    def index():
        return 'Lovebirds® 2026 Dev domain on Flask 3.1.2 running on Python 3.13 !!'

    return app


