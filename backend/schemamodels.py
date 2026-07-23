from pydantic import BaseModel , EmailStr , Field,ConfigDict
# import re
from datetime import datetime
from typing import Optional,Literal 
# from sqlalchemy.dialects.postgresql import UUID

from pydantic import BaseModel
from datetime import date
from typing import Optional

from pydantic import BaseModel

# User Models
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


# driver Models
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



#vehicles Models 
class VehicleCreate(BaseModel):
    registration_number: str
    name_model: str
    type: str
    max_load_capacity_kg: float
    acquisition_cost: float


class VehicleUpdate(BaseModel):
    registration_number: str
    name_model: str
    type: str
    max_load_capacity_kg : float
    acquisition_cost: float

class VehicleResponse(BaseModel):
    vehicle_id: int
    registration_number: str
    name_model: str
    type: str
    max_load_capacity_kg: float
    acquisition_cost: float
    created_at: datetime
    status:str
    model_config = {
        "from_attributes": True
    }


# trip Create Models
class TripCreate(BaseModel):

    trip_id: str

    source: str

    destination: str

    vehicle_id: int

    driver_id: int

    cargo_weight_kg: float

    planned_distance_km: float
    estimated_cost: float
    status: Literal[
        "Draft",
        "Dispatched",
        "Completed",
        "Cancelled"
    ] = "Draft"


class TripUpdate(BaseModel):

    source: str

    destination: str

    vehicle_id: int

    driver_id: int

    cargo_weight_kg: float
    estimated_cost: float
    planned_distance_km: float

class TripResponse(BaseModel):

    trip_id: str

    source: str

    destination: str

    vehicle_id: int

    driver_id: int
    estimated_cost: float
    vehicle: str

    driver: str

    cargo_weight_kg: float

    planned_distance_km: float

    status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )





class MaintenanceCreate(BaseModel):

    vehicle_id: int

    service_type: str

    service_date: date

    cost: float

    status: Literal[
        "Active",
        "Closed"
    ] = "Active"


class MaintenanceUpdate(BaseModel):

    vehicle_id: int

    service_type: str

    service_date: date

    cost: float


class MaintenanceResponse(BaseModel):

    maintenance_id: int

    vehicle_id: int

    vehicle: str

    service_type: str

    service_date: date

    cost: float

    status: str

    model_config = ConfigDict(
        from_attributes=True
    )




class FuelCreate(BaseModel):
    trip_id: Optional[str]=None
    maintenance_id: Optional[int]=None

    vehicle_id:Optional[int] = None

    date: date

    liters_filled: float

    fuel_cost: float


class FuelUpdate(BaseModel):
    trip_id: Optional[str]=None
    maintenance_id: Optional[int]=None
    
    vehicle_id:Optional[int] = None

    date: date

    liters_filled: float

    fuel_cost: float


class FuelResponse(BaseModel):

    fuel_log_id:int

    vehicle_id:int

    vehicle:str

    name_model:str

    trip_id: Optional[str] = None

    maintenance_id: Optional[int] = None

    date:date

    liters_filled:float

    fuel_cost:float
    model_config = ConfigDict(
        from_attributes=True
    )


class ExpenseCreate(BaseModel):
    vehicle_id: int
    trip_id: Optional[str] = None
    expense_type: str
    amount: float
    date: date

class ExpenseUpdate(BaseModel):
    vehicle_id: int
    trip_id: Optional[str] = None
    expense_type: str
    amount: float
    date: date
    
class ExpenseResponse(BaseModel):
    expense_id: int

    vehicle_id: int
    vehicle: str
    name_model: str

    trip_id: Optional[str] = None

    expense_type: str
    amount: float
    date: date

    model_config = ConfigDict(from_attributes=True)


# --- AUTHENTICATION MODELS ---



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
