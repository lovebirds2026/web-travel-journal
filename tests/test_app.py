# flags -v -s (print) -k (function) --last-failed  --setup-show!! 

from web_travel import db

# general unit tests
def test_user_table_exists(User, init_database):
    prepopulated_user = db.session.scalar(db.select(User).where(User.username == 'Kori'))
    assert prepopulated_user is not None
    assert prepopulated_user.password != 'x' # password has been hashed

