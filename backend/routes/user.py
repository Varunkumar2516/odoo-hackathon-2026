from fastapi import Depends, APIRouter, status, HTTPException, Response,Request ,Cookie
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemamodels import UserCreate,UserResponse,UserUpdate
from backend import models
from fastapi.responses import JSONResponse
from backend import oauth2
from backend.utils import hash,VerifyHash
router = APIRouter(
    prefix='/api',
    tags=['User']
)

@router.get('/users',response_model=List[UserResponse])
def getUsers(db : Session = Depends(get_db) ):
    Users = db.query(models.UserModel).all()
    return Users


@router.post('/users',response_model=UserResponse)
def createUser(data : UserCreate,
               db : Session = Depends(get_db) ,
               current_user : models.UserModel = Depends(oauth2.get_current_user)):
    # first Proving the Current User Identity
    if current_user.role not in  ["administrators",'admin']: 
       raise HTTPException(
        status_code=403,
        detail="Only administrators can create users."
        )

    # now checking the DB if the Email Already Exist 
    user_with_email = db.query(models.UserModel).filter(models.UserModel.email == data.email).first()
    if user_with_email:
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
    
    return created_user

@router.put('/users/{user_id}')
def createUser(user_id:int,
               data:UserUpdate,
               db : Session = Depends(get_db) ,
               current_user : models.UserModel = Depends(oauth2.get_current_user)):
    
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Delete users."
        )

    user = db.query(models.UserModel).filter(models.UserModel.user_id==user_id)
    required_user = user.first()
    if required_user == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='No Any User Exist.')
    
    if required_user.role.lower() =='driver':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='Cannot Change Role Of Driver.')
    user.update(data.model_dump(),synchronize_session=False)
    db.commit()
    db.refresh(required_user)
    return required_user
 

@router.delete('/users/{user_id}')
def deleteUser(user_id:int ,
               db : Session = Depends(get_db) ,
               current_user : models.UserModel = Depends(oauth2.get_current_user)):
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Delete users."
        )

    deleted_user = db.query(models.UserModel).filter(models.UserModel.user_id == user_id).first()
    if deleted_user.role.lower() =='driver':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='Cannot Delete Driver From here.')
    if not deleted_user:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='No Any User Exist.')
    
    db.delete(deleted_user)
    db.commit()
    print('userDeleted')
    return {'userDeleted':"success"}

 