import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from .. import db
from ..models.User import User
from ..utils import decode_token

bluepr = Blueprint('auth', __name__, url_prefix='/auth')

# utility decorator to require NOT logged in user
def guest_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None:
            return redirect(url_for('public.index'))
        return view(**kwargs)

    return wrapped_view

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
            return redirect(url_for('public.index'))
        return view(**kwargs)

    return wrapped_view


# routes
@bluepr.route('/register', methods=['GET', 'POST'])
@guest_required
def register():
    if request.method == 'POST':
        errors, new_user = User.create(request.form)
        if not errors:
            try:
                db.session.add(new_user)
                db.session.commit()
            except db.exc.IntegrityError:
                errors.append(f'User with email {new_user.email} already exists.')
            else:
                if email_sent := new_user.send_email_confirmation_link():
                    flash(f'User {new_user.username} successfully created. '
                        'You can login after you verify your email.')
                    return redirect(url_for('auth.login'))

                errors.append(f'We could not send an email to {new_user.email}. '
                    'Please contact the site administrator for more information on '
                    'resolving the issue.', 'error')
        for msg in errors:
            flash(msg, 'error')

    return render_template('auth/register.html', form=request.form)


@bluepr.route('/confirm/<t>', methods=['GET'])
def confirm_email(t):
    if token := decode_token(t):
        user = db.get_or_404(User, token['user_id'])
        user.active = True
        db.session.commit()
        flash('Email successfully confirmed. You can now login.')

    return redirect(url_for('auth.login'))


@bluepr.route('/login', methods=['GET', 'POST'])
@guest_required
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
        elif user.deleted:
            error = 'This account is inactive. Please contact the site admins at office@ai-me.bg for details.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id # atob(session.split('.')[0]) in browser console
            session['is_admin'] = user.is_admin
            return redirect(url_for('public.index'))

        flash(error, 'error')

    return render_template('auth/login.html', form=request.form)


@bluepr.route('/forgot', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        email = request.form['email']
        stmt = db.select(User).where(User.email == email)
        user = db.session.scalar(stmt)

        if user is not None:
            user.send_reset_password_link()
        flash('You will receive an email reset link if you are registered with this address.')
    return render_template('auth/requestpasswordreset.html')


@bluepr.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token_param = request.args.get('t')
    if token_param:
        token = decode_token(token_param)
    if not token_param or not token:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        password = request.form['password']
        password2 = request.form['password2']
        error = None

        if not password or not password2:
            error = 'Both Password fields are required'
        elif password != password2:
            error = 'Passwords do not match'

        if not error:
            user = db.session.get(User, token['user_id'])
            user.set_password(password)
            db.session.commit()
            flash('Password changed successfully. You can now login.')
            return redirect(url_for('auth.login'))

        flash(error, 'error')

    return render_template('auth/resetpassword.html')


@bluepr.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# registers a function that runs before the view function, no matter what URL is requested.
@bluepr.before_app_request
def load_logged_in_user():
    session['last_url'] = request.full_path # experimental
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)


@bluepr.after_app_request
def add_cache_headers(response):
    match response.mimetype:
        case 'text/html': max_age = 3600
        case 'text/css': max_age = 3600 * 24
        case _: max_age = 3600 * 24 * 30
    response.cache_control.no_cache = False
    response.cache_control.max_age = max_age
    return response