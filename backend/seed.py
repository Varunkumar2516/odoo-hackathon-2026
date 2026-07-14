import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your Base, models, and engine 
# (Adjust these imports based on your actual file naming)
from backend.database import engine, Base,get_db
from backend.models import UserModel, Vehicle, Driver, Trip, MaintenanceLog, FuelLog, Expense
from backend.utils import hash
# Initialize Faker and Session
fake = Faker()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
db = SessionLocal()

def seed_data():
    print("Starting database seeding...")
    
    # 1. Create Users
    roles = ['Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst', 'admin']
    users = []
    # Ensure at least one admin
    users.append(UserModel(name="Admin User", email="admin@fleet.com", password="hashed_password_123", role="admin"))
    
    for _ in range(9):
        users.append(UserModel(
            name=fake.name(),
            email=fake.unique.email(),
            password=hash('1234'), # In production, use pwd_context.hash()
            role=random.choice(roles)
        ))
    db.add_all(users)
    print(f"Added {len(users)} users.")

    # 2. Create Vehicles
    v_types = ['Van', 'Truck', 'Mini']
    v_statuses = ['Available', 'On Trip', 'In Shop', 'Retired']
    vehicles = []
    for _ in range(10):
        vehicles.append(Vehicle(
            registration_number=fake.unique.license_plate(),
            name_model=f"{fake.company()} {random.choice(['Transit', 'Sprinter', 'F-150', 'Actros'])}",
            type=random.choice(v_types),
            max_load_capacity_kg=round(random.uniform(1000.0, 15000.0), 2),
            odometer_km=round(random.uniform(5000.0, 150000.0), 2),
            acquisition_cost=round(random.uniform(20000.0, 80000.0), 2),
            status=random.choice(v_statuses)
        ))
    db.add_all(vehicles)
    db.flush() # Flushes to database to generate vehicle_ids for relationships
    print(f"Added {len(vehicles)} vehicles.")

    # 3. Create Drivers
    d_statuses = ['Available', 'On Trip', 'Off Duty', 'Suspended']
    drivers = []
    for _ in range(8):
        drivers.append(Driver(
            name=fake.name(),
            license_number=fake.unique.bothify(text='??-######-##'),
            license_category=random.choice(['Class A', 'Class B', 'Commercial']),
            license_expiry_date=fake.date_between(start_date='+1y', end_date='+5y'),
            contact_number=fake.phone_number()[:20],
            safety_score=round(random.uniform(75.0, 100.0), 1),
            status=random.choice(d_statuses)
        ))
    db.add_all(drivers)
    db.flush() # Generates driver_ids
    print(f"Added {len(drivers)} drivers.")

    # 4. Create Trips
    trip_statuses = ['Draft', 'Dispatched', 'Completed', 'Cancelled']
    trips = []
    for i in range(15):
        random_vehicle = random.choice(vehicles)
        random_driver = random.choice(drivers)
        
        trips.append(Trip(
            trip_id=f"TRIP-{1000 + i}",
            source=fake.city(),
            destination=fake.city(),
            vehicle_id=random_vehicle.vehicle_id,
            driver_id=random_driver.driver_id,
            cargo_weight_kg=round(random.uniform(100.0, random_vehicle.max_load_capacity_kg), 2),
            planned_distance_km=round(random.uniform(50.0, 800.0), 2),
            status=random.choice(trip_statuses)
        ))
    db.add_all(trips)
    db.flush()
    print(f"Added {len(trips)} trips.")

    # 5. Create Maintenance Logs
    m_statuses = ['Active', 'Closed']
    m_types = ['Oil Change', 'Brake Inspection', 'Engine Tune-up', 'Tire Replacement']
    for _ in range(10):
        db.add(MaintenanceLog(
            vehicle_id=random.choice(vehicles).vehicle_id,
            service_type=random.choice(m_types),
            cost=round(random.uniform(50.0, 1200.0), 2),
            service_date=fake.date_between(start_date='-1y', end_date='today'),
            status=random.choice(m_statuses)
        ))
    print("Added 10 maintenance logs.")

    # 6. Create Fuel Logs
    for _ in range(20):
        db.add(FuelLog(
            vehicle_id=random.choice(vehicles).vehicle_id,
            date=fake.date_between(start_date='-6m', end_date='today'),
            liters_filled=round(random.uniform(30.0, 150.0), 2),
            fuel_cost=round(random.uniform(40.0, 250.0), 2)
        ))
    print("Added 20 fuel logs.")

    # 7. Create Expenses
    exp_types = ['Toll', 'Maintenance Linked', 'Other']
    for _ in range(15):
        random_trip = random.choice(trips)
        db.add(Expense(
            trip_id=random_trip.trip_id if random.choice([True, False]) else None, # Can be nullable
            vehicle_id=random_trip.vehicle_id,
            expense_type=random.choice(exp_types),
            amount=round(random.uniform(10.0, 150.0), 2),
            date=fake.date_between(start_date='-3m', end_date='today')
        ))
    print("Added 15 expenses.")

    # Commit all changes to the database safely
    try:
        db.commit()
        print("\nDatabase seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"\nSeeding failed! Error rolled back: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
