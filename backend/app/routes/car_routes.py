from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Car
from app.schemas import CarSchema, CarListSchema
from app.utils.decorators import admin_required
from sqlalchemy import Case, or_, and_
import math

car_bp = Blueprint('cars', __name__)

# Initialize schemas
car_schema = CarSchema()
cars_schema = CarSchema(many=True)
car_list_schema = CarListSchema()


@car_bp.route('/', methods=['GET'])
def get_cars():
    """
    Get all cars with optional filtering and pagination
    Query Parameters:
        - page: int (default: 1)
        - per_page: int (default: 10, max: 100)
        - search: string (search in make and model)
        - car_type: string
        - min_rate: float
        - max_rate: float
        - available: boolean
        - sort_by: string (price, year, make)
        - order: string (asc, desc)
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    search = request.args.get('search', '')
    car_type = request.args.get('car_type', '')
    min_rate = request.args.get('min_rate', type=float)
    max_rate = request.args.get('max_rate', type=float)
    available = request.args.get('available', type=bool)
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')

    # Build query
    query = Car.query

    # Apply filters
    if search:
        query = query.filter(
            or_(
                Car.make.ilike(f'%{search}%'),
                Car.model.ilike(f'%{search}%')
            )
        )

    if car_type:
        query = query.filter(Car.car_type == car_type)

    if min_rate is not None:
        query = query.filter(Car.daily_rate >= min_rate)

    if max_rate is not None:
        query = query.filter(Car.daily_rate <= max_rate)

    if available is not None:
        query = query.filter(Car.is_available == available)

    # Apply sorting
    if sort_by == 'price':
        sort_column = Car.daily_rate
    elif sort_by == 'year':
        sort_column = Car.year
    elif sort_by == 'make':
        sort_column = Car.make
    else:
        sort_column = Car.id

    if order == 'desc':
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = query.order_by(sort_column)

    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    # Prepare response
    result = {
        'cars': car_schema.dump(paginated.items, many=True),
        'total': paginated.total,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(paginated.total / per_page)
    }

    return jsonify(result), 200


@car_bp.route('/<int:car_id>', methods=['GET'])
def get_car(car_id):
    """
    Get a specific car by ID
    """
    car = Car.query.get(car_id)

    if not car:
        return jsonify({'error': 'Car not found'}), 404

    return jsonify(car_schema.dump(car)), 200


@car_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_car():
    """
    Create a new car (Admin only)
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ['make', 'model', 'year', 'license_plate', 'daily_rate']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Check if license plate already exists
    if Car.query.filter_by(license_plate=data['license_plate']).first():
        return jsonify({'error': 'License plate already exists'}), 409

    try:
        # Create new car
        car = Car(
            make=data['make'],
            model=data['model'],
            year=data['year'],
            license_plate=data['license_plate'],
            color=data.get('color'),
            daily_rate=data['daily_rate'],
            is_available=data.get('is_available', True),
            car_type=data.get('car_type'),
            seats=data.get('seats', 5),
            transmission=data.get('transmission'),
            mileage=data.get('mileage', 0),
            fuel_type=data.get('fuel_type'),
            image_url=data.get('image_url'),
            description=data.get('description')
        )

        db.session.add(car)
        db.session.commit()

        return jsonify({
            'message': 'Car created successfully',
            'car': car_schema.dump(car)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create car: {str(e)}'}), 500


@car_bp.route('/<int:car_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_car(car_id):
    """
    Update a car (Admin only)
    """
    car = Car.query.get(car_id)

    if not car:
        return jsonify({'error': 'Car not found'}), 404

    data = request.get_json()

    # Allowed fields for update
    allowed_fields = [
        'make', 'model', 'year', 'color', 'daily_rate',
        'is_available', 'car_type', 'seats', 'transmission',
        'mileage', 'fuel_type', 'image_url', 'description'
    ]

    # Check if license plate is being updated and is unique
    if 'license_plate' in data and data['license_plate'] != car.license_plate:
        if Car.query.filter_by(license_plate=data['license_plate']).first():
            return jsonify({'error': 'License plate already exists'}), 409
        car.license_plate = data['license_plate']

    try:
        # Update allowed fields
        for field in allowed_fields:
            if field in data:
                setattr(car, field, data[field])

        db.session.commit()

        return jsonify({
            'message': 'Car updated successfully',
            'car': car_schema.dump(car)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update car: {str(e)}'}), 500


@car_bp.route('/<int:car_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_car(car_id):
    """
    Delete a car (Admin only)
    """
    car = Car.query.get(car_id)

    if not car:
        return jsonify({'error': 'Car not found'}), 404

    # Check if car has active rentals
    active_rentals = len([r for r in car.rentals if r.status == 'active'])
    if active_rentals > 0:
        return jsonify({
            'error': f'Cannot delete car with {active_rentals} active rental(s)'
        }), 400

    try:
        db.session.delete(car)
        db.session.commit()

        return jsonify({
            'message': f'Car {car.make} {car.model} deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete car: {str(e)}'}), 500


@car_bp.route('/available', methods=['GET'])
def get_available_cars():
    """
    Get only available cars (convenience endpoint)
    """
    cars = Car.query.filter_by(is_available=True).all()
    return jsonify({
        'cars': car_schema.dump(cars, many=True),
        'count': len(cars)
    }), 200


@car_bp.route('/types', methods=['GET'])
def get_car_types():
    """
    Get all unique car types with counts
    """
    from sqlalchemy import func

    results = db.session.query(
        Car.car_type,
        func.count(Car.id).label('count'),
        func.sum(Case((Car.is_available == True, 1), else_=0)).label('available_count')
    ).group_by(Car.car_type).all()

    return jsonify({
        'types': [
            {
                'type': r.car_type or 'Uncategorized',
                'total': r.count,
                'available': r.available_count
            }
            for r in results
        ]
    }), 200