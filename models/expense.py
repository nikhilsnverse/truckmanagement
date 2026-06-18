from datetime import datetime
from database import db


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    bill_image = db.Column(db.String(255), nullable=True)
    approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    approver = db.relationship('User', foreign_keys=[approved_by])

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'type': self.type,
            'amount': self.amount,
            'description': self.description,
            'bill_image': self.bill_image,
            'approved': self.approved,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Expense {self.type}: ${self.amount}>'
