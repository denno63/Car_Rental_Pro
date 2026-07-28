"""
Car Schema - Serialization/Deserialization for Car model
"""
from marshmallow import Schema, fields, validate, ValidationError
from app.models import Car


class CarSchema(Schema):
    """Schema for Car model"""
    id = fields.Int(dump_only=True)
    make = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    model = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    year = fields.Int(required=True, validate=validate.Range(min=2000, max=2025))
    license_plate = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    color = fields.Str(validate=validate.Length(max=30))
    daily_rate = fields.Float(required=True, validate=validate.Range(min=0.01))
    is_available = fields.Bool()
    car_type = fields.Str(validate=validate.Length(max=30))
    seats = fields.Int(validate=validate.Range(min=2, max=20))
    transmission = fields.Str(validate=validate.Length(max=20))
    mileage = fields.Int(validate=validate.Range(min=0))
    fuel_type = fields.Str(validate=validate.Length(max=20))
    image_url = fields.Str(validate=validate.Length(max=255))
    description = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        model = Car
        include_fk = True
        load_instance = True

    def validate_license_plate(self, value):
        """Custom validation for license plate"""
        if len(value) < 3:
            raise ValidationError("License plate must be at least 3 characters")
        return value


class CarListSchema(Schema):
    """Schema for list of cars with pagination"""
    cars = fields.List(fields.Nested(CarSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    total_pages = fields.Int()