from sqlalchemy import Column, Integer, Boolean, ForeignKey, Float, CheckConstraint, Date, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .database import Base

class UserModel(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) # FIXED

    __table_args__ = (
        CheckConstraint(role.in_(['Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst','admin']), name='check_valid_role'), # FIXED
    )


class Vehicle(Base):
    __tablename__ = 'vehicles'

    vehicle_id = Column(Integer, primary_key=True, autoincrement=True)
    registration_number = Column(String(50), unique=True, nullable=False)
    name_model = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    max_load_capacity_kg = Column(Float, nullable=False)
    odometer_km = Column(Float, nullable=False, default=0.0)
    acquisition_cost = Column(Float, nullable=False)
    status = Column(String(30), nullable=False, default='Available')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # FIXED

    __table_args__ = (
        CheckConstraint(type.in_(['Van', 'Truck', 'Mini']), name='check_valid_vehicle_type'), # FIXED
        CheckConstraint(status.in_(['Available', 'On Trip', 'In Shop', 'Retired']), name='check_valid_vehicle_status'), # FIXED
    )
    
    # Relationships
    trips = relationship("Trip", back_populates="vehicle")
    maintenance_logs = relationship("MaintenanceLog", back_populates="vehicle")
    fuel_logs = relationship("FuelLog", back_populates="vehicle")


class Driver(Base):
    __tablename__ = 'drivers'

    driver_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    license_category = Column(String(20), nullable=False)
    license_expiry_date = Column(Date, nullable=False)
    contact_number = Column(String(20), nullable=False)
    safety_score = Column(Float, default=100.0)
    status = Column(String(30), nullable=False, default='Available')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # FIXED

    __table_args__ = (
        CheckConstraint('safety_score >= 0 AND safety_score <= 100', name='check_safety_score_range'),
        CheckConstraint(status.in_(['Available', 'On Trip', 'Off Duty', 'Suspended']), name='check_valid_driver_status'), # FIXED
    )

    # Relationships
    trips = relationship("Trip", back_populates="driver")


class Trip(Base):
    __tablename__ = 'trips'

    trip_id = Column(String(50), primary_key=True) 
    source = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.driver_id'), nullable=False)
    cargo_weight_kg = Column(Float, nullable=False)
    planned_distance_km = Column(Float, nullable=False)
    status = Column(String(30), nullable=False, default='Draft')
    created_at = Column(DateTime, default=datetime.utcnow) # FIXED

    __table_args__ = (
        CheckConstraint(status.in_(['Draft', 'Dispatched', 'Completed', 'Cancelled']), name='check_valid_trip_status'), # FIXED
    )

    # Relationships
    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")


class MaintenanceLog(Base):
    __tablename__ = 'maintenance_logs'

    maintenance_id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'), nullable=False)
    service_type = Column(String(100), nullable=False)
    cost = Column(Float, nullable=False, default=0.0)
    service_date = Column(Date, nullable=False)
    status = Column(String(30), nullable=False, default='Active')

    __table_args__ = (
        CheckConstraint(status.in_(['Active', 'Closed']), name='check_valid_maintenance_status'), # FIXED
    )

    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_logs")


class FuelLog(Base):
    __tablename__ = 'fuel_logs'

    fuel_log_id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'), nullable=False)
    date = Column(Date, nullable=False)
    liters_filled = Column(Float, nullable=False)
    fuel_cost = Column(Float, nullable=False)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="fuel_logs")


class Expense(Base):
    __tablename__ = 'expenses'

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(50), ForeignKey('trips.trip_id'), nullable=True) 
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'), nullable=False)
    expense_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint(expense_type.in_(['Toll', 'Maintenance Linked', 'Other']), name='check_valid_expense_type'), # FIXED
    )