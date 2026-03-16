from flask import render_template, request, flash

from .. import db
from .. model import User
from web_travel.admin import bluepr
from .. auth import admin_required

@bluepr.route('/users/list', methods=['GET'])
@admin_required
def list_users():
    if request.args.get('del'):
        user_id = request.args.get('del')
        user = db.get_or_404(User, user_id)
        user.deleted = not user.deleted
        db.session.commit()
        flash(f'User {user.username} status changed to {user.active}.')

    stmt = db.select(User).order_by(User.id)
    users = db.session.scalars(stmt).all()

    return render_template('admin/users_list.html', users=users)

