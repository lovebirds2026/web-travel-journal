from flask import current_app, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message

from .. import db, mail
from ..utils import create_token, decode_token, check_email_input

# define tables with ORM here
#print(db.metadata) # empty at this point

class Base(db.Model):
    __abstract__ = True

    def xx(self):
        return 'xx -- xx'


class User(Base):
    __table__ = db.metadata.tables['user']

    searchable_fields = ('id', 'username', 'email', 'full_name', )

    def __repr__(self):
        return f'User {self.username} with email {self.email} .'

    def __init__(self, **kwargs):
        kwargs['password'] = self.hash_password(kwargs['password'])
        super().__init__(**kwargs)

    def set_password(self, password_plaintext):
        self.password = self.hash_password(password_plaintext)

    def check_password(self, password_plaintext):
        return check_password_hash(self.password, password_plaintext)

    # these may need to be moved out to a service layer
    def send_email_confirmation_link(self):
        token = create_token({'user_id': self.id}, 60 * 60)
        link = url_for('auth.confirm_email', _external=True, t=token)
        msg = Message(
            'Travel Journal account email confirmation',
            sender='office@ai-me.bg',
            recipients=[self.email],
            html='Click here to confirm your email at Travel Journal:</br> '
                f'<a href="{link}" target="_blank">{link}</a> '
        )
        try:
            mail.send(msg)
        except Exception as e: # The mail server could not deliver mail etc.
            current_app.logger.warning(e)
            return False
        return True

    def send_reset_password_link(self):
        token = create_token({'user_id': self.id}, 30 * 60) # 30min expiration
        link = url_for('auth.reset_password', _external=True, t=token)
        msg = Message(
            'Travel Journal reset password link',
            sender='office@ai-me.bg',
            recipients=[self.email],
            html='Click here to reset your password at Travel Journal:</br> '
                'This link will be valid for 30 minutes.</br> '
                f'<a href="{link}" target="_blank">{link}</a> '
        )
        mail.send(msg)

    @classmethod
    def create(cls, form_data) -> tuple:
        errors = []
        required_fields = ['username', 'email', 'password', 'password2']
        for field in required_fields:
            if value := form_data.get(field):
                if field == 'email' and not check_email_input(value):
                    errors.append('Invalid email format.')
                if field == 'password' and value != form_data.get('password2'):
                    errors.append('Passwords do not match')
            else:
                errors.append(f'{field.capitalize()} is required')

        user = None
        if not errors:
            required_fields[-1] = 'full_name'
            values = {key: form_data.get(key) for key in required_fields}
            user = cls(**values)
        return errors, user

    @staticmethod
    def hash_password(password_plaintext):
        return generate_password_hash(password_plaintext)


# class Continent(Base):
#     ...



# db.create_all()