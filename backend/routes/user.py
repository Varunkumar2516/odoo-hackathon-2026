from fastapi import Depends, APIRouter, status, HTTPException, Response,Request
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemamodels import UserCreate, UserResponse,UserLogin,LoginResponse
from backend import models


from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from backend.utils import hash,VerifyHash
router = APIRouter(
    tags=['User']
)

@router.post('/signup', status_code=status.HTTP_201_CREATED,response_model=UserResponse)
async def CreateUser(data: UserCreate, db: Session = Depends(get_db)):
    
    # 1. Check if email already exists
    user_with_email = db.query(models.UserModel).filter(models.UserModel.email == data.email).first()

    if user_with_email :
        if user_with_email.is_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Email Already Exists'
            )
        else:
            db.delete(user_with_email)
            db.commit()


    # 2. Hash password and update payload
    hashed_password = hash(data.password)
    user_dict = data.model_dump()
    user_dict["password"] = hashed_password
    
    # 3. Initialize DB Model
    created_user = models.UserModel(**user_dict)
    db.add(created_user)
    db.commit()
    db.refresh(created_user)

    return created_user

@router.post('/login', status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def LoginUser(data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(models.UserModel).filter(models.UserModel.email == data.email).first()
    
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    is_password_correct = VerifyHash(data.password, user.password)
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    
    dummy_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_session_token"

    return {
        "message": "Welcome back!",
        "access_token": dummy_token,
        "token_type": "bearer",
        "user": user
    }