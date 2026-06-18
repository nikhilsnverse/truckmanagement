import os
import uuid
from datetime import datetime, date, timedelta
from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return filename
    return None


def calculate_income(distance, trip_type, rate):
    if trip_type == 'distance_based' and distance and rate:
        return distance * rate
    elif trip_type == 'fixed':
        return rate or 0
    return 0


def get_expiry_alerts():
    today = date.today()
    thirty_days = today + timedelta(days=30)
    from models.truck import Truck
    trucks = Truck.query.all()
    alerts = []
    for truck in trucks:
        if truck.insurance_expiry and truck.insurance_expiry <= thirty_days:
            alerts.append({
                'type': 'Insurance Expiry',
                'truck': truck.truck_number,
                'expiry_date': truck.insurance_expiry.isoformat(),
                'days_left': (truck.insurance_expiry - today).days
            })
        if truck.fitness_expiry and truck.fitness_expiry <= thirty_days:
            alerts.append({
                'type': 'Fitness Expiry',
                'truck': truck.truck_number,
                'expiry_date': truck.fitness_expiry.isoformat(),
                'days_left': (truck.fitness_expiry - today).days
            })
    return alerts
