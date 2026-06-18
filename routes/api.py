from flask import Blueprint, jsonify, session
from utils.decorators import login_required
from models.trip import Trip
from models.expense import Expense
from models.truck import Truck
from models.user import User
from database import db
from sqlalchemy import func
from datetime import datetime, date, timedelta

api_bp = Blueprint('api', __name__)


@api_bp.route('/stats')
@login_required
def stats():
    total_trucks = Truck.query.count()
    active_trucks = Truck.query.filter_by(status='Active').count()
    total_trips = Trip.query.count()
    completed_trips = Trip.query.filter_by(status='Completed').count()
    total_income = db.session.query(func.coalesce(func.sum(Trip.income), 0)).scalar()
    total_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()

    today = date.today()
    thirty_days = today + timedelta(days=30)
    expiring = Truck.query.filter(
        (Truck.insurance_expiry <= thirty_days) | (Truck.fitness_expiry <= thirty_days)
    ).count()

    return jsonify({
        'total_trucks': total_trucks,
        'active_trucks': active_trucks,
        'total_trips': total_trips,
        'completed_trips': completed_trips,
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'profit': float(total_income - total_expense),
        'expiring_count': expiring
    })


@api_bp.route('/monthly-data')
@login_required
def monthly_data():
    data = db.session.query(
        func.date_trunc('month', Trip.created_at).label('month'),
        func.coalesce(func.sum(Trip.income), 0).label('income'),
        func.coalesce(func.sum(Expense.amount), 0).label('expense')
    ).outerjoin(Expense, Expense.trip_id == Trip.id
    ).filter(Trip.status == 'Completed'
    ).group_by('month'
    ).order_by('month').limit(12).all()

    result = [{
        'month': str(q.month).split()[0] if q.month else '',
        'income': float(q.income),
        'expense': float(q.expense),
        'profit': float(q.income) - float(q.expense)
    } for q in data]

    return jsonify(result)


@api_bp.route('/recent-trips')
@login_required
def recent_trips():
    trips = Trip.query.order_by(Trip.created_at.desc()).limit(5).all()
    return jsonify([t.to_dict() for t in trips])


@api_bp.route('/drivers')
@login_required
def drivers():
    drivers = User.query.filter_by(role='driver').all()
    return jsonify([d.to_dict() for d in drivers])


@api_bp.route('/trucks')
@login_required
def trucks():
    trucks = Truck.query.all()
    return jsonify([t.to_dict() for t in trucks])


@api_bp.route('/alerts')
@login_required
def alerts():
    today = date.today()
    thirty_days = today + timedelta(days=30)
    trucks = Truck.query.filter(
        (Truck.insurance_expiry <= thirty_days) | (Truck.fitness_expiry <= thirty_days)
    ).all()

    result = []
    for truck in trucks:
        if truck.insurance_expiry and truck.insurance_expiry <= thirty_days:
            result.append({
                'type': 'Insurance',
                'truck': truck.truck_number,
                'expires': truck.insurance_expiry.isoformat(),
                'days_left': (truck.insurance_expiry - today).days
            })
        if truck.fitness_expiry and truck.fitness_expiry <= thirty_days:
            result.append({
                'type': 'Fitness',
                'truck': truck.truck_number,
                'expires': truck.fitness_expiry.isoformat(),
                'days_left': (truck.fitness_expiry - today).days
            })
    return jsonify(result)
