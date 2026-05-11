from flask import current_app, Blueprint, render_template, send_from_directory, url_for

import logging
log = logging.getLogger(__name__)

from .. import db
from ..models.Place import Place, FieldStatus
from ..models.Continent import Continent
from ..models.Country import Country
from ..models.Travel import Travel
from ..models.TravelRelation import TravelRelation
from ..models.Photo import Photo
from ..models.PhotoRelation import PhotoRelation

bluepr = Blueprint('public', __name__)

@bluepr.route('/')
def index():
    continents = Continent.get_active()
    countries = Country.get_active()
    for continent in continents:
        thumb = continent.get_thumbnail()
        if thumb:
            continent.thumbnail = url_for('public.uploaded_thumbnail', filename=thumb.filename + '.' + thumb.extension)
        else:
            continent.thumbnail = url_for('static', filename='world_placeholder.png')
        # print(continent.name, continent.thumbnail)

    for country in countries:
        thumb = country.get_thumbnail()
        if thumb:
            country.thumbnail = url_for('public.uploaded_thumbnail', filename=thumb.filename + '.' + thumb.extension)
        else:
            country.thumbnail = url_for('static', filename='world_placeholder.png')

    return render_template('public/index.html', title='Home', continents=continents,
        countries=countries)


@bluepr.route('/uploads/photos/<filename>')
def uploaded_photo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_PHOTOS'], filename)

@bluepr.route('/uploads/photos/thumbnails/<filename>')
def uploaded_thumbnail(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_THUMBS'], filename)

