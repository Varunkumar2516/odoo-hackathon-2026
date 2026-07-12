
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def home():
    return {"safe Runningg"}