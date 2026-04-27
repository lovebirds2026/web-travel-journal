from flask import session
from sqlalchemy.orm import joinedload

from web_travel import db
from web_travel.models.Place import Place, FieldStatus

def test_place_attributes_exist(init_database):
    stmt = Place.search_and_filter(dict(name='Hand of God')).options(joinedload(Place.country))
    result = db.session.scalar(stmt)
    assert result.country.name == 'Chad'

def test_user_has_relation_with_his_places(User, init_database):
    normal_user = db.session.get(User, 2)
    assert len(normal_user.places) == 2

def test_create_place_with_default_status_new(flask_client, init_database):
    # simulate logged in normal user
    with flask_client.session_transaction() as session:
        session['user_id'] = 2
    
    # create a new place
    data = dict(name='Test place 3', description='description', country_id=3, user_id=2)
    response = flask_client.post('/places/edit', data=data, follow_redirects=True)
    assert 'data saved' in response.text
    
    # test default status
    new_place = db.session.execute(db.select(Place).where(Place.description == 'description')).scalar()
    assert new_place.status == FieldStatus.NEW

    # try to edit status with normal user (not allowed)
    data.update(dict(id=new_place.id, status=FieldStatus.ACTIVE))
    response = flask_client.post(f'/places/edit?placeID={new_place.id}', data=data)
    assert new_place.status == FieldStatus.NEW

    # clear user from session
    with flask_client.session_transaction() as session:
        session.clear()

def test_view_only_public_active_as_guest(flask_client, init_database):
    response = flask_client.get('/places')
    rows = response.text.count('<tr>')
    assert rows == 2 # thead>tr and Hand of God sole active place

def test_view_all_as_admin(flask_client, init_database):
    with flask_client.session_transaction() as session:
        session['user_id'] = 1

    response = flask_client.get('/places')
    rows = response.text.count('<tr>')
    assert rows == 4 # thead>tr and 3 other - 2 predefined + 1 test

    with flask_client.session_transaction() as session:
        session.clear()
