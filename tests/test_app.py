# coverage run -m pytest | coverage report
# flags -v -s (print) -k (function) --last-failed  --setup-show!! 
from sqlalchemy import desc
from flask_mail import Message

from web_travel import db, mail
from instance.config import Config
from web_travel.models.Continent import Continent
from web_travel.models.Country import Country
from web_travel.models.Place import Place

# general unit tests
def test_index(flask_client):
    response = flask_client.get('/')
    assert response.status_code == 200
    assert 'Home' in response.text and 'Web Travel' in response.text

def test_user_table_exists(User, init_database):
    prepopulated_user = db.session.scalar(db.select(User).where(User.username == 'Kori'))
    assert prepopulated_user is not None
    assert prepopulated_user.password != 'x' # password has been hashed

def test_continent_table_exists(init_database):
    prepopulated_continent = db.session.scalar(db.select(Continent))
    assert prepopulated_continent is not None
    assert prepopulated_continent.name == 'South America'

def test_country_table_exists(init_database):
    prepopulated_country = db.session.scalar(db.select(Country))
    assert prepopulated_country is not None
    assert prepopulated_country.name == 'Bolivia'

def test_place_table_exists(init_database):
    prepopulated_place = db.session.scalar(db.select(Place).order_by(desc('id')))
    assert prepopulated_place is not None
    assert prepopulated_place.name == 'place2'

def test_server_name_in_email():
    deployment_suffix = '' if Config.SERVER_NAME == 'travel.aime.bg' else ' [DEV]'

    with mail.record_messages() as outbox:
        msg = Message(
            'Subject' + deployment_suffix,
            sender=['Travel Journal' + deployment_suffix, 'office@ai-me.bg'],
            recipients=['office@ai-me.bg'],
            body='Pytest email dev server suffix'
        )
        mail.send(msg)
        assert outbox[0].subject.endswith('[DEV]')
