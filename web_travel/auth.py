import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text

from . import db

bluepr = Blueprint('auth', __name__, url_prefix='/auth')

@bluepr.route('/') # , methods=['GET', 'POST']
def test():
    res = db.session.execute(text('SELECT * FROM public.user')).all()
    print(res[0][:5])

    return f'test OK {res[0][:5]}'