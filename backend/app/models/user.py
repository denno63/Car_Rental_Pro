"""
User Model - Manages user accounts and authentication
"""
from app import db
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='customer')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rentals = db.relationship('Rental', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email
        self.password_hash = self.hash_password(password)
        super(User, self).__init__(**kwargs)

    def hash_password(self, password):
        """Hash a password"""
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify password against stored hash"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary (for API responses)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


# JWT Callbacks - Add these to app/__init__.py
def jwt_identity_lookup(payload):
    """Get user from JWT identity"""
    from app import db
    user_id = payload.get('sub')
    if user_id:
        return User.query.get(int(user_id))
    return None


def jwt_claims_loader(user):
    """Add custom claims to JWT"""
    return {
        'role': user.role,
        'username': user.username
    }