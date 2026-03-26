from werkzeug.security import check_password_hash, generate_password_hash

from .. import db

# define tables with ORM here
#print(db.metadata) # empty at this point

class User(db.Model):
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

    @staticmethod
    def hash_password(password_plaintext):
        return generate_password_hash(password_plaintext)



# class Continent(db.Model):
#     ...



# db.create_all()