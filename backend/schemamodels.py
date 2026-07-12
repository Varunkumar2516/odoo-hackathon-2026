from pydantic import BaseModel , EmailStr , Field,ConfigDict
import re
from datetime import datetime
from typing import Optional,Literal 
from sqlalchemy.dialects.postgresql import UUID

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
