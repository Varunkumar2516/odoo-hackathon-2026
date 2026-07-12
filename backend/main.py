
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

from .routes import user, vehicle, maintenance
from fastapi.middleware.cors import CORSMiddleware

# running statement to Create all MOdels From SQLalchemy 
models.Base.metadata.create_all(bind=engine)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)

app.include_router(vehicle.router)

app.include_router(maintenance.router)

@app.get('/')
def home():
    return {"safe Runningg"}