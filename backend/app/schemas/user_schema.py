"""
User Schema - Serialization/Deserialization for User model
"""
from marshmallow import Schema, fields, validate, ValidationError
from app.models import User


class UserSchema(Schema):
    """Schema for User model"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    role = fields.Str(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Add rentals relationship (dump_only to avoid recursion)
    rentals = fields.Nested('RentalSchema', many=True, dump_only=True, exclude=('user',))

    class Meta:
        model = User
        include_fk = True
        load_instance = True