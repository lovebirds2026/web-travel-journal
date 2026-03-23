from flask import Blueprint

bluepr = Blueprint('admin', __name__, url_prefix='/admin') # web_travel.admin

from . import views # or from web_travel.admin (absolute path), deferred import too
# registers the routes onto the blueprint (decorators run at import time)
