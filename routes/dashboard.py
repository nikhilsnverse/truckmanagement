from flask import Blueprint, render_template, session, redirect, url_for
from utils.decorators import login_required
from models.truck import Truck
from models.trip import Trip
from models.expense import Expense
from models.user import User
from database import db
from datetime import datetime, date, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('/')
@login_required
def index():
    role = session.get('role')

    if role == 'owner':
        return _owner_dashboard()
    elif role == 'manager':
        return _manager_dashboard()
    elif role == 'driver':
        return _driver_dashboard()
    return redirect(url_for('auth.login'))


def _owner_dashboard():
    total_trucks = Truck.query.count()
    active_trucks = Truck.query.filter_by(status='Active').count()
    total_trips = Trip.query.count()
    completed_trips = Trip.query.filter_by(status='Completed').count()

    total_income = db.session.query(func.coalesce(func.sum(Trip.income), 0)).scalar()
    total_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()
    total_profit = total_income - total_expense

    recent_trips = Trip.query.order_by(Trip.created_at.desc()).limit(5).all()
    drivers_count = User.query.filter_by(role='driver').count()
    managers_count = User.query.filter_by(role='manager').count()

    today = date.today()
    thirty_days = today + timedelta(days=30)
    expiring_trucks = Truck.query.filter(
        (Truck.insurance_expiry <= thirty_days) | (Truck.fitness_expiry <= thirty_days)
    ).all()

    monthly_rows = db.session.query(
        func.date_trunc('month', Trip.created_at).label('month'),
        func.coalesce(func.sum(Trip.income), 0).label('income'),
        func.coalesce(func.sum(Expense.amount), 0).label('expense')
    ).outerjoin(Expense, Expense.trip_id == Trip.id
    ).filter(Trip.status == 'Completed'
    ).group_by('month'
    ).order_by('month').limit(12).all()

    monthly_data = []
    for r in monthly_rows:
        monthly_data.append({
            'month': str(r.month).split()[0] if r.month else '',
            'income': float(r.income),
            'expense': float(r.expense)
        })

    return render_template('dashboard/owner.html',
        total_trucks=total_trucks,
        active_trucks=active_trucks,
        total_trips=total_trips,
        completed_trips=completed_trips,
        total_income=total_income,
        total_expense=total_expense,
        total_profit=total_profit,
        recent_trips=recent_trips,
        drivers_count=drivers_count,
        managers_count=managers_count,
        expiring_trucks=expiring_trucks,
        monthly_data=monthly_data
    )


def _manager_dashboard():
    total_trucks = Truck.query.count()
    active_trips = Trip.query.filter_by(status='In_Progress').count()
    pending_trips = Trip.query.filter_by(status='Assigned').count()

    total_income = db.session.query(func.coalesce(func.sum(Trip.income), 0)).scalar()
    total_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()

    recent_trips = Trip.query.order_by(Trip.created_at.desc()).limit(5).all()

    today = date.today()
    thirty_days = today + timedelta(days=30)
    expiring_trucks = Truck.query.filter(
        (Truck.insurance_expiry <= thirty_days) | (Truck.fitness_expiry <= thirty_days)
    ).all()

    return render_template('dashboard/manager.html',
        total_trucks=total_trucks,
        active_trips=active_trips,
        pending_trips=pending_trips,
        total_income=total_income,
        total_expense=total_expense,
        recent_trips=recent_trips,
        expiring_trucks=expiring_trucks
    )


def _driver_dashboard():
    driver_id = session.get('user_id')
    assigned_trips = Trip.query.filter_by(driver_id=driver_id, status='Assigned').count()
    in_progress_trips = Trip.query.filter_by(driver_id=driver_id, status='In_Progress').count()
    completed_trips = Trip.query.filter_by(driver_id=driver_id, status='Completed').count()

    my_trips = Trip.query.filter_by(driver_id=driver_id).order_by(Trip.created_at.desc()).limit(5).all()
    total_earned = db.session.query(func.coalesce(func.sum(Trip.income), 0)).filter(
        Trip.driver_id == driver_id, Trip.status == 'Completed'
    ).scalar()

    return render_template('dashboard/driver.html',
        assigned_trips=assigned_trips,
        in_progress_trips=in_progress_trips,
        completed_trips=completed_trips,
        my_trips=my_trips,
        total_earned=total_earned
    )
