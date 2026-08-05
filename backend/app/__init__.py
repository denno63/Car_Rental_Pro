"""
RentWheel - Car Rental Management System
Flask Application Factory Pattern
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_object=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    # ✅ CRITICAL FIX: Changed DATABASE_URL to DATABASE_URI
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

    # Configure CORS - Allow all origins
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })

    # Import models
    from app.models import User, Car, Rental, Payment

    # Create tables and seed data on startup
    with app.app_context():
        db.create_all()

        # Seed data if no users exist
        if User.query.count() == 0:
            print("🌱 Seeding database...")

            # Create admin user
            admin = User(
                username='admin',
                email='admin@rentwheel.com',
                password='Admin123!',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            db.session.add(admin)

            # Create regular users
            users = [
                User(
                    username='john_doe',
                    email='john@example.com',
                    password='John123!',
                    first_name='John',
                    last_name='Doe',
                    role='customer'
                ),
                User(
                    username='jane_smith',
                    email='jane@example.com',
                    password='Jane123!',
                    first_name='Jane',
                    last_name='Smith',
                    role='customer'
                ),
                User(
                    username='bob_wilson',
                    email='bob@example.com',
                    password='Bob123!',
                    first_name='Bob',
                    last_name='Wilson',
                    role='customer'
                )
            ]
            for user in users:
                db.session.add(user)

            # Create cars
            cars = [
                Car(make='Toyota', model='Camry', year=2022, license_plate='ABC123', color='Silver', daily_rate=65.00, car_type='Sedan', seats=5, transmission='Automatic', mileage=15230, fuel_type='Gasoline', description='Comfortable sedan with great fuel economy.'),
                Car(make='Honda', model='CR-V', year=2023, license_plate='XYZ789', color='Blue', daily_rate=85.00, car_type='SUV', seats=5, transmission='Automatic', mileage=5000, fuel_type='Hybrid', description='Spacious SUV with hybrid technology.'),
                Car(make='Tesla', model='Model 3', year=2023, license_plate='TESLA01', color='White', daily_rate=150.00, car_type='Sedan', seats=5, transmission='Automatic', mileage=1200, fuel_type='Electric', description='Fully electric sedan with autopilot.'),
                Car(make='BMW', model='X5', year=2022, license_plate='BMW777', color='Black', daily_rate=120.00, car_type='SUV', seats=7, transmission='Automatic', mileage=8200, fuel_type='Diesel', description='Luxury SUV with premium features.'),
                Car(make='Ford', model='F-150', year=2022, license_plate='FORD150', color='Red', daily_rate=95.00, car_type='Truck', seats=5, transmission='Automatic', mileage=25000, fuel_type='Gasoline', description='Powerful pickup truck with towing capacity.'),
                Car(make='Mercedes', model='C-Class', year=2023, license_plate='MER123', color='Silver', daily_rate=130.00, car_type='Sedan', seats=5, transmission='Automatic', mileage=3500, fuel_type='Gasoline', description='Luxury sedan with elegant design.'),
                Car(make='Hyundai', model='Tucson', year=2023, license_plate='HYUND01', color='Green', daily_rate=75.00, car_type='SUV', seats=5, transmission='Automatic', mileage=1800, fuel_type='Hybrid', description='Eco-friendly SUV with great fuel efficiency.'),
                Car(make='Chevrolet', model='Malibu', year=2022, license_plate='CHEV01', color='White', daily_rate=70.00, car_type='Sedan', seats=5, transmission='Automatic', mileage=18000, fuel_type='Gasoline', description='Reliable sedan perfect for business trips.'),
                Car(make='Toyota', model='RAV4', year=2023, license_plate='RAV2023', color='Gray', daily_rate=88.00, car_type='SUV', seats=5, transmission='Automatic', mileage=2500, fuel_type='Hybrid', description='Popular SUV with hybrid efficiency.'),
                Car(make='Nissan', model='Altima', year=2022, license_plate='ALT123', color='Blue', daily_rate=60.00, car_type='Sedan', seats=5, transmission='Automatic', mileage=22000, fuel_type='Gasoline', description='Affordable sedan with good mileage.')
            ]
            for car in cars:
                db.session.add(car)

            db.session.commit()
            print("✅ Database seeded with 4 users and 10 cars!")

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

    # Register blueprints with /api prefix
    from app.routes import auth_bp, car_bp, rental_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(car_bp, url_prefix='/api')
    app.register_blueprint(rental_bp, url_prefix='/api')

   # Add this for debugging
    @app.route('/debug/routes')
    def list_routes():
       routes = []
       for rule in app.url_map.iter_rules():
        routes.append(str(rule))
       return jsonify({'routes': routes})

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