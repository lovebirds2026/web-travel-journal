from web_travel import db

# general unit tests - move to test_app
def test_continent_table_exists(User, init_database):
    prepopulated_user = db.session.scalar(db.select(User).where(User.username == 'Kori'))
    assert prepopulated_user is not None
    assert prepopulated_user.password != 'x' # password has been hashed

def test_select_one_continent_by_search_field_id():
    ...

# @TODO add records in conftest
# test admin access