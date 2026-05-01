# Web Travel Journal

A Flask + SQLAlchemy project I built during my Python web development study.  
[Travel Journal](https://travel.aime.bg) is a full CRUD app with auth, admin area, relational tagging, photo uploads and tests.

## Features

- User registration, login, logout
- Email confirmation + password reset via token links
- Role-based access
- Manage continents, countries, places, travels, and photos
- Attach relation tags across entities (for example: photo -> country/place/travel)
- Visibility and moderation flow (`new`, `active`, `rejected`, `deleted`)

## Tech stack

- Python 3.13
- Flask
- Flask-SQLAlchemy (SQLAlchemy 2 ORM-style)
- Flask-Mail
- JWT (`pyjwt`)
- Jinja templates + light vanilla JS
- Pytest/Coverage
- Jira with a dedicated Project Lead

## Quietly technical parts I am proud of

- Reusable model design:
  - shared `Base` model with common fields/audit-ish columns
  - generic search/filter helper
  - relation mixin used by both `Travel` and `Photo`
- Relation modeling with constraints and indexes:
  - unique constraints to avoid duplicate relation rows
  - enum-backed relation types + status fields
  - targeted indexes on filtering columns
- Access control beyond route-level checks:
  - decorators for guest/login/admin flows
  - ownership checks in edit/update flows
- Upload and moderation flow:
  - extension validation + safe filenames + timestamp strategy
  - per-item public/hidden switch + admin status transitions
- Performance awareness while still learning:
  - explicit `selectinload(...)` where relation loading matters
  - a custom query counter utility in tests for inspection
- Testing setup:
  - fixtures for bootstrapping app/db state
  - focused tests for auth, admin access, and core entities

## What I learned building this

- How to structure a Flask app with blueprints and keep routes manageable
- How to model many-to-many-like relation tables in SQLAlchemy without overcomplicating it
- Where ORM convenience is great, and where explicit SQLAlchemy statements are cleaner
- How much security matters even in a learning project (password hashing, token expiry, file checks)
- How tests expose design issues early (especially around sessions, auth, and DB setup)

## What I would improve next

- Add migrations (Alembic) instead of using the `reflect() + create_all()` flow
- Improve API functionality with a Service layer to streamline some route functions
- Introduce a proper UI/UX all around the site :-()

## File Structure
.
|-- .coverage
|-- LICENSE
|-- README.md
|-- instance
|   |-- config.py
|   `-- test.db
|-- pyproject.toml
|-- tests
|   |-- conftest.py
|   |-- test_admin.py
|   |-- test_app.py
|   |-- test_continent.py
|   |-- test_country.py
|   |-- test_place.py
|   |-- test_photo.py
|   |-- test_travel.py
|   `-- test_user.py
`-- web_travel
    |-- __init__.py
    |-- logs
    |   `-- logfile.log
    |-- static
    |   |-- lovebirds_ico.ico
    |   `-- water-light.css
    |-- models
    |   |-- __init__.py
    |   |-- Continent.py
    |   |-- Country.py
    |   |-- Photo.py
    |   |-- PhotoRelation.py
    |   |-- Place.py
    |   |-- Travel.py
    |   |-- TravelRelation.py
    |   `-- User.py
    |-- views
    |   |-- __init__.py
    |   |-- admin
    |   |   |-- __init__.py
    |   |   |-- continents.py
    |   |   |-- countries.py
    |   |   `-- users.py
    |   |-- auth.py
    |   `-- routes.py
    |-- templates
    |   |-- base.html
    |   |-- admin
    |   |   |-- continents_edit.html
    |   |   |-- continents_list.html
    |   |   |-- countries_edit.html
    |   |   |-- countries_list.html
    |   |   |-- users_edit.html
    |   |   `-- users_list.html
    |   |-- auth
    |   |   |-- login.html
    |   |   |-- register.html
    |   |   |-- requestpasswordreset.html
    |   |   `-- resetpassword.html
    |   |-- main
    |   |   |-- index.html
    |   |   |-- photos.html
    |   |   |-- photos_edit.html
    |   |   |-- places.html
    |   |   |-- places_edit.html
    |   |   |-- travels.html
    |   |   |-- travels_edit.html
    |   |   `-- user.html
    |   `-- snippets
    |       `-- relations.html
    |-- utils.py
    `-- wsgi.py