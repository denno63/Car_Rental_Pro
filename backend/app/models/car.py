"""
Car Model - Manages car inventory
"""
from app import db
from datetime import datetime


class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    color = db.Column(db.String(30))
    daily_rate = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    car_type = db.Column(db.String(30))
    seats = db.Column(db.Integer, default=5)
    transmission = db.Column(db.String(20))
    mileage = db.Column(db.Integer, default=0)
    fuel_type = db.Column(db.String(20))
    image_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rentals = db.relationship('Rental', backref='car', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert car to dictionary (for API responses)"""
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'license_plate': self.license_plate,
            'color': self.color,
            'daily_rate': self.daily_rate,
            'is_available': self.is_available,
            'car_type': self.car_type,
            'seats': self.seats,
            'transmission': self.transmission,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type,
            'image_url': self.image_url,
            'description': self.description
        }

    def __repr__(self):
        return f'<Car {self.make} {self.model} ({self.license_plate})>'