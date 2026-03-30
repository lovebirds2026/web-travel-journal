# flags -v -s (print) -k (function) --last-failed  --setup-show!! 
from flask_mail import Message

from web_travel import db, mail
from instance.config import Config

# general unit tests
def test_user_table_exists(User, init_database):
    prepopulated_user = db.session.scalar(db.select(User).where(User.username == 'Kori'))
    assert prepopulated_user is not None
    assert prepopulated_user.password != 'x' # password has been hashed

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
