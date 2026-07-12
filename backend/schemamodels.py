from pydantic import BaseModel , EmailStr , Field,ConfigDict
from typing import List
import re
from datetime import datetime
from typing import Optional,Literal 
from sqlalchemy.dialects.postgresql import UUID
from datetime import date

class UserCreate(BaseModel):
    name:str
    email:EmailStr
    password:str 


class UserResponse(BaseModel):
    id:int
    name:str
    email:EmailStr 
    
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email:EmailStr
    password:str


class LoginResponse(BaseModel):
    email:EmailStr

class VehicleBase(BaseModel):
    registration_number: str = Field(..., max_length=50, description="Unique Reg No.")
    name_model: str = Field(..., max_length=100)
    type: Literal['Van', 'Truck', 'Mini']
    max_load_capacity_kg: float
    odometer_km: float = 0.0
    acquisition_cost: float
    status: Literal['Available', 'On Trip', 'In Shop', 'Retired'] = 'Available'


class VehicleCreate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    vehicle_id: int
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class MaintenanceLogCreate(BaseModel):
    vehicle_id: int
    service_type: str
    cost: float
    service_date: date
    status: str
    
class MaintenanceLog(MaintenanceLogCreate):
    maintenance_id: int 

    class Config:
        from_attributes = True 
        
class FuelLogBase(BaseModel):
    vehicle_name: str
    date: date
    liters: float
    fuel_cost: float

class ExpenseBase(BaseModel):
    trip_id: str
    vehicle_name: str
    toll: float
    other: float
    maintenance_linked: float
    status: str
    
class VehicleSummary(BaseModel):
    vehicle_id: int
    registration_number: str

    class Config:
        from_attributes = True

class FuelLogCreate(BaseModel):
    vehicle_id: int
    date: date
    liters_filled: float
    fuel_cost: float

class FuelLogResponse(FuelLogCreate):
    fuel_log_id: int
    vehicle: Optional[VehicleSummary] = None

    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    trip_id: Optional[str] = None
    vehicle_id: int
    expense_type: str
    amount: float
    date: date

class ExpenseResponse(ExpenseCreate):
    expense_id: int
    vehicle: Optional[VehicleSummary] = None

    class Config:
        from_attributes = True
        

class TripCreate(BaseModel):
    trip_id: str
    source: str
    destination: str
    vehicle_id: int
    driver_id: int
    cargo_weight_kg: float
    planned_distance_km: float

class TripResponse(TripCreate):
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        
class DriverCreate(BaseModel):
    name: str
    license_number: str
    license_category: str
    license_expiry_date: date
    contact_number: str
    status: str = 'Available'

class DriverResponse(DriverCreate):
    driver_id: int
    safety_score: float

    class Config:
        from_attributes = True
        
class AnalyticsSummary(BaseModel):
    fuel_efficiency: str
    fleet_utilization: str
    operational_cost: float
    vehicle_roi: str

class VehicleCost(BaseModel):
    vehicle_name: str
    cost: float

class AnalyticsResponse(BaseModel):
    summary: AnalyticsSummary
    monthly_revenue: List[float]
    top_costly_vehicles: List[VehicleCost]