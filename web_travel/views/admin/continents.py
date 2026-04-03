from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import update

from ... import db
from web_travel.views.admin import bluepr
from ..auth import admin_required
from ...models.Continent import Continent, FieldStatus


@bluepr.route('/continents/list', methods=['GET'])# ?del=<int>
@admin_required
def list_continents():
    if request.args.get('del'):
        continent_id = request.args.get('del')
        continent = db.get_or_404(Continent, continent_id)
        continent.deleted = not continent.deleted
        db.session.commit()
        flash(f'Continent {continent.name} status changed to {"deleted" if continent.deleted else "active"}.')

    filters = {} # Dropdown boolean filters
    status = request.args.get('status')
    if status:
        filters['status'] = status
    deleted = request.args.get('deleted')
    if deleted:
        filters['deleted'] = deleted == '1'
    search_text = request.args.get('search_text') # Text search in field
    search_field = request.args.get('search_field')

    stmt = Continent.search_and_filter(filters, search_field, search_text)
    continents = db.session.scalars(stmt).all()
    return render_template('admin/continents_list.html', continents=continents, field_statuses=FieldStatus)


@bluepr.route('/continents/edit', methods=['GET', 'POST']) # ?continentID=<int>
@admin_required
def add_edit_continent():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Invalid continent name.', 'error')
        else:
            values_dict = dict(
                name=name,
                status=request.form.get('status'),
                deleted=bool(request.form.get('deleted')),
            )

            if continent_id := request.form.get('id'): # Update
                stmt = update(Continent).where(Continent.id == continent_id).values(values_dict)
                result = db.session.execute(stmt) # can check result.rowcount
            else: # Add
                new_continent = Continent(**values_dict)
                db.session.add(new_continent)
            
            db.session.commit()
            flash('Continent data saved.')

    continent_id = request.args.get('continentID') or None
    continent = db.session.get(Continent, continent_id)

    return render_template('admin/continents_edit.html', continent=continent, field_statuses=FieldStatus)
