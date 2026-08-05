"""
Rental Model - Manages car rental transactions
"""
from app import db
from datetime import datetime


class Rental(db.Model):
    __tablename__ = 'rentals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    actual_return_date = db.Column(db.DateTime)
    total_cost = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payments = db.relationship('Payment', backref='rental', lazy=True, cascade='all, delete-orphan')

    def calculate_cost(self):
        """Calculate total rental cost"""
        if not self.start_date or not self.end_date:
            return 0
            
        days = (self.end_date - self.start_date).days
        if days <= 0:
            return 0
            
        # Try to get car daily rate
        daily_rate = 0
        if self.car:
            daily_rate = self.car.daily_rate
        else:
            # Fallback: try to query the car
            from app.models import Car
            car = Car.query.get(self.car_id)
            if car:
                daily_rate = car.daily_rate
            else:
                return 0
                
        cost = days * daily_rate

        # Apply long-term discount (10% for 7+ days)
        if days >= 7:
            cost *= 0.9

        return round(cost, 2)

    def to_dict(self):
        """Convert rental to dictionary (for API responses)"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'car_id': self.car_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'actual_return_date': self.actual_return_date.isoformat() if self.actual_return_date else None,
            'total_cost': self.total_cost,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Rental {self.id} - User {self.user_id} - Car {self.car_id}>'