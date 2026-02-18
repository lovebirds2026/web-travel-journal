import os
from flask import Flask

def create_app(test_config=None):
    """Create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    app.logger.debug('A value for debugging')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists??
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/')
    def index():
        return 'Lovebirds® 2026 Dev domain on Flask 3.1.2 running on Python 3.13 !!'


    return app
