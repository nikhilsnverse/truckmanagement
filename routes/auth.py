from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from database import db

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter email and password.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['role'] = user.role

        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('dashboard.index'))

    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
