from flask import session
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from datetime import date

from web_travel import db
from web_travel.models.Travel import Travel
from web_travel.models.TravelRelation import TravelRelation

# helper func
def get_travel_relations_count():
    return db.session.execute(db.select(func.count()).select_from(TravelRelation)).scalar()


def test_add_travel_relations(init_database):
    assert get_travel_relations_count() == 0

    travel = db.session.get(Travel, 1)
    assert len(travel.relations) == 0
    travel.relations.append(TravelRelation(relation='continent', relationFK=2))
    db.session.commit()
    assert len(travel.relations) == 1
    assert travel.relations[0].relation == 'continent' and travel.relations[0].relationFK == 2
    assert get_travel_relations_count() == 1

def test_remove_travel_relations(init_database):
    travel = db.session.get(Travel, 1)
    travel.relations.clear()
    db.session.commit()

    assert len(travel.relations) == 0
    assert get_travel_relations_count() == 0

def test_add_travel(flask_client):
    # simulate logged in normal user
    with flask_client.session_transaction() as session:
        session['user_id'] = 2

    # create a new travel
    date_ = date.fromisoformat('2025-01-01')
    data = dict(title='Travel 3', date_from=date_, date_to=date_, user_note='', description='', 
        public=True)
    data['relations[]'] = ['continent:2', 'country:2', 'country:3']
    response = flask_client.post('/travels/edit?travelID=', data=data, follow_redirects=True)
    assert 'data saved' in response.text

    new_travel = db.session.execute(db.select(Travel).where(Travel.title == 'Travel 3')).scalar()
    assert new_travel.title == 'Travel 3'
    assert new_travel.public == True
    assert len(new_travel.relations) == 3
    assert get_travel_relations_count() == 3

def test_relations_count_db_queries(query_counter):
    travel = db.session.get(Travel, 2)
    with query_counter() as counter: # pass True as argument to print queries
        rels = travel.get_relation_names()
    assert counter() == 3 # 1 to get travel.relations, 1 for all continents + 1 for all countries

def test_add_missing_date(flask_client):
    data = dict(title='Travel 3', date_to=date.fromisoformat('2025-01-01'), user_note='', 
        description='')
    response = flask_client.post('/travels/edit', data=data)
    assert 'dates are required' in response.text

def test_edit_invalid_date(flask_client):
    data = dict(id=2, title='Travel 3', date_from='Mar 23, 2000', date_to=date.fromisoformat('2025-01-01'), 
        user_note='', description='')
    response = flask_client.post('/travels/edit?travelID=2', data=data)
    assert 'Invalid date' in response.text


def test_edit_travel_ok(flask_client):
    date_ = date.fromisoformat('2000-12-12')
    data = dict(id=2, title='modified', date_from=date_, date_to=date_, user_note='', description='')
    response = flask_client.post('/travels/edit?travelID=2', data=data, follow_redirects=True)
    assert 'data saved' in response.text

    travel = db.session.get(Travel, 2)
    assert travel.date_from == date_
    assert travel.title == 'modified'
    assert travel.public == False

def test_list_travels(flask_client):
    response = flask_client.get('/travels')
    rows = response.text.count('<tr>')
    assert rows == 2 # thead>tr and his own travel just created

def test_zero_travelID_param(flask_client):
    response = flask_client.get('/travels/edit?travelID=0', follow_redirects=True)
    assert ': Home' in response.text

    # clear user from session
    with flask_client.session_transaction() as session:
        session.clear()

