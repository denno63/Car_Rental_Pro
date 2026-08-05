"""
Rental Routes - Rental management with business logic
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Car, Rental
from app.schemas import RentalSchema, RentalListSchema, RentalCreateSchema
from app.utils.decorators import admin_required
from datetime import datetime, timedelta
import math

rental_bp = Blueprint('rentals', __name__, url_prefix='/rentals')

# Initialize schemas
rental_schema = RentalSchema()
rentals_schema = RentalSchema(many=True)
rental_list_schema = RentalListSchema()
rental_create_schema = RentalCreateSchema()


def check_car_availability(car_id, start_date, end_date, exclude_rental_id=None):
    """
    Check if a car is available for the given date range
    """
    query = Rental.query.filter(
        Rental.car_id == car_id,
        Rental.status.in_(['active', 'pending']),
        Rental.start_date <= end_date,
        Rental.end_date >= start_date
    )
    
    if exclude_rental_id:
        query = query.filter(Rental.id != exclude_rental_id)
    
    return query.count() == 0


def calculate_rental_cost(car, start_date, end_date):
    """
    Calculate rental cost with discounts
    """
    days = (end_date - start_date).days
    if days <= 0:
        return 0
    
    base_cost = days * car.daily_rate
    
    # Apply discounts
    discount = 0
    if days >= 7:
        discount = 0.10  # 10% off for 7+ days
    elif days >= 3:
        discount = 0.05   # 5% off for 3+ days
    
    total_cost = base_cost * (1 - discount)
    
    # Round to 2 decimal places
    return round(total_cost, 2)


@rental_bp.route('/', methods=['POST'])
@jwt_required()
def create_rental():
    """
    Create a new rental booking
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['car_id', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    # Validate dates
    if start_date < datetime.now():
        return jsonify({'error': 'Start date cannot be in the past'}), 400
    
    if end_date <= start_date:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    if (end_date - start_date).days > 30:
        return jsonify({'error': 'Maximum rental period is 30 days'}), 400
    
    # Check if car exists
    car = Car.query.get(data['car_id'])
    if not car:
        return jsonify({'error': 'Car not found'}), 404
    
    # Check if car is available
    if not car.is_available:
        return jsonify({'error': 'Car is not available'}), 400
    
    # Check for date conflicts
    if not check_car_availability(car.id, start_date, end_date):
        return jsonify({'error': 'Car is already booked for these dates'}), 409
    
    # Calculate cost
    total_cost = calculate_rental_cost(car, start_date, end_date)
    
    try:
        # Create rental
        rental = Rental(
            user_id=int(current_user_id),
            car_id=car.id,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost,
            status='active',
            notes=data.get('notes', '')
        )
        
        # Mark car as unavailable
        car.is_available = False
        
        db.session.add(rental)
        db.session.commit()
        
        return jsonify({
            'message': 'Rental created successfully',
            'rental': rental_schema.dump(rental)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create rental: {str(e)}'}), 500


@rental_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_rentals():
    """
    Get current user's rentals
    """
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    status = request.args.get('status')
    
    # Build query
    query = Rental.query.filter_by(user_id=int(current_user_id))
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Rental.created_at.desc())
    
    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'rentals': rental_schema.dump(paginated.items, many=True),
        'total': paginated.total,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(paginated.total / per_page)
    }
    
    return jsonify(result), 200


@rental_bp.route('/<int:rental_id>', methods=['GET'])
@jwt_required()
def get_rental(rental_id):
    """
    Get a specific rental
    """
    current_user_id = get_jwt_identity()
    rental = Rental.query.get(rental_id)
    
    if not rental:
        return jsonify({'error': 'Rental not found'}), 404
    
    # Check if user owns this rental or is admin
    user = User.query.get(int(current_user_id))
    if rental.user_id != int(current_user_id) and user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(rental_schema.dump(rental)), 200


@rental_bp.route('/<int:rental_id>/return', methods=['PUT'])
@jwt_required()
def return_rental(rental_id):
    """
    Process car return
    """
    current_user_id = get_jwt_identity()
    rental = Rental.query.get(rental_id)
    
    if not rental:
        return jsonify({'error': 'Rental not found'}), 404
    
    # Check if user owns this rental
    if rental.user_id != int(current_user_id):
        return jsonify({'error': 'Access denied'}), 403
    
    if rental.status != 'active':
        return jsonify({'error': f'Rental is already {rental.status}'}), 400
    
    try:
        # Process return
        rental.actual_return_date = datetime.now()
        rental.status = 'completed'
        
        # Calculate late fee if applicable
        if rental.actual_return_date > rental.end_date:
            late_days = (rental.actual_return_date - rental.end_date).days
            late_fee = late_days * (rental.car.daily_rate * 0.5)
            rental.total_cost += late_fee
            rental.total_cost = round(rental.total_cost, 2)
        
        # Make car available again
        rental.car.is_available = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'Car returned successfully',
            'rental': rental_schema.dump(rental),
            'late_fee': late_fee if 'late_fee' in locals() else 0
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process return: {str(e)}'}), 500


@rental_bp.route('/<int:rental_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_rental(rental_id):
    """
    Cancel a rental booking
    """
    current_user_id = get_jwt_identity()
    rental = Rental.query.get(rental_id)
    
    if not rental:
        return jsonify({'error': 'Rental not found'}), 404
    
    # Check if user owns this rental
    if rental.user_id != int(current_user_id):
        return jsonify({'error': 'Access denied'}), 403
    
    if rental.status != 'active':
        return jsonify({'error': f'Rental is already {rental.status}'}), 400
    
    # Check if cancellation is allowed (24 hours before start)
    now = datetime.now()
    if (rental.start_date - now).days < 1:
        return jsonify({'error': 'Cannot cancel within 24 hours of start'}), 400
    
    try:
        rental.status = 'cancelled'
        rental.car.is_available = True
        
        # Calculate refund (if any)
        refund_amount = rental.total_cost * 0.5  # 50% refund for cancellations
        
        db.session.commit()
        
        return jsonify({
            'message': 'Rental cancelled successfully',
            'refund_amount': refund_amount,
            'rental': rental_schema.dump(rental)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to cancel rental: {str(e)}'}), 500


@rental_bp.route('/admin/all', methods=['GET'])
@jwt_required()
@admin_required
def get_all_rentals():
    """
    Admin: Get all rentals
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)
    
    # Build query
    query = Rental.query
    
    if status:
        query = query.filter_by(status=status)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    query = query.order_by(Rental.created_at.desc())
    
    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'rentals': rental_schema.dump(paginated.items, many=True),
        'total': paginated.total,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(paginated.total / per_page)
    }
    
    return jsonify(result), 200


@rental_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_rental_stats():
    """
    Admin: Get rental statistics
    """
    from sqlalchemy import func, and_
    
    # Total rentals
    total_rentals = Rental.query.count()
    
    # Active rentals
    active_rentals = Rental.query.filter_by(status='active').count()
    
    # Completed rentals
    completed_rentals = Rental.query.filter_by(status='completed').count()
    
    # Cancelled rentals
    cancelled_rentals = Rental.query.filter_by(status='cancelled').count()
    
    # Total revenue (completed rentals only)
    total_revenue = db.session.query(
        func.sum(Rental.total_cost)
    ).filter(Rental.status == 'completed').scalar() or 0
    
    # Monthly revenue (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    monthly_revenue = db.session.query(
        func.sum(Rental.total_cost)
    ).filter(
        Rental.status == 'completed',
        Rental.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Most popular cars
    popular_cars = db.session.query(
        Car.make,
        Car.model,
        func.count(Rental.id).label('rental_count')
    ).join(Rental).filter(
        Rental.status == 'completed'
    ).group_by(Car.id).order_by(
        func.count(Rental.id).desc()
    ).limit(5).all()
    
    return jsonify({
        'total_rentals': total_rentals,
        'active_rentals': active_rentals,
        'completed_rentals': completed_rentals,
        'cancelled_rentals': cancelled_rentals,
        'total_revenue': round(total_revenue, 2),
        'monthly_revenue': round(monthly_revenue, 2),
        'popular_cars': [
            {
                'make': car.make,
                'model': car.model,
                'rental_count': car.rental_count
            }
            for car in popular_cars
        ]
    }), 200