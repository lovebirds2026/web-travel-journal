from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import update

from ... import db
from web_travel.views.admin import bluepr
from ..auth import admin_required
from ...models.Continent import Continent
from ...models.Country import Country, FieldStatus


@bluepr.route('/countries/list', methods=['GET'])# ?del=<int>
@admin_required
def list_countries():
    if request.args.get('del'):
        country_id = request.args.get('del')
        country = db.get_or_404(Country, country_id)
        country.deleted = not country.deleted
        db.session.commit()
        flash(f'Country {country.name} status changed to {"deleted" if country.deleted else "active"}.')

    filters = {} # Dropdown boolean filters
    if status := request.args.get('status'):
        filters['status'] = status
    if deleted := request.args.get('deleted'):
        filters['deleted'] = deleted == '1'
    if continent_id := request.args.get('continent_id'):
        filters['continentFK'] = continent_id

    search_text = request.args.get('search_text') # Text search in field
    search_field = request.args.get('search_field')

    stmt = Country.search_and_filter(filters, search_field, search_text)
    countries = db.session.scalars(stmt).all()
    continents = Continent.get_active()
    return render_template('admin/countries_list.html', countries=countries, field_statuses=FieldStatus,
        continents=continents)


@bluepr.route('/countries/edit', methods=['GET', 'POST']) # ?countryID=<int>
@admin_required
def add_edit_country():
    if request.method == 'POST':
        name = request.form.get('name')
        continent_id = request.form.get('continent_id')
        if not name:
            flash('Invalid country name.', 'error')
        elif not continent_id:
            flash('Please assign a continent.', 'error')
        else:
            values_dict = dict(
                name=name,
                continentFK=continent_id,
                status=request.form.get('status'),
                deleted=bool(request.form.get('deleted')),
            )

            if country_id := request.form.get('id'): # Update
                stmt = update(Country).where(Country.id == country_id).values(values_dict)
                result = db.session.execute(stmt) # can check result.rowcount
            else: # Add
                new_country = Country(**values_dict)
                db.session.add(new_country)

            db.session.commit()
            flash('Country data saved.')
            return redirect(url_for('admin.list_countries'))

    country_id = request.args.get('countryID') or 0
    country = db.session.get(Country, country_id)
    continents = Continent.get_active()

    return render_template('admin/countries_edit.html', country=country, field_statuses=FieldStatus,
        continents=continents)
