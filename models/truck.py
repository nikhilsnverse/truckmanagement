from datetime import datetime
from database import db


class Truck(db.Model):
    __tablename__ = 'trucks'

    id = db.Column(db.Integer, primary_key=True)
    truck_number = db.Column(db.String(50), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    insurance_expiry = db.Column(db.Date, nullable=False)
    fitness_expiry = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Active')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trips = db.relationship('Trip', backref='truck', lazy=True, foreign_keys='Trip.truck_id')
    documents = db.relationship('Document', backref='truck', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'truck_number': self.truck_number,
            'model': self.model,
            'insurance_expiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            'fitness_expiry': self.fitness_expiry.isoformat() if self.fitness_expiry else None,
            'status': self.status,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Truck {self.truck_number}>'
