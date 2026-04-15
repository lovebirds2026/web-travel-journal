from flask import Blueprint

bluepr = Blueprint('admin', __name__, url_prefix='/admin') # web_travel.admin

# register the routes onto the blueprint (decorators run at import time)
from . import users, continents, countries # or from web_travel.admin (absolute path)
