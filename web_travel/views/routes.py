from flask import current_app, Blueprint, flash, g, render_template, request, session, \
    make_response, redirect, url_for, send_from_directory
from sqlalchemy import update
from sqlalchemy.orm import selectinload

from datetime import date
import logging
log = logging.getLogger(__name__)

from .. import db
from ..models.User import User
from .auth import login_required
from ..models.Place import Place, FieldStatus
from ..models.Country import Country
from ..models.Travel import Travel
from ..models.TravelRelation import TravelRelation
from ..models.Photo import Photo
from ..models.PhotoRelation import PhotoRelation
from ..utils import save_photo

bluepr = Blueprint('main', __name__) # web_travel.routes

@bluepr.route('/')
def index():
    return render_template('main/index.html', title='Home')


@bluepr.errorhandler(413)
def request_entity_too_large(error):
    flash(f'Max file size is {current_app.config['MAX_CONTENT_LENGTH'] // 1000000} MB.', 'error')
    redirect_url = session.get('last_url', url_for('main.photos'))
    return redirect(redirect_url)


@bluepr.route('/photos/add', methods=['GET', 'POST'])
@login_required
def add_photos():
    if request.method == 'POST':
        # Process photo uploads
        if 'photos' not in request.files or not request.files['photos'].filename:
            flash('Please select some photos.', 'error')
        else:
            photos = []
            relations = request.form.getlist('relations[]') # ['continent:2', 'country:3', ]
            for file in request.files.getlist('photos'):
                if fileinfo := save_photo(file): # saved on drive, now save in db
                    flash(f'Photo {fileinfo.path} uploaded.')
                    name, ext = fileinfo.path.rsplit('.', maxsplit=1)
                    photo = Photo(filename=name, extension=ext, size=fileinfo.size)
                    photos.append(photo)

                    if relations: # because it's new, only update if there are any
                        photo.update_relations(relations)
                else:
                    flash(f'Invalid file: {file.filename}', 'error')
                db.session.add_all(photos)
                db.session.commit()

    all_relations = PhotoRelation.as_dict(g.user.id, g.user.is_admin)
    return render_template('main/photos_edit.html', all_relations=all_relations)

@bluepr.route('/photos', methods=['GET', 'POST'])
@login_required
def photos():
    if request.method == 'POST':
        # Change public/hidden, status or DELETE
        if edit_photo_id := request.form.get('photo_id'):
            edit_photo = db.session.get(Photo, edit_photo_id)
            if edit_photo and (g.user.is_admin or edit_photo.cid == g.user.id):
                new_status = request.form.get('status')
                if g.user.is_admin and new_status and new_status in FieldStatus:
                    edit_photo.status = new_status
                elif request.form.get('delete'):
                    db.session.delete(edit_photo)
                elif public := request.form.get('public'):
                    edit_photo.public = int(public)
                else: # relations-only update
                    relations = request.form.getlist('relations[]')
                    edit_photo.update_relations(relations)
                flash('Photo updated')
                db.session.commit()

    stmt = db.select(Photo).order_by('id')
    if g.user.is_admin:
        stmt = stmt.options(selectinload(Photo.owner))
    else:
        stmt = stmt.where(Photo.cid == g.user.id)
    photos = db.session.scalars(stmt).all()
    for photo in photos:
        photo._relations: dict = photo.get_relation_names()

    all_relations = PhotoRelation.as_dict(g.user.id, g.user.is_admin)
    return render_template('main/photos.html', photos=photos, field_statuses=FieldStatus,
        all_relations=all_relations)


@bluepr.route('/uploads/photos/<filename>')
def uploaded_photo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_PHOTOS'], filename)

@bluepr.route('/uploads/photos/thumbnails/<filename>')
def uploaded_thumbnail(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_THUMBS'], filename)


@bluepr.route('/travels', methods=['GET'])
@login_required
def travels():
    stmt = db.select(Travel).order_by('id')
    if g.user.is_admin:
        stmt = stmt.options(selectinload(Travel.owner))
    else:
        stmt = stmt.where(Travel.cid == g.user.id)
    travels = db.session.scalars(stmt).all()

    return render_template('main/travels.html', travels=travels)


@bluepr.route('/travels/edit', methods=['GET', 'POST']) #travelID=<int>
@login_required
def add_edit_travel():
    travel_id = request.args.get('travelID') or 0
    if travel_id:
        travel = db.session.get(Travel, travel_id)
        if not g.user.is_admin and (not travel or not travel.cid == g.user.id):
            return redirect(url_for('main.index'))

    if request.method == 'POST':
        errors = Travel.validate_input(request.form)
        if errors:
            for msg in errors:
                flash(msg, 'error')
        else:
            Travel.add_edit(request.form)
            flash('Travel data saved.')
            return redirect(url_for('main.travels'))

    travel = db.session.get(Travel, travel_id)
    relations: dict = travel.get_relation_names() if travel else {}
    all_relations = TravelRelation.as_dict(exclude=relations)

    return render_template('main/travels_edit.html', travel=travel, current_relations=relations,
        all_relations=all_relations)


@bluepr.route('/places', methods=['GET'])
def places():
    if g.user and g.user.is_admin and request.args.get('del'):
        place_id = request.args.get('del')
        place = db.get_or_404(Place, place_id)
        place.deleted = not place.deleted
        db.session.commit()
        flash(f'Place {place.name} status changed to {"deleted" if place.deleted else "active"}.')

    filters = {} # Dropdown boolean filters
    if status := request.args.get('status'):
        filters['status'] = status
    if deleted := request.args.get('deleted'):
        filters['deleted'] = deleted == '1'
    if country_id := request.args.get('country_id'):
        filters['countryFK'] = country_id
    if own_only := request.args.get('my'):
        filters['cid'] = g.user.id

    search_text = request.args.get('search_text') # Text search in field
    search_field = request.args.get('search_field')

    stmt = Place.search_and_filter(filters, search_field, search_text)
    # eager load relations. Also joinedload(Place.country) or in model: relationship(lazy="selectin")
    stmt = stmt.options(selectinload(Place.country), selectinload(Place.owner))

    if not g.user:
        stmt = stmt.where(Place.status == FieldStatus.ACTIVE, Place.deleted == False)
    elif not g.user.is_admin:
        stmt = stmt.where( (Place.cid == g.user.id) | 
            (Place.status == FieldStatus.ACTIVE) & (Place.deleted == False) )
    places = db.session.scalars(stmt).all()
    countries = Country.get_active()

    return render_template('main/places.html', places=places, countries=countries, 
        field_statuses=FieldStatus)


@bluepr.route('/places/edit', methods=['GET', 'POST']) # ?placeID=<int>
@login_required
def add_edit_place():
    place_id = request.args.get('placeID') or 0
    if place_id:
        place = db.session.get(Place, place_id)
        if not g.user.is_admin and (not place or not place.cid == g.user.id):
            return redirect(url_for('main.index'))

    if request.method == 'POST':
        errors = Place.add_edit(request.form, is_admin=g.user.is_admin)
        if errors:
            for msg in errors:
                flash(msg, 'error')
        else:
            flash('Place data saved.')
            return redirect(url_for('main.places'))

    place = db.session.get(Place, place_id)
    countries = Country.get_active()

    return render_template('main/places_edit.html', place=place, field_statuses=FieldStatus,
        countries=countries)


@bluepr.route('/user', methods=['GET', 'POST'])
@login_required
def user_account():
    if request.method == 'POST':
        g.user.full_name = request.form['full_name']
        password = request.form['password']
        password2 = request.form['password2']
        error = None

        if len(password) > 0: # user wants to update their password
            if password != password2:
                error = 'Passwords do not match.'
            else:
                g.user.set_password(password)

        if not error:
            db.session.commit()
            flash('Changes saved.')
        else:
            flash(error, 'error')

    return render_template('main/user.html')

