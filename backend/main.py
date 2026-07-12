
# Fast api Imports
from fastapi import FastAPI,Body,Response,HTTPException,status,Depends

# random Numberimport 
from random import randrange

from typing import List
# datetime import
from datetime import datetime, timezone


# import models from SQLalchemy
from . import models 
from backend.database import engine,get_db
from sqlalchemy.orm import Session


from backend.schemamodels import UserCreate

from .routes import user
from fastapi.middleware.cors import CORSMiddleware

# running statement to Create all MOdels From SQLalchemy 
models.Base.metadata.create_all(bind=engine)



app = FastAPI()

app.include_router(user.router)


@app.get('/')
def home():
    return {"safe Runningg"}