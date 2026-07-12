from jose import JWTError,jwt
import secrets 
from dotenv import load_dotenv
# Load variables from .env into the system environment
from pathlib import Path
import os
from backend import schemamodels, models
from fastapi import Depends,status,HTTPException,Request

# for extracting the token from authorization Request
from fastapi.security import OAuth2PasswordBearer,HTTPBearer


from sqlalchemy.orm import Session
from .database import get_db


from datetime import datetime,timedelta,timezone
from uuid import uuid4

basedir = Path(__file__).resolve().parent
finalpath = basedir / 'Config.env'
load_dotenv(finalpath)


SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
EMAIL_SECRET_KEY=os.getenv("EMAIL_SECRET_KEY") 
PASS_SECRET_KEY=os.getenv("PASS_SECRET_KEY") 
ALGORITHM = os.getenv("ALGORITHM")
ACCESSEXPIRATION=os.getenv("TOKEN_EXPIRE_IN_MINUTES",10) 
REFRESHEXPIRATION=os.getenv("REFRESH_EXPIRE_IN_MINUTES",43200) 
EMAILEXPIRATION = os.getenv("EMAIL_EXPIRATION_TIME")
PASSEXPIRATION = os.getenv("PASS_EXPIRATION_TIME")

# creation token Functions
def create_token(user_id :int ,token_type,minute,secret):
    to_encode = {
        'user_id':user_id,
        'type':token_type,
        'exp':datetime.now(timezone.utc) + timedelta(minutes=int(minute)),
        'iat':datetime.now(timezone.utc),
        'jti':str(uuid4())
    }

    
    return (jwt.encode(to_encode,
                      secret,
                      algorithm=ALGORITHM),schemamodels.TokenData(**to_encode))




def create_access_token(user_id : int):
    return create_token(user_id,token_type='access',minute=ACCESSEXPIRATION,secret=SECRET_KEY)

def create_refresh_token(user_id : int):
    return create_token(user_id,token_type='refresh',minute=REFRESHEXPIRATION,secret=REFRESH_SECRET_KEY)

def create_email_verify_token(user_id:int):
    return create_token(user_id,token_type='email-verify',minute=EMAILEXPIRATION,secret=EMAIL_SECRET_KEY)

def create_password_reset_token(user_id:int):
    return create_token(user_id,token_type='reset-password',minute=PASSEXPIRATION,secret=PASS_SECRET_KEY)

credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not Validate Credentials',
                                           headers={'WWW-Authenticate':'Bearer'})

# verify functions 

# simple function to find Payload
def decode_token(token:str,SECRET_KEY :str)-> dict:
    return jwt.decode(token,
            SECRET_KEY,
            algorithms=[ALGORITHM])


# overall verification of Token
def verify_token(token:str , token_type : str , SECRET_KEY):
    try: 
        payload = decode_token(token,SECRET_KEY)
        if payload is None:
            raise credentials_exception
        id: str = payload.get('user_id')
        type : str = payload.get('type')

        if id is None or type != token_type:
            raise credentials_exception
        
        token_data = schemamodels.TokenData(**payload)

        return token_data
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f'Could not Validate Credentials {str(e)}',
                                           headers={'WWW-Authenticate':'Bearer'})




def verify_access_token(token: str):
    return verify_token(
        token,
        "access",
        SECRET_KEY=SECRET_KEY
    )


def verify_refresh_token(token: str):
    return verify_token(
        token,
        "refresh",
        SECRET_KEY=REFRESH_SECRET_KEY
    )

def verify_email_token(token:str):
     return verify_token(
        token,
        "email-verify",
        SECRET_KEY=EMAIL_SECRET_KEY
    )

def verify_forget_password_token(token:str):
    return verify_token(
        token,
        'reset-password',
        SECRET_KEY=PASS_SECRET_KEY
    )


# for Cookie Based Authentication
def get_current_user(request : Request ,db:Session = Depends(get_db)):
     
     token = request.cookies.get("access_token")
     if not token:
        raise credentials_exception
     token_data = verify_access_token(token)

     current_user = db.query(models.UserModel).filter(models.UserModel.user_id == token_data.user_id).first()
     if not current_user:
         raise credentials_exception
     return current_user
    