from flask import Blueprint, flash, g, render_template, request, session, make_response

from .. import db
from ..models.User import User
from .auth import login_required

bluepr = Blueprint('main', __name__) # web_travel.routes

@bluepr.route('/')
def index():
    return render_template('main/index.html', title='Home')


@bluepr.route('/travels')
def travels():
    return render_template('main/travels.html')


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
                g.user.set_password(password)

        if not error:
            db.session.commit()
            flash('Changes saved.')
        else:
            flash(error, 'error')

    return render_template('main/user.html')

