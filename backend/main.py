
# # Fast api Imports
# from fastapi import FastAPI,Body,Response,HTTPException,status,Depends

# # random Numberimport 
# from random import randrange

# from typing import List
# # datetime import
# from datetime import datetime, timezone


# # import models from SQLalchemy
# from . import models 
# from backend.database import engine,get_db
# from sqlalchemy.orm import Session


# from backend.schemamodels import UserCreate

# from .routes import user
# from fastapi.middleware.cors import CORSMiddleware

# # running statement to Create all MOdels From SQLalchemy 
# models.Base.metadata.create_all(bind=engine)



# app = FastAPI()

# app.include_router(user.router)


# @app.get('/')
# def home():
#     return {"safe Runningg"}
# ================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your route files
from routes import trips, maintenance,user

app = FastAPI(title="TransitOps API")

# Setup CORS to allow the frontend team to connect easily
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect the routers to the main application
app.include_router(trips.router)
app.include_router(maintenance.router)
app.include_router(user.router)
@app.get("/")
def root():
    return {"status": "TransitOps API is successfully running"}