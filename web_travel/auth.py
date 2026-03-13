import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text, exc
from flask_mail import Message

from . import db, mail
from .model import User
from .utils import create_token, decode_token, check_email_input

bluepr = Blueprint('auth', __name__, url_prefix='/auth')

@bluepr.route('/')
def test():
    res = db.session.execute(text('SELECT * FROM public.user')).all()

    stmt = db.select(User)
    res1 = db.session.scalar(stmt) # scalar = execute + scalars + first
    #print(vars(res1))
    return f'Module {__name__}: OK, found user {res[0][:3]}'


@bluepr.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        errors = []

        if not username: errors.append('Username is required')
        if not email: errors.append('Email is required')
        elif not check_email_input(email): errors.append('Invalid email format.')
        if not password: errors.append('Password is required')
        if password != password2: errors.append('Passwords do not match')

        if not errors:
            try:
                new_user = User(username=username, password=generate_password_hash(password),
                    email=email, full_name=full_name)
                db.session.add(new_user)
                db.session.commit()
            except db.exc.IntegrityError:
                errors.append(f'User with email {email} already exists.')
            else:
                flash(f'User {new_user.username} successfully created. '
                    'You can login after you verify your email.')
                # send email confirmation link
                token = create_token({'user_id': new_user.id}, 3600)
                link = url_for('auth.confirm_email', _external=True, t=token)
                msg = Message(
                    'Web Travel account email confirmation',
                    sender='office@ai-me.bg',
                    recipients=[new_user.email],
                    html='Click here to confirm your email at Web Travel:</br> '
                        f'<a href="{link}" target="_blank">{link}</a> '
                )
                mail.send(msg)
                return redirect(url_for('auth.login'))

        [flash(msg, 'error') for msg in errors]

    return render_template('auth/register.html', form=request.form)


@bluepr.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        stmt = db.select(User).where(User.email == email)
        user = db.session.scalars(stmt).one_or_none() # .scalar_one_or_none()

        if user is None:
            error = 'Invalid email.'
        elif not user.active:
            error = 'You must confirm your email first by clicking on the link sent to you when registering.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id # atob(session.split('.')[0]) in browser console
            session['is_admin'] = user.is_admin
            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template('auth/login.html', form=request.form)


@bluepr.route('/forgot', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        error = None

        stmt = db.select(User).where(User.email == email)
        user = db.session.scalar(stmt)
        print(user)

        if user is not None:
            print('-- sending email..')
            # msg = Message(
            #     'Web Travel password reset link',
            #     sender='office@ai-me.bg',
            #     recipients=[email],
            #     body='token here' # or html=..
            # )
            # mail.send(msg)
            # print('-- email sent.')

    return render_template('auth/resetpassword.html')


@bluepr.route('/confirm/<t>', methods=['GET'])
def confirm_email(t):
    if token := decode_token(t):
        user = db.get_or_404(User, token['user_id'])
        user.active = True
        db.session.commit()
        flash('Email successfully confirmed. You can now login.')

    return redirect(url_for('auth.login'))


@bluepr.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# registers a function that runs before the view function, no matter what URL is requested.
@bluepr.before_app_request # Note: I would just save the whole user in the session
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)


# utility decorator to require logged in user
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view

# utility decorator to require logged in admin
def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or not g.user.is_admin:
            return redirect(url_for('index'))
        return view(**kwargs)

    return wrapped_view