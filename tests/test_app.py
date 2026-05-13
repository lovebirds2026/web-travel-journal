# coverage run -m pytest
# coverage report
# flags -v -s (print) -k (function) --last-failed  --setup-show!! 
from sqlalchemy import desc
from flask_mail import Message
from pathlib import Path
from werkzeug.datastructures import FileStorage

from web_travel import db, mail
from instance.config import Config
from web_travel.models.Continent import Continent
from web_travel.models.Country import Country
from web_travel.models.Place import Place
from web_travel.models.Travel import Travel
from web_travel.models.Photo import Photo
from web_travel.utils import allowed_photo_ext, save_photo

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

def test_travel_table_exists(init_database):
    prepopulated_travel = db.session.scalar(db.select(Travel).order_by(desc('id')))
    assert prepopulated_travel is not None
    assert prepopulated_travel.title == 'Travel 1'

def test_photo_table_exists(init_database):
    prepopulated_photo = db.session.scalar(db.select(Photo).order_by(desc('id')))
    assert prepopulated_photo is not None
    assert prepopulated_photo.filename == 'photo1'
    assert prepopulated_photo.extension == 'png'

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

def test_upload_image(flask_client):
    upload_path = Path(Config.UPLOAD_FOLDER_PHOTOS)
    assert upload_path.is_dir()

    thumb_path = Path(Config.UPLOAD_FOLDER_THUMBS)
    assert thumb_path.is_dir()

    assets_folder = Path(__file__).parent / 'assets'
    test_file_fail = assets_folder / 'testpdf.pdf'
    with open(test_file_fail, 'rb') as fp:
        file = FileStorage(fp)
    assert allowed_photo_ext(file.filename) == False
    assert not save_photo(file)

    test_file_ok = assets_folder / 'screen.png'
    with open(test_file_ok, 'rb') as fp:
        file = FileStorage(fp)
        result = save_photo(file)
        assert result.path and result.size > 0

    # clean up
    (upload_path / result.path).unlink()
    (thumb_path / result.path).unlink()
