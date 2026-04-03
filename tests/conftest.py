import os
import pytest
import sqlite3
from sqlalchemy import text
from web_travel import create_app, db
from instance.config import TestingConfig


@pytest.fixture(scope='session')
def flask_client():
    create_users_table()
    flask_app = create_app(test_app=True)
    # hack fix for SQLAlchemy not trusting autoincrement on SQLite reflected tables
    db.metadata.tables['user'].c.id.nullable = False

    # NB: this can be structured in another way, like return app + return client
    # and separate 'with' blocks for each where needed. Not sure which is better
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            # the with block is suspended and active in the tests!
            yield testing_client


# workaround for not having to deferred import reflected User model in each test function
@pytest.fixture(scope='session')
def User(flask_client):
    from web_travel.models.User import User # the good ole' deferred import trick
    return User


@pytest.fixture(scope='session')
def init_database(User):
    db.create_all()

    user1 = User(email='patkennedy79o_o_@gmail.com', password='x', username='Kori', is_admin=True)
    user2 = User(email='bali234451234556@gmail.com', password='z', username='Bali')
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    yield # pause point - testing happens here

    db.drop_all()


def create_users_table():
    # this table exists already and is reflected in the app, need to create it manually
    sql_stmts = [
        "DROP TABLE IF EXISTS user;",

        """CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE,
        password TEXT NOT NULL,
        full_name TEXT,
        is_admin INTEGER DEFAULT 0,
        cid INTEGER,
        ct DATE,
        uid INTEGER,
        ut DATE,
        deleted INTEGER DEFAULT 0,
        active INTEGER DEFAULT 0
        );""",

        # "INSERT INTO user (email, password, username) VALUES ('sadi@email.eamil.lo', 'x', 'Testy')",
    ]

    conn = sqlite3.connect(TestingConfig.SQLALCHEMY_DATABASE_URI.split('///')[1])    
    c = conn.cursor()
    try:
        for sql_stmt in sql_stmts:
            c.execute(sql_stmt)
        conn.commit()
    finally:
        conn.close()

