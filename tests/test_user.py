from web_travel import db
from web_travel.utils import create_token
from flask import session, g

# integration tests
def test_index(flask_client):
    response = flask_client.get('/')
    assert response.status_code == 200
    assert 'Home' in response.text and 'Web Travel' in response.text


def test_register_incorrect_data(flask_client):
    base_data = {
        'username': 'testy0',
        'email': 'office@ai-me.bg',
        'password': 'password',
        'password2': 'password',
    }
    print(g.user)
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
        'password2': password,
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
    response = flask_client.post('/auth/login', follow_redirects=True,
        data={'email': 'office@ai-me.bg', 'password': ' '})
    assert response.request.path == '/auth/login'
    assert session.get('user_id') is None


def test_reset_password(flask_client, User, init_database):
    user = db.session.scalar(db.select(User).where(User.username == 'Bali'))
    assert user is not None
    token = create_token({'user_id': user.id}, 30 * 60)

    new_pass = '  '
    response = flask_client.post(f'auth/reset-password?t={token}', data={
        'password': new_pass,
        'password2': new_pass,
    }, follow_redirects=True)
    assert user.check_password(new_pass)
    assert 'Password changed successfully' in response.text


def test_disallowed_login_register_when_logged(flask_client, init_database):
    # accessing/setting a value in the session BEFORE making a request
    with flask_client.session_transaction() as session:
        session['user_id'] = 1 # set a user id without going through the login route

    response = flask_client.get('/auth/login', follow_redirects=True)
    assert response.request.path == '/'

    response2 = flask_client.get('/auth/register', follow_redirects=True)
    assert response2.request.path == '/'


def test_change_user_details(flask_client, User, init_database):
    with flask_client.session_transaction() as session:
        session['user_id'] = 1

    response_get = flask_client.get('/user')
    assert 'User account management' in response_get.text

    new_pass = '_'
    response_post = flask_client.post('/user', data={
        'full_name': 'Changed_full_name',
        'password': new_pass,
        'password2': new_pass,
    })
    assert 'Changes saved' in response_post.text

    user = db.session.get(User, 1)
    assert user.check_password(new_pass)

    with flask_client.session_transaction() as session:
        session.clear()

