from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import owner_required
from models.user import User
from database import db

owner_bp = Blueprint('owner', __name__, template_folder='../templates')


@owner_bp.route('/users')
@owner_required
def manage_drivers():
    users = User.query.filter(User.role.in_(['manager', 'driver'])).order_by(User.created_at.desc()).all()
    return render_template('drivers/list.html', users=users)


@owner_bp.route('/users/add', methods=['POST'])
@owner_required
def add_user():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'driver')
    phone = request.form.get('phone', '').strip()

    if not name or not email or not password:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('owner.manage_drivers'))

    existing = User.query.filter_by(email=email).first()
    if existing:
        flash('Email already registered.', 'danger')
        return redirect(url_for('owner.manage_drivers'))

    user = User(name=name, email=email, role=role, phone=phone or None)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash(f'{role.title()} "{name}" created successfully!', 'success')
    return redirect(url_for('owner.manage_drivers'))


@owner_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@owner_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'owner':
        flash('Cannot delete owner account.', 'danger')
        return redirect(url_for('owner.manage_drivers'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.name}" deleted.', 'success')
    return redirect(url_for('owner.manage_drivers'))
