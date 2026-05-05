from flask import session
from sqlalchemy.orm import joinedload

from web_travel import db
from web_travel.models.Photo import Photo
from web_travel.models.PhotoRelation import PhotoRelation

def test_add_photo_relations(init_database):
    photo = db.session.get(Photo, 1)
    assert len(photo.relations) == 0
    photo.relations.extend([
        PhotoRelation(relation='continent', relationFK=2),
        PhotoRelation(relation='travel', relationFK=1),
    ])
    db.session.commit()
    assert len(photo.relations) == 2

def test_photos_list(flask_client):
    # simulate logged in normal user
    with flask_client.session_transaction() as session:
        session['user_id'] = 2

    response = flask_client.get('/photos')
    assert 'Africa' in response.text
    assert 'Travel 1' in response.text

def test_photos_http_edit_relations(flask_client):
    data = {
        'photo_id': '1',
        'relations[]': ['continent:1'],
    }
    response = flask_client.post('/photos', data=data)
    assert 'Photo updated' in response.text
    assert 'Africa' not in response.text
    assert 'Travel 1' not in response.text
    assert 'South America' in response.text

    # clear user from session
    with flask_client.session_transaction() as session:
        session.clear()

