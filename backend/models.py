from sqlalchemy import (
    Column, 
    Integer, 
    Boolean, 
    ForeignKey, 
    Float, 
    CheckConstraint, 
    Date, 
    DateTime, 
    String, 
    func
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from backend.database import Base

class UserModel(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    
    # FIX: Use func.now() for server side default timestamps
    created_at = Column(DateTime, server_default=func.now()) 

    # FIX: Converted dynamic python list lookup to standard database-level text constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst', 'admin')", 
            name='check_valid_role'
        ),
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
    
    # FIX: Kept application-layer defaults using python datetime references (no brackets)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 

    # FIX: Converted dynamic constraints to strings
    __table_args__ = (
        CheckConstraint("type IN ('Van', 'Truck', 'Mini')", name='check_valid_vehicle_type'),
        CheckConstraint("status IN ('Available', 'On Trip', 'In Shop', 'Retired')", name='check_valid_vehicle_status'),
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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 

    # FIX: Converted status validation to dynamic database safe string format
    __table_args__ = (
        CheckConstraint('safety_score >= 0 AND safety_score <= 100', name='check_safety_score_range'),
        CheckConstraint("status IN ('Available', 'On Trip', 'Off Duty', 'Suspended')", name='check_valid_driver_status'), 
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
    created_at = Column(DateTime, default=datetime.utcnow) 

    # FIX: Formatted constraints as clean SQL expressions
    __table_args__ = (
        CheckConstraint("status IN ('Draft', 'Dispatched', 'Completed', 'Cancelled')", name='check_valid_trip_status'), 
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

    # FIX: Handled dynamic function constraint exception
    __table_args__ = (
        CheckConstraint("status IN ('Active', 'Closed')", name='check_valid_maintenance_status'), 
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

    # FIX: Converted check constraints into database literal strings
    __table_args__ = (
        CheckConstraint("expense_type IN ('Toll', 'Maintenance Linked', 'Other')", name='check_valid_expense_type'), 
    )
