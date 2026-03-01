import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text
from flask_mail import Message

from . import db, mail
from .model import User

bluepr = Blueprint('auth', __name__, url_prefix='/auth')

@bluepr.route('/') # , methods=['GET', 'POST']
def test():
    res = db.session.execute(text('SELECT * FROM public.user')).all()

    stmt = db.select(User)
    res1 = db.session.execute(stmt).scalars().first()
    #print(vars(res1))
    return f'Module {__name__}: OK, found user {res[0][:5]}'

# http://127.0.0.1:5000/auth/register?username=dar&password=xx
@bluepr.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username: error = 'Username is required'
        if not password: error = 'Password is required'

        if error is None:
            try:
                new_user = User(username=username, password=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()
            except db.IntegrityError:
                error = f'User {username} already exists.'
            else:
                flash(f'User {new_user.username} successfully created. You can now login')
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bluepr.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        stmt = db.select(User).where(User.username == username)
        user = db.session.execute(stmt).scalar_one()
        print(user)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bluepr.route('/forgot', methods=('GET', 'POST'))
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        error = None

        stmt = db.select(User).where(User.email == email)
        user = db.session.scalar(stmt)
        print(user)

        if user is not None:
            ...
            # msg = Message(
            #     'Web Travel password reset link',
            #     recipients=[recipient],
            #     body=body # or html=..
            # )
            # mail.send(msg)

    return render_template('auth/resetpassword.html')


# registers a function that runs before the view function, no matter what URL is requested.
@bluepr.before_app_request # Note: I would just save the whole user in the session
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)


@bluepr.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# utility decorator to require logged in user
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view