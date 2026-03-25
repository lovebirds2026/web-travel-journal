# Write a unit test that generates a confirmation token for a user and that 
# tests whether or not the user in question can be confirmed successfully.

# flags -v -s (print) -k (function) --last-failed  --setup-show!! 

from web_travel import db

def test_user_table_exists(User, init_database):
    prepopulated_user = db.session.scalar(db.select(User))
    assert prepopulated_user.username == 'Kori'
    assert prepopulated_user.email == 'patkennedy79o_o_@gmail.com'
    #assert prepopulated_user.password != 'x'

