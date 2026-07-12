from pydantic import BaseModel , EmailStr , Field,ConfigDict
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