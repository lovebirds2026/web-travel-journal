from flask import current_app, Blueprint, render_template, send_from_directory, url_for, redirect, flash
from sqlalchemy.orm import selectinload
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
    """ Displays all continents and max 50 contries with related images. """
    continents = Continent.get_active()
    shuffle(continents)
    for continent in continents:
        continent.img = continent.get_thumbnail() # n queries (7)

    # new approach: get right cards
    right_cards = PhotoRelation.get_card_data(Country)
    shuffle(right_cards)

    return render_template('public/index.html', title='Home', continents=continents,
        countries=right_cards)


@bluepr.route('/continent/<int:id>')
def continent(id):
    """ Displays contries and travels for the continent (if such). """
    continent = db.session.get(Continent, id)
    country_ids = [country.id for country in continent.countries]

    # get travels
    stmt = (
        db.select(Travel.id).select_from(TravelRelation).where(
        TravelRelation.relation == 'continent', TravelRelation.relationFK == continent.id)
        .join(Travel, Travel.id == TravelRelation.travelFK)
    )
    travel_ids = db.session.scalars(stmt).all()

    left_cards = PhotoRelation.get_card_data(Country, country_ids)
    shuffle(left_cards)

    right_cards = PhotoRelation.get_card_data(Travel, travel_ids)
    shuffle(right_cards)

    return render_template('public/continent.html', title=continent.name, continent=continent,
        countries=left_cards, travels=right_cards)


@bluepr.route('/country/<int:id>')
def country(id):
    """ Displays travels and places for the country (if such). """
    country = db.session.get(Country, id)
    for place in country.places:
        place.img = place.get_thumbnail() # n queries, but should be worth it with caching?

    # get travels
    stmt = (
        db.select(Travel.id).select_from(TravelRelation).where(
        TravelRelation.relation == 'country', TravelRelation.relationFK == country.id)
        .join(Travel, Travel.id == TravelRelation.travelFK)
    )
    travel_ids = db.session.scalars(stmt).all()

    left_cards = PhotoRelation.get_card_data(Travel, travel_ids)
    shuffle(left_cards)

    return render_template('public/country.html', title=country.name, country=country,
        travels=left_cards, places=country.places)


@bluepr.route('/travel/<int:id>')
def travel(id):
    """ Displays specific travel details """
    travel = db.session.scalar(db.select(Travel).where(
        Travel.id == id, Travel.public == True, Travel.deleted == False))
    if not travel:
        flash('Travel not found.', 'error')
        return(redirect(url_for('public.index')))

    relations: dict = travel.get_relation_names()
    photos = Photo.get_from_relation(travel)

    return render_template('public/travel.html', title=travel.title, travel=travel, relations=relations, photos=photos)


@bluepr.route('/place/<int:id>')
def place(id):
    """ Displays specific place details """
    place = db.session.scalar(db.select(Place).where(
        Place.id == id, Place.status == FieldStatus.ACTIVE, Place.deleted == False))
    if not place:
        flash('Place not found.', 'error')
        return(redirect(url_for('public.index')))

    stmt = (db.select(Travel).select_from(TravelRelation)
        .where(TravelRelation.relation == 'place', TravelRelation.relationFK == place.id)
        .join(Travel, Travel.id == TravelRelation.travelFK)
        .order_by(Travel.id.asc())
    )
    travels = db.session.scalars(stmt).all()
    print(travels)
    photos = Photo.get_from_relation(place)

    return render_template('public/place.html', title=place.name, place=place, travels=travels, photos=photos)


@bluepr.route('/uploads/photos/<filename>')
def uploaded_photo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_PHOTOS'], filename)

@bluepr.route('/uploads/photos/thumbnails/<filename>')
def uploaded_thumbnail(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_THUMBS'], filename)

