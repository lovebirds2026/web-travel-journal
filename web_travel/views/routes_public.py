from flask import current_app, Blueprint, render_template, send_from_directory, url_for
from random import shuffle

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
    shuffle(continents)
    for continent in continents:
        continent.img = continent.get_thumbnail() # n queries (7)

    # new approach: get right cards
    right_cards = PhotoRelation.get_card_data(Continent)
    shuffle(right_cards)

    return render_template('public/index.html', title='Home', continents=continents,
        countries=right_cards)


@bluepr.route('/uploads/photos/<filename>')
def uploaded_photo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_PHOTOS'], filename)

@bluepr.route('/uploads/photos/thumbnails/<filename>')
def uploaded_thumbnail(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_THUMBS'], filename)

