from flask import session

from web_travel import db
from web_travel.models.Continent import Continent, FieldStatus

def test_select_one_continent_by_search_field(init_database):
    search_text = 'North '
    search_field = 'name'
    stmt = Continent.search_and_filter({}, search_field, search_text)
    res = db.session.scalars(stmt).all()
    assert len(res) == 1

def test_default_continent_status_is_new(init_database):
    stmt = Continent.search_and_filter({'status': 'new'})
    prepopulated_continent = db.session.scalar(stmt.order_by('id'))
    assert prepopulated_continent.name == 'North America'

def test_change_continent_status(flask_client, init_database):
    continent = db.session.get(Continent, 1)
    assert continent is not None
    assert continent.status != FieldStatus.REJECTED

    # simulate logged in admin user
    with flask_client.session_transaction() as session:
        session['user_id'] = 1
    data = dict(id=continent.id, name=continent.name, status=FieldStatus.REJECTED)
    response = flask_client.post(f'/admin/continents/edit?continentID={continent.id}', data=data)
    assert 'data saved' in response.text
    assert continent.status == FieldStatus.REJECTED

    with flask_client.session_transaction() as session:
        session.clear()

def test_continents_admin_only_access(flask_client):
    response = flask_client.get('/admin/continents/edit', follow_redirects=True)
    assert response.request.path == '/'