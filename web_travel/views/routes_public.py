from flask import current_app, Blueprint, render_template, send_from_directory

import logging
log = logging.getLogger(__name__)

from .. import db
from ..models.Place import Place, FieldStatus
from ..models.Country import Country
from ..models.Travel import Travel
from ..models.TravelRelation import TravelRelation
from ..models.Photo import Photo
from ..models.PhotoRelation import PhotoRelation

bluepr = Blueprint('public', __name__)

@bluepr.route('/')
def index():
    return render_template('public/index.html', title='Home')


@bluepr.route('/uploads/photos/<filename>')
def uploaded_photo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_PHOTOS'], filename)

@bluepr.route('/uploads/photos/thumbnails/<filename>')
def uploaded_thumbnail(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_THUMBS'], filename)

