from fastapi import Depends, APIRouter, status, HTTPException, Response,Request ,Cookie
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemamodels import UserCreate, UserResponse,UserLogin,LoginResponse
from backend import models
from fastapi.responses import JSONResponse
from backend import oauth2
from backend.utils import hash,VerifyHash
router = APIRouter(
    prefix='/api',
    tags=['Authentication']
)

@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def CreateUser(data: UserCreate, db: Session = Depends(get_db)):
    
    # 1. Check if email already exists
    user_with_email = db.query(models.UserModel).filter(models.UserModel.email == data.email).first()

    if  user_with_email :
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Email Already Exists'
            )
    
    # 2. Hash password and update payload
    hashed_password = hash(data.password)
    user_dict = data.model_dump()
    user_dict["password"] = hashed_password
    
    # 3. Initialize DB Model
    created_user = models.UserModel(**user_dict)
    db.add(created_user)
    db.commit()
    db.refresh(created_user)

    return {'success':'Your Account Created'}

@router.post('/login', status_code=status.HTTP_200_OK)
async def LoginUser(data: UserLogin, db: Session = Depends(get_db)):
    print("LOGIN API CALLED")
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
        
    access_token = oauth2.create_access_token(user_id = user.user_id)[0]
    refresh_token,refresh_token_data = oauth2.create_refresh_token(user_id=user.user_id)

    response = JSONResponse({
        'message':'loginSuccess',
    })

    response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="Lax"
            )
    response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite="Lax"
            )
    print(response.headers)
    return response






@router.get("/me")
def me(access_token: str = Cookie(None), db: Session = Depends(get_db)):

    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = oauth2.verify_access_token(access_token)
        
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token {e}"
        )

    user = db.query(models.UserModel).filter(
        models.UserModel.user_id == payload.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return {
           "name":user.name
           }


@router.get('/logout')
def logout(response:Response):
    response.delete_cookie(
        key="access_token",   # <-- cookie ka exact naam
        path="/"
    )
    response.delete_cookie(
        key="refresh_token",   # <-- cookie ka exact naam
        path="/"
    )

    return {"message": "Logged out successfully"}