"""
Routes Package
"""
from app.routes.auth_routes import auth_bp
from app.routes.car_routes import car_bp

__all__ = ['auth_bp', 'car_bp']