from flask import Blueprint, flash, g, render_template, request, session, make_response, \
    redirect, url_for
from sqlalchemy import update
from sqlalchemy.orm import selectinload

from datetime import date

from .. import db
from ..models.User import User
from .auth import login_required
from ..models.Place import Place, FieldStatus
from ..models.Country import Country
from ..models.Travel import Travel

bluepr = Blueprint('main', __name__) # web_travel.routes

@bluepr.route('/')
def index():
    return render_template('main/index.html', title='Home')


@bluepr.route('/travels', methods=['GET'])
@login_required
def travels():
    stmt = db.select(Travel).order_by('id')
    if g.user.is_admin:
        stmt = stmt.options(selectinload(Travel.owner))
    else:
        stmt = stmt.where(Travel.ownerFK == g.user.id)
    travels = db.session.scalars(stmt).all()

    return render_template('main/travels.html', travels=travels)


@bluepr.route('/travels/edit', methods=['GET', 'POST']) #travelID=<int>
@login_required
def add_edit_travel():
    travel_id = request.args.get('travelID') or 0
    if travel_id:
        travel = db.session.get(Travel, travel_id)
        if not g.user.is_admin and (not travel or not travel.ownerFK == g.user.id):
            return redirect(url_for('main.index'))

    if request.method == 'POST':
        errors = []
        title = request.form.get('title')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        if not title:
            errors.append('Travel name is required.')
        if not date_from or not date_to:
            errors.append('Both from and to dates are required.')
        else:
            try:
                date_from = date.fromisoformat(date_from)
                date_to = date.fromisoformat(date_to)
            except ValueError:
                errors.append('Invalid date format.')

        if not errors:
            values_dict = dict(
                title=title,
                user_note=request.form.get('notes'),
                date_from=date_from,
                date_to=date_to,
                public=bool(request.form.get('public', False)),
            )
            if travel_id := request.form.get('id', 0): # Update
                stmt = update(Travel).where(Travel.id == travel_id).values(values_dict)
                db.session.execute(stmt)
            else: # Add
                new_travel = Travel(**values_dict, ownerFK=g.user.id)
                db.session.add(new_travel)

            db.session.commit()
            flash('Travel data saved.')
            return redirect(url_for('main.travels'))

        for msg in errors:
            flash(msg, 'error')

    travel = db.session.get(Travel, travel_id)
    return render_template('main/travels_edit.html', travel=travel)


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
        filters['ownerFK'] = g.user.id

    search_text = request.args.get('search_text') # Text search in field
    search_field = request.args.get('search_field')

    stmt = Place.search_and_filter(filters, search_field, search_text)
    # eager load relations. Also joinedload(Place.country) or in model: relationship(lazy="selectin")
    stmt = stmt.options(selectinload(Place.country), selectinload(Place.owner))

    if not g.user:
        stmt = stmt.where(Place.status == FieldStatus.ACTIVE, Place.deleted == False)
    elif not g.user.is_admin:
        stmt = stmt.where( (Place.ownerFK == g.user.id) | 
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
        if not g.user.is_admin and (not place or not place.ownerFK == g.user.id):
            return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        country_id = request.form.get('country_id')
        if not name:
            flash('Invalid place name.', 'error')
        elif not country_id:
            flash('Please assign a country.', 'error')
        else:
            values_dict = dict(
                name=name,
                description=request.form.get('description', ''),
                countryFK=country_id,
                deleted=bool(request.form.get('deleted')),
            )
            if g.user.is_admin and request.form.get('status'):
                values_dict['status'] = request.form.get('status')

            if place_id := request.form.get('id', 0): # Update
                stmt = update(Place).where(Place.id == place_id).values(values_dict)
                db.session.execute(stmt)
            else: # Add
                new_place = Place(**values_dict, ownerFK=g.user.id)
                db.session.add(new_place)

            db.session.commit()
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

