from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, manager_required, driver_required, role_required
from models.trip import Trip
from models.truck import Truck
from models.user import User
from models.expense import Expense
from database import db
from datetime import datetime
from utils.helpers import calculate_income

trips_bp = Blueprint('trips', __name__, template_folder='../templates')


@trips_bp.route('/')
@login_required
def list_trips():
    role = session.get('role')
    query = Trip.query

    if role == 'driver':
        query = query.filter_by(driver_id=session.get('user_id'))
    elif role == 'manager':
        query = query.filter_by(assigned_by=session.get('user_id'))

    status_filter = request.args.get('status', '')
    if status_filter:
        query = query.filter_by(status=status_filter)

    trips = query.order_by(Trip.created_at.desc()).all()
    return render_template('trips/list.html', trips=trips, status_filter=status_filter, role=role)


@trips_bp.route('/add', methods=['GET', 'POST'])
@manager_required
def add_trip():
    trucks = Truck.query.filter_by(status='Active').all()
    drivers = User.query.filter_by(role='driver').all()

    if request.method == 'POST':
        truck_id = request.form.get('truck_id')
        driver_id = request.form.get('driver_id')
        source = request.form.get('source', '').strip()
        destination = request.form.get('destination', '').strip()
        distance = request.form.get('distance', '').strip()
        trip_type = request.form.get('trip_type', 'distance_based')
        rate = request.form.get('rate', '').strip()

        if not truck_id or not driver_id or not source or not destination:
            flash('Please fill in all required fields.', 'danger')
            return render_template('trips/form.html', trip=None, trucks=trucks, drivers=drivers)

        distance_val = float(distance) if distance else 0
        rate_val = float(rate) if rate else 0
        income = calculate_income(distance_val, trip_type, rate_val)

        trip = Trip(
            truck_id=int(truck_id),
            driver_id=int(driver_id),
            assigned_by=session.get('user_id'),
            source=source,
            destination=destination,
            distance=distance_val,
            trip_type=trip_type,
            rate=rate_val,
            income=income,
            status='Assigned'
        )
        db.session.add(trip)
        db.session.commit()
        flash('Trip assigned successfully!', 'success')
        return redirect(url_for('trips.list_trips'))

    return render_template('trips/form.html', trip=None, trucks=trucks, drivers=drivers)


@trips_bp.route('/edit/<int:trip_id>', methods=['GET', 'POST'])
@manager_required
def edit_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    trucks = Truck.query.filter_by(status='Active').all()
    drivers = User.query.filter_by(role='driver').all()

    if request.method == 'POST':
        trip.truck_id = int(request.form.get('truck_id'))
        trip.driver_id = int(request.form.get('driver_id'))
        trip.source = request.form.get('source', '').strip()
        trip.destination = request.form.get('destination', '').strip()
        trip.distance = float(request.form.get('distance', 0))
        trip.trip_type = request.form.get('trip_type', 'distance_based')
        trip.rate = float(request.form.get('rate', 0))
        trip.income = calculate_income(trip.distance, trip.trip_type, trip.rate)

        db.session.commit()
        flash('Trip updated successfully!', 'success')
        return redirect(url_for('trips.list_trips'))

    return render_template('trips/form.html', trip=trip, trucks=trucks, drivers=drivers)


@trips_bp.route('/start/<int:trip_id>', methods=['POST'])
@driver_required
def start_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.driver_id != session.get('user_id'):
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('trips.list_trips'))

    trip.status = 'In_Progress'
    trip.start_time = datetime.utcnow()
    db.session.commit()
    flash('Trip started!', 'success')
    return redirect(url_for('trips.list_trips'))


@trips_bp.route('/complete/<int:trip_id>', methods=['POST'])
@driver_required
def complete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.driver_id != session.get('user_id'):
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('trips.list_trips'))

    distance = request.form.get('distance', '').strip()
    if distance:
        trip.distance = float(distance)
        trip.income = calculate_income(trip.distance, trip.trip_type, trip.rate)

    trip.status = 'Completed'
    trip.end_time = datetime.utcnow()
    db.session.commit()
    flash('Trip completed!', 'success')
    return redirect(url_for('trips.list_trips'))


@trips_bp.route('/delete/<int:trip_id>', methods=['POST'])
@manager_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    db.session.delete(trip)
    db.session.commit()
    flash('Trip deleted.', 'success')
    return redirect(url_for('trips.list_trips'))
