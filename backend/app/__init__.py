"""
CarRentalPro - Car Rental Management System
Flask Application Factory Pattern
"""

from flask import Flask
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
cors = CORS()


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

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=os.getenv('FRONTEND_URL', 'http://localhost:3000'))

    # Import models (for Flask-Migrate to detect)
    from app.models import User, Car, Rental, Payment  # noqa

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