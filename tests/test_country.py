from flask import session

from web_travel import db
from web_travel.models.Country import Country, FieldStatus

def test_select_one_country_by_search_field(init_database):
    stmt = Country.search_and_filter({'continentFK': 1})
    res = db.session.scalars(stmt).all()
    assert len(res) == 1

def test_default_country_status_is_new(init_database):
    stmt = Country.search_and_filter({'status': FieldStatus.NEW})
    prepopulated_country = db.session.scalar(stmt)
    assert prepopulated_country.name == 'Bolivia'

def test_change_country_status(flask_client, init_database):
    country = db.session.get(Country, 1)
    assert country is not None
    assert country.status == FieldStatus.NEW

    # simulate logged in admin user
    with flask_client.session_transaction() as session:
        session['user_id'] = 1
    data = dict(id=country.id, name=country.name, continent_id=country.continentFK, status=FieldStatus.REJECTED)
    response = flask_client.post(f'/admin/countries/edit?countryID={country.id}', data=data)
    assert 'data saved' in response.text
    assert country.status == FieldStatus.REJECTED

    with flask_client.session_transaction() as session:
        session.clear()

def test_countries_admin_only_access(flask_client):
    response = flask_client.get('/admin/countries/edit', follow_redirects=True)
    assert response.request.path == '/'