from pydantic import BaseModel , EmailStr , Field,ConfigDict
# import re
from datetime import datetime
from typing import Optional,Literal 
# from sqlalchemy.dialects.postgresql import UUID

from pydantic import BaseModel
from datetime import date
from typing import Optional

from pydantic import BaseModel

class DriverBase(BaseModel):
    name: str
    license_number: str
    license_category: str
    license_expiry_date: date
    contact_number: str
    safety_score: float = 100.0
    status: str = "Available"


class DriverCreate(DriverBase):
    pass


class DriverUpdate(DriverBase):
    pass


class DriverResponse(DriverBase):
    driver_id: int

    class Config:
        from_attributes = True
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
    name:str
    

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
    email:EmailStr



class TokenData(BaseModel):
    user_id : int 
    type : Literal["access", "refresh","email-verify",'reset-password']
    exp : datetime
    iat : datetime 
    jti : str

class CurrentUser(BaseModel):
    id:int 
    name:str

class refreshToken(BaseModel):
    refresh_token : str
