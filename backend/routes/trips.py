from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend import models, schemamodels
from backend.database import get_db

router = APIRouter(prefix="/trips", tags=["Trip Dispatcher"])

@router.post("/", response_model=schemamodels.TripResponse)
def create_trip(payload: schemamodels.TripCreate, db: Session = Depends(get_db)):
    # Check if trip_id already exists
    if db.query(models.Trip).filter(models.Trip.trip_id == payload.trip_id).first():
        raise HTTPException(status_code=400, detail="Trip ID already exists")
        
    new_trip = models.Trip(**payload.model_dump(), status="Draft")
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip

@router.get("/", response_model=List[schemamodels.TripResponse])
def get_trips(db: Session = Depends(get_db)):
    return db.query(models.Trip).all()