"""
Custom Decorators for Authorization
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from app.models import User


def role_required(required_role):
    """
    Decorator to check if user has the required role
    Usage: @role_required('admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user claims
            claims = get_jwt()
            user_role = claims.get('role', 'customer')
            
            # Check if user has required role
            if user_role != required_role and user_role != 'admin':
                return jsonify({
                    'error': f'Role {required_role} required'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorator to check if user is admin
    Usage: @admin_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        user_role = claims.get('role', 'customer')
        
        if user_role != 'admin':
            return jsonify({
                'error': 'Admin access required'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Helper to get current user from JWT
    """
    user_id = get_jwt_identity()
    if user_id:
        return User.query.get(int(user_id))
    return None