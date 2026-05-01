import os
import pytest
import sqlite3
from datetime import date
from sqlalchemy import event
from sqlalchemy.engine import Engine
from web_travel import create_app, db
from instance.config import TestingConfig
from web_travel.models.Continent import Continent, FieldStatus
from web_travel.models.Country import Country
from web_travel.models.Place import Place
from web_travel.models.Travel import Travel
from web_travel.models.Photo import Photo


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

    # either cid or app_context needs to be provided, otherwise session.get call in model fires
    continent1 = Continent(name='South America', cid=1)
    continent2 = Continent(name='Africa', cid=1)
    db.session.add(continent1)
    db.session.add(continent2)

    country1 = Country(name='Bolivia', continentFK=1, cid=1)
    country2 = Country(name='Chad', continentFK=2, cid=1)
    country3 = Country(name='Sudan', continentFK=2, cid=1, status=FieldStatus.REJECTED)
    db.session.add_all([country1, country2, country3])

    place1 = Place(name='Hand of God', description='G', countryFK=2, cid=2, status=FieldStatus.ACTIVE)
    place2 = Place(name='place2', description='', countryFK=1, cid=2, status=FieldStatus.REJECTED, deleted=True)
    db.session.add_all([place1, place2])

    date_ = date.fromisoformat('2026-04-27')
    travel1 = Travel(title='Travel 1', description='', user_note='', date_from=date_, date_to=date_, 
        public=True, cid=1)
    db.session.add(travel1)

    photo1 = Photo(filename='photo1', extension='jpg', size=0, cid=2)
    photo2 = Photo(filename='photo1', extension='png', size=0, cid=2, public=True, status=FieldStatus.ACTIVE)
    db.session.add_all([photo1, photo2])

    db.session.commit()

    yield # pause point - testing happens here

    db.drop_all()


@pytest.fixture
def query_counter():
    return QueryCounter


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


class QueryCounter:
    """Context manager to count (and optionally print) SQLAlchemy queries."""
    def __init__(self, print_sql: bool = False):
        self._count = 0
        self._print_sql = print_sql

    def __enter__(self):
        event.listen(Engine, "before_cursor_execute", self.callback)
        return self

    def __exit__(self, *args, **kwargs):
        event.remove(Engine, "before_cursor_execute", self.callback)

    def callback(self, conn, cursor, statement, parameters, context, executemany):
        self._count += 1
        if self._print_sql:
            print(f'\n--- Query #{self._count} ---\n{statement}\nparams: {parameters}')

    def __call__(self):
        return self._count
