"""
RentWheel - Car Rental Management System
Flask Application Factory Pattern
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()


def create_app(config_object=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'sqlite:///rentwheel.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(
        os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = int(
        os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    # Configure CORS - Allow all origins (for testing)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        },
        r"/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })

    # JWT Callbacks
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user.id) if hasattr(user, 'id') else str(user)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models import User
        identity = jwt_data["sub"]
        return User.query.get(int(identity))

    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        from app.models import User
        user = User.query.get(int(identity))
        if user:
            return {
                'role': user.role,
                'username': user.username
            }
        return {}

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({
            'error': 'Missing or invalid token'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({
            'error': 'Invalid token'
        }), 401

    @jwt.expired_token_loader
    def expired_token_response(callback):
        return jsonify({
            'error': 'Token has expired'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_response(callback):
        return jsonify({
            'error': 'Token has been revoked'
        }), 401

    # Import models (for Flask-Migrate to detect)
    from app.models import User, Car, Rental, Payment  # noqa

    # Register blueprints
    from app.routes import auth_bp, car_bp, rental_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(car_bp)
    app.register_blueprint(rental_bp)

    @app.route('/')
    def home():
        return {
            'message': 'Welcome to RentWheel API',
            'version': '1.0.0',
            'status': 'running'
        }

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    return app