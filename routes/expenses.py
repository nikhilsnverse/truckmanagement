from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, manager_required, owner_required, role_required
from models.expense import Expense
from models.trip import Trip
from database import db
from utils.helpers import save_file

expenses_bp = Blueprint('expenses', __name__, template_folder='../templates')


@expenses_bp.route('/')
@manager_required
def list_expenses():
    role = session.get('role')
    query = Expense.query

    type_filter = request.args.get('type', '')
    if type_filter:
        query = query.filter_by(type=type_filter)

    approved_filter = request.args.get('approved', '')
    if approved_filter == 'pending':
        query = query.filter_by(approved=False)
    elif approved_filter == 'approved':
        query = query.filter_by(approved=True)

    expenses = query.order_by(Expense.created_at.desc()).all()
    return render_template('expenses/list.html', expenses=expenses,
                           type_filter=type_filter, approved_filter=approved_filter, role=role)


@expenses_bp.route('/add/<int:trip_id>', methods=['GET', 'POST'])
@manager_required
def add_expense(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if request.method == 'POST':
        exp_type = request.form.get('type', '').strip()
        amount = request.form.get('amount', '').strip()
        description = request.form.get('description', '').strip()
        bill_image = None

        if 'bill_image' in request.files:
            file = request.files['bill_image']
            if file and file.filename:
                bill_image = save_file(file)

        if not exp_type or not amount:
            flash('Please fill in required fields.', 'danger')
            return render_template('expenses/form.html', trip=trip, expense=None)

        expense = Expense(
            trip_id=trip.id,
            type=exp_type,
            amount=float(amount),
            description=description,
            bill_image=bill_image,
            approved=False
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('trips.list_trips'))

    return render_template('expenses/form.html', trip=trip, expense=None)


@expenses_bp.route('/approve/<int:expense_id>', methods=['POST'])
@owner_required
def approve_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    expense.approved = True
    expense.approved_by = session.get('user_id')
    db.session.commit()
    flash('Expense approved!', 'success')
    return redirect(url_for('expenses.list_expenses'))


@expenses_bp.route('/delete/<int:expense_id>', methods=['POST'])
@manager_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('expenses.list_expenses'))
