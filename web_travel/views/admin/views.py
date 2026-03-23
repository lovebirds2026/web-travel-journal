from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import update, cast, String

from ... import db
from ...models.User import User
from web_travel.views.admin import bluepr
from ...utils import check_email_input
from ..auth import admin_required

@bluepr.route('/users/list', methods=['GET'])# ?del=<int>
@admin_required
def list_users():
    if request.args.get('del'):
        user_id = request.args.get('del')
        user = db.get_or_404(User, user_id)
        user.deleted = not user.deleted
        db.session.commit()
        flash(f'User {user.username} status changed to {"deleted" if user.deleted else "active"}.')

    # Dropdown boolean filters
    filters = {}
    is_admin = request.args.get('is_admin')
    if is_admin:
        filters['is_admin'] = is_admin == '1' # WOW!
    deleted = request.args.get('deleted')
    if deleted:
        filters['deleted'] = deleted == '1'
    stmt = db.select(User).filter_by(**filters).order_by(User.id)

    # Text search in field
    search_text = request.args.get('search_text')
    search_field = request.args.get('search_field')
    if search_text and search_field and search_field in User.searchable_fields:
        user_field = cast(getattr(User, search_field), String) # to make id searchable
        stmt = stmt.where(user_field.icontains(search_text))

    users = db.session.scalars(stmt).all()
    return render_template('admin/users_list.html', users=users)


@bluepr.route('/users/edit', methods=['GET', 'POST']) # ?userID=<int>
@admin_required
def edit_user():
    if request.method == 'POST':
        email = request.form.get('email')
        if not check_email_input(email):
            flash('Invalid email format.', 'error')
        else:
            update_dict = dict(
                username=request.form.get('username'),
                email=email,
                full_name=request.form.get('full_name'),
                active=bool(request.form.get('active')),
                is_admin=bool(request.form.get('is_admin')),
                deleted=bool(request.form.get('deleted')),
            )
            stmt = update(User).where(User.id == request.form['id']).values(update_dict)
            result = db.session.execute(stmt)
            db.session.commit()
            if result.rowcount:
                flash('User data updated.')

    user_id = request.args.get('userID')
    if not user_id:
        return redirect(url_for('admin.list_users'))
    user = db.get_or_404(User, user_id)

    return render_template('admin/users_edit.html', user=user)
