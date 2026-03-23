from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
from werkzeug.security import generate_password_hash

from .. import db
from ..models.User import User
from .auth import login_required

bluepr = Blueprint('main', __name__) # web_travel.routes

@bluepr.route('/')
def index():
    header = 'Lovebirds® 2026 Dev domain on Flask 3.1.2 running on Python 3.13'
    return render_template('base.html', title='Homepage', header=header)


@bluepr.route('/user', methods=['GET', 'POST'])
@login_required
def user_account():
    if request.method == 'POST':
        g.user.full_name = request.form['full_name']
        password = request.form['password']
        password2 = request.form['password2']
        error = None

        if len(password) > 0: # user wants to update their password
            if password != password2:
                error = 'Passwords do not match.'
            else:
                g.user.password = generate_password_hash(password)

        if not error:
            db.session.commit()
            flash('Changes saved.')
        else:
            flash(error, 'error')

    return render_template('main/user.html')

