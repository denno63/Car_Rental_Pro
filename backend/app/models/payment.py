"""
Payment Model - Manages rental payments
"""
from app import db
from datetime import datetime


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(30))
    transaction_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')

    def to_dict(self):
        """Convert payment to dictionary (for API responses)"""
        return {
            'id': self.id,
            'rental_id': self.rental_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'status': self.status
        }

    def __repr__(self):
        return f'<Payment {self.id} - Rental {self.rental_id} - ${self.amount}>'