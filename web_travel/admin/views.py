from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import update

from .. import db
from .. model import User
from web_travel.admin import bluepr
from .. auth import admin_required

@bluepr.route('/users/list', methods=['GET'])# ?del=<int>
@admin_required
def list_users():
    if request.args.get('del'):
        user_id = request.args.get('del')
        user = db.get_or_404(User, user_id)
        user.deleted = not user.deleted
        db.session.commit()
        flash(f'User {user.username} status changed to {"deleted" if user.deleted else "active"}.')

    stmt = db.select(User).order_by(User.id)
    users = db.session.scalars(stmt).all()

    return render_template('admin/users_list.html', users=users)


@bluepr.route('/users/edit', methods=['GET', 'POST']) # ?userID=<int>
@admin_required
def edit_user():
    if request.method == 'POST':
        update_dict = dict(
            full_name=request.form.get('full_name'),
            active=bool(request.form.get('active')),
            is_admin=bool(request.form.get('is_admin')),
            deleted=bool(request.form.get('deleted')),
        )
        if update_dict:
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
