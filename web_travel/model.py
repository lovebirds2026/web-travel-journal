from . import db

# define tables with ORM here
#print(db.metadata) # empty at this point

class User(db.Model):
    __table__ = db.metadata.tables['user']

    def __repr__(self):
        return f'User {self.username} with email {self.email} .'