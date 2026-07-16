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
    email: str
    contact_number: str
    license_number:str
    license_category:str
    license_expiry_date:date
    safety_score:float=100
    password: str
    status:Literal[
        "Available",
        "On Trip",
        "Off Duty",
        "Suspended"
    ] = "Available"

class DriverCreate(DriverBase):
    pass
   


class DriverUpdate(DriverBase):
    pass


class DriverResponse(BaseModel):
    driver_id: int
    user_id: int
    name: str
    email: str
    contact_number: str
    license_number: str
    license_category: str
    license_expiry_date: date
    safety_score: float
    status: str
    model_config = ConfigDict(from_attributes=True)

class VehicleCreate(BaseModel):
    reg_number: str
    model: str
    type: str
    max_load: float
    acquisition_cost: float


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
    role: Literal['Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst', 'admin','Driver'] 
    name:str
    contact_number:str
    

class UserResponse(BaseModel):
    user_id: int
    name:str
    email: str
    role: str
    contact_number:Optional[str] = None

    class Config:
        from_attributes = True
class UserUpdate(BaseModel):
    name:str
    email:str
    role:str
    contact_number: str

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
