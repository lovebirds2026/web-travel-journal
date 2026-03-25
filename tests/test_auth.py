from web_travel import db
from flask import session

# route tests
def test_index(flask_client):
    response = flask_client.get('/')
    assert response.status_code == 200
    assert 'Home' in response.text
    assert 'Web Travel' in response.text

def test_user_table_exists(User, init_database):
    prepopulated_user = db.session.scalar(db.select(User))
    assert prepopulated_user.username == 'Kori'
    assert prepopulated_user.email == 'patkennedy79o_o_@gmail.com'
    #assert prepopulated_user.password != 'x'


def test_register_incorrect_data(flask_client):
    base_data = {
        'username': 'testy1',
        'email': 'office@ai-me.bg',
        'password': 'password',
        'password2': 'password',
    }

    # missing username
    data = dict(base_data)
    data['username'] = ''
    response = flask_client.post('/auth/register', data=data, follow_redirects=True)
    assert response.request.path == '/auth/register'
    assert 'is required' in response.text

    # invalid email
    data = dict(base_data)
    data['email'] = 'x@who.'
    response = flask_client.post('/auth/register', data=data, follow_redirects=True)
    assert response.request.path == '/auth/register'
    assert 'Invalid email' in response.text

    # missing password
    data = dict(base_data)
    data['password'] = data['password2'] = ''
    response = flask_client.post('/auth/register', data=data, follow_redirects=True)
    assert response.request.path == '/auth/register'
    assert 'is required' in response.text

    # different passwords
    data = dict(base_data)
    data['password2'] += '_added'
    response = flask_client.post('/auth/register', data=data, follow_redirects=True)
    assert response.request.path == '/auth/register'
    assert 'do not match' in response.text


def test_register_emailconf_login(flask_client):
    email, password = 'office@ai-me.bg', 'password'
    response_register = flask_client.post('/auth/register', follow_redirects=True, data={
        'username': 'testy1',
        'full_name': 'Full Name T',
        'email': email,
        'password': password,
        'password2': 'password',
    })
    assert response_register.status_code == 200
    token = response_register.json['token'] # register returns the token if app.testing=True
    
    # try logging in and failing
    response_login_fail = flask_client.post('/auth/login', follow_redirects=True,
        data={'email': email, 'password': password})
    assert response_login_fail.request.path == '/auth/login'
    assert 'confirm your email first' in response_login_fail.text
    assert session.get('user_id') is None

    # confirm email
    response_confirm_email = flask_client.get(f'/auth/confirm/{token}', follow_redirects=True)
    assert response_confirm_email.request.path == '/auth/login'
    assert 'confirmed' in response_confirm_email.text

    # login
    response_login = flask_client.post('/auth/login', follow_redirects=True,
        data={'email': email, 'password': password})
    assert response_login.request.path == '/'
    assert session.get('user_id') is not None

    # logout
    response_logout = flask_client.get('/auth/logout', follow_redirects=True)
    assert response_logout.request.path == '/auth/login'
    assert session.get('user_id') is None


def test_login_fail(flask_client):
    pass
