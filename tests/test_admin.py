from flask import session

def test_users_list_missing_admin_access(flask_client):
    response = flask_client.get('/admin/users/list')
    assert response.status_code == 302 # FOUND -> redirected to index


def test_users_list(flask_client, init_database):
    with flask_client.session_transaction() as session:
        session['user_id'] = 1

    response = flask_client.get('/admin/users/list')
    assert response.status_code == 200
    assert 'Admin: Users list' in response.text

    with flask_client.session_transaction() as session:
        session.clear()

