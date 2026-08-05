"""
Rental Schema - Serialization/Deserialization for Rental model
"""
from marshmallow import Schema, fields, validate, ValidationError
from app.models import Rental
from datetime import datetime


class RentalSchema(Schema):
    """Schema for Rental model"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    car_id = fields.Int(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    actual_return_date = fields.DateTime(dump_only=True)
    total_cost = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested fields - use string references with proper excludes
    user = fields.Nested('UserSchema', dump_only=True, exclude=('rentals',))
    car = fields.Nested('CarSchema', dump_only=True, exclude=('rentals',))

    class Meta:
        model = Rental
        include_fk = True
        load_instance = True

    def validate_start_date(self, value):
        """Validate start date is not in the past"""
        if value < datetime.now():
            raise ValidationError("Start date cannot be in the past")
        return value


class RentalListSchema(Schema):
    """Schema for list of rentals with pagination"""
    rentals = fields.List(fields.Nested(RentalSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    total_pages = fields.Int()


class RentalCreateSchema(Schema):
    """Schema for creating a rental"""
    car_id = fields.Int(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    notes = fields.Str()

    def validate_start_date(self, value):
        if value < datetime.now():
            raise ValidationError("Start date cannot be in the past")
        return value

    def validate_end_date(self, value, **kwargs):
        start_date = self.context.get('start_date')
        if start_date and value <= start_date:
            raise ValidationError("End date must be after start date")
        if (value - start_date).days > 30:
            raise ValidationError("Maximum rental period is 30 days")
        return value