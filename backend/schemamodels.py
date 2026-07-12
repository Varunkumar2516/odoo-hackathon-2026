# from pydantic import BaseModel , EmailStr , Field,ConfigDict
# import re
# from datetime import datetime
# from typing import Optional,Literal 
# from sqlalchemy.dialects.postgresql import UUID

# class UserCreate(BaseModel):
#     name:str
#     email:EmailStr
#     password:str 


# class UserResponse(BaseModel):
#     id:int
#     name:str
#     email:EmailStr 
    
#     model_config = ConfigDict(from_attributes=True)

# class UserLogin(BaseModel):
#     email:EmailStr
#     password:str


# class LoginResponse(BaseModel):
#     email:EmailStr

# =================================================

from pydantic import BaseModel
from datetime import date
from typing import Optional

class VehicleCreate(BaseModel):
    reg_number: str
    model: str
    type: str
    max_load: float
    acquisition_cost: float

class DriverCreate(BaseModel):
    name: str
    license_number: str
    license_category: str
    license_expiry: date

class TripCreate(BaseModel):
    vehicle_id: int
    driver_id: int
    source: str
    destination: str
    cargo_weight: float
    distance: float

class MaintenanceCreate(BaseModel):
    vehicle_id: int
    description: str
    cost: float
# --- AUTHENTICATION MODELS ---

class UserCreate(BaseModel):
    email: str
    password: str
    role: str  # Fleet Manager, Driver, Safety Officer, Financial Analyst

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str