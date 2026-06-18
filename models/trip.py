from datetime import datetime
from database import db


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    distance = db.Column(db.Float, nullable=True)
    trip_type = db.Column(db.String(20), nullable=False)
    rate = db.Column(db.Float, nullable=True)
    income = db.Column(db.Float, default=0.0)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Assigned')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    driver = db.relationship('User', foreign_keys=[driver_id])
    assigner = db.relationship('User', foreign_keys=[assigned_by])
    expenses = db.relationship('Expense', backref='trip', lazy=True, cascade='all, delete-orphan')

    def total_expenses(self):
        return sum(e.amount for e in self.expenses)

    def profit(self):
        return self.income - self.total_expenses()

    def to_dict(self):
        return {
            'id': self.id,
            'truck_id': self.truck_id,
            'truck_number': self.truck.truck_number if hasattr(self, 'truck') else None,
            'driver_id': self.driver_id,
            'driver_name': self.driver.name if hasattr(self, 'driver') else None,
            'assigned_by': self.assigned_by,
            'source': self.source,
            'destination': self.destination,
            'distance': self.distance,
            'trip_type': self.trip_type,
            'rate': self.rate,
            'income': self.income,
            'total_expenses': self.total_expenses(),
            'profit': self.profit(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Trip {self.id}: {self.source} -> {self.destination}>'
