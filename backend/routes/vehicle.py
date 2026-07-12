from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemamodels
from backend.database import get_db

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles Registry"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemamodels.VehicleResponse)
def create_vehicle(vehicle: schemamodels.VehicleCreate, db: Session = Depends(get_db)):
    
    existing_vehicle = db.query(models.Vehicle).filter(models.Vehicle.registration_number == vehicle.registration_number).first()
    if existing_vehicle:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Yeh Registration Number already exist karta hai!")
    
    new_vehicle = models.Vehicle(**vehicle.model_dump())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle


@router.get("/", response_model=List[schemamodels.VehicleResponse])
def get_all_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles