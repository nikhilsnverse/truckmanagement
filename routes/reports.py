from flask import Blueprint, render_template, request, session
from utils.decorators import login_required, manager_required
from models.trip import Trip
from models.expense import Expense
from models.truck import Truck
from models.user import User
from database import db
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
import io

reports_bp = Blueprint('reports', __name__, template_folder='../templates')


@reports_bp.route('/')
@manager_required
def index():
    return render_template('reports/index.html')


@reports_bp.route('/profit')
@manager_required
def profit_report():
    period_raw = request.args.get('period', 'monthly')
    pg_period = 'month' if period_raw == 'monthly' else 'year'
    period = period_raw

    query = db.session.query(
        func.date_trunc(pg_period, Trip.created_at).label('period'),
        func.coalesce(func.sum(Trip.income), 0).label('income'),
        func.coalesce(func.sum(Expense.amount), 0).label('expense')
    ).outerjoin(Expense, Expense.trip_id == Trip.id
    ).filter(Trip.status == 'Completed'
    ).group_by('period'
    ).order_by('period').all()

    profit_data = [{
        'period': str(q.period).split()[0] if q.period else 'N/A',
        'income': float(q.income),
        'expense': float(q.expense),
        'profit': float(q.income) - float(q.expense)
    } for q in query]

    return render_template('reports/profit.html', data=profit_data, period=period)


@reports_bp.route('/truck-wise')
@manager_required
def truck_wise():
    trucks = Truck.query.all()
    report = []
    for truck in trucks:
        trips = Trip.query.filter_by(truck_id=truck.id, status='Completed').all()
        total_income = sum(t.income for t in trips)
        total_expense = sum(sum(e.amount for e in t.expenses) for t in trips)
        report.append({
            'truck': truck,
            'total_trips': len(trips),
            'total_income': total_income,
            'total_expense': total_expense,
            'profit': total_income - total_expense
        })
    return render_template('reports/truck_wise.html', report=report)


@reports_bp.route('/export/csv')
@manager_required
def export_csv():
    import flask
    trips = Trip.query.filter_by(status='Completed').order_by(Trip.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Trip ID', 'Truck', 'Driver', 'Source', 'Destination', 'Distance',
                     'Income', 'Expenses', 'Profit', 'Date'])

    for t in trips:
        writer.writerow([
            t.id, t.truck.truck_number if t.truck else 'N/A',
            t.driver.name if t.driver else 'N/A',
            t.source, t.destination, t.distance,
            t.income, t.total_expenses(), t.profit(),
            t.created_at.strftime('%Y-%m-%d') if t.created_at else 'N/A'
        ])

    csv_bytes = output.getvalue().encode()
    return flask.Response(
        csv_bytes,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=trips_report.csv'}
    )
