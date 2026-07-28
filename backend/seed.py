"""
Database Seeding Script
Populates the database with initial test data
"""
from app import create_app, db
from app.models import User, Car, Rental, Payment
from datetime import datetime, timedelta
import random

app = create_app()


def seed_users():
    """Create sample users"""
    users = [
        {
            'username': 'admin',
            'email': 'admin@rentwheel.com',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin'
        },
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'John123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'customer'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'Jane123!',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'customer'
        },
        {
            'username': 'bob_wilson',
            'email': 'bob@example.com',
            'password': 'Bob123!',
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'role': 'customer'
        }
    ]

    for user_data in users:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role']
        )
        db.session.add(user)

    db.session.commit()
    print(f"✅ Created {len(users)} users")
    return User.query.all()


def seed_cars():
    """Create sample cars"""
    cars = [
        {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2022,
            'license_plate': 'ABC123',
            'color': 'Silver',
            'daily_rate': 65.00,
            'car_type': 'Sedan',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 15230,
            'fuel_type': 'Gasoline',
            'description': 'Comfortable sedan with great fuel economy.'
        },
        {
            'make': 'Honda',
            'model': 'CR-V',
            'year': 2023,
            'license_plate': 'XYZ789',
            'color': 'Blue',
            'daily_rate': 85.00,
            'car_type': 'SUV',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 5000,
            'fuel_type': 'Hybrid',
            'description': 'Spacious SUV with hybrid technology.'
        },
        {
            'make': 'BMW',
            'model': 'X5',
            'year': 2022,
            'license_plate': 'BMW777',
            'color': 'Black',
            'daily_rate': 120.00,
            'car_type': 'SUV',
            'seats': 7,
            'transmission': 'Automatic',
            'mileage': 8200,
            'fuel_type': 'Diesel',
            'description': 'Luxury SUV with premium features.'
        },
        {
            'make': 'Tesla',
            'model': 'Model 3',
            'year': 2023,
            'license_plate': 'TESLA01',
            'color': 'White',
            'daily_rate': 150.00,
            'car_type': 'Sedan',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 1200,
            'fuel_type': 'Electric',
            'description': 'Fully electric sedan with autopilot.'
        },
        {
            'make': 'Ford',
            'model': 'F-150',
            'year': 2022,
            'license_plate': 'FORD150',
            'color': 'Red',
            'daily_rate': 95.00,
            'car_type': 'Truck',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 25000,
            'fuel_type': 'Gasoline',
            'description': 'Powerful pickup truck with towing capacity.'
        },
        {
            'make': 'Mercedes',
            'model': 'C-Class',
            'year': 2023,
            'license_plate': 'MER123',
            'color': 'Silver',
            'daily_rate': 130.00,
            'car_type': 'Sedan',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 3500,
            'fuel_type': 'Gasoline',
            'description': 'Luxury sedan with elegant design.'
        },
        {
            'make': 'Hyundai',
            'model': 'Tucson',
            'year': 2023,
            'license_plate': 'HYUND01',
            'color': 'Green',
            'daily_rate': 75.00,
            'car_type': 'SUV',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 1800,
            'fuel_type': 'Hybrid',
            'description': 'Eco-friendly SUV with great fuel efficiency.'
        },
        {
            'make': 'Chevrolet',
            'model': 'Malibu',
            'year': 2022,
            'license_plate': 'CHEV01',
            'color': 'White',
            'daily_rate': 70.00,
            'car_type': 'Sedan',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 18000,
            'fuel_type': 'Gasoline',
            'description': 'Reliable sedan perfect for business trips.'
        },
        {
            'make': 'Toyota',
            'model': 'RAV4',
            'year': 2023,
            'license_plate': 'RAV2023',
            'color': 'Gray',
            'daily_rate': 88.00,
            'car_type': 'SUV',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 2500,
            'fuel_type': 'Hybrid',
            'description': 'Popular SUV with hybrid efficiency.'
        },
        {
            'make': 'Nissan',
            'model': 'Altima',
            'year': 2022,
            'license_plate': 'ALT123',
            'color': 'Blue',
            'daily_rate': 60.00,
            'car_type': 'Sedan',
            'seats': 5,
            'transmission': 'Automatic',
            'mileage': 22000,
            'fuel_type': 'Gasoline',
            'description': 'Affordable sedan with good mileage.'
        }
    ]

    for car_data in cars:
        car = Car(**car_data)
        db.session.add(car)

    db.session.commit()
    print(f"✅ Created {len(cars)} cars")
    return Car.query.all()


def seed_rentals(users, cars):
    """Create sample rentals"""
    # Set up dates for rentals
    today = datetime.now().date()
    
    rentals_data = [
        {
            'user': users[1],  # john_doe
            'car': cars[0],    # Toyota Camry
            'start_date': today - timedelta(days=5),
            'end_date': today + timedelta(days=2),
            'status': 'active'
        },
        {
            'user': users[2],  # jane_smith
            'car': cars[1],    # Honda CR-V
            'start_date': today - timedelta(days=10),
            'end_date': today - timedelta(days=3),
            'status': 'completed'
        },
        {
            'user': users[3],  # bob_wilson
            'car': cars[2],    # BMW X5
            'start_date': today + timedelta(days=3),
            'end_date': today + timedelta(days=8),
            'status': 'active'
        },
        {
            'user': users[1],  # john_doe
            'car': cars[3],    # Tesla Model 3
            'start_date': today - timedelta(days=15),
            'end_date': today - timedelta(days=8),
            'status': 'completed'
        }
    ]

    for rental_data in rentals_data:
        # Calculate days and cost
        start = rental_data['start_date']
        end = rental_data['end_date']
        days = (end - start).days
        daily_rate = rental_data['car'].daily_rate
        total_cost = days * daily_rate
        
        # Apply discount for 7+ days
        if days >= 7:
            total_cost *= 0.9
            
        total_cost = round(total_cost, 2)
        
        rental = Rental(
            user_id=rental_data['user'].id,
            car_id=rental_data['car'].id,
            start_date=start,
            end_date=end,
            status=rental_data['status'],
            total_cost=total_cost
        )
        db.session.add(rental)

    db.session.commit()
    print(f"✅ Created {len(rentals_data)} rentals")


def seed_database():
    """Main seeding function"""
    print("🌱 Seeding database...")

    with app.app_context():
        # Clear existing data
        print("🗑️  Clearing existing data...")
        db.drop_all()
        db.create_all()
        print("✅ Database reset")

        # Seed data
        users = seed_users()
        cars = seed_cars()
        seed_rentals(users, cars)

        print("🎉 Database seeding complete!")


if __name__ == '__main__':
    seed_database()