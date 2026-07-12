from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend import models, schemamodels
from backend.database import get_db

router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.get("/", response_model=List[schemamodels.DriverResponse])
def get_drivers(db: Session = Depends(get_db)):
    return db.query(models.Driver).all()

@router.post("/", response_model=schemamodels.DriverResponse)
def add_driver(payload: schemamodels.DriverCreate, db: Session = Depends(get_db)):
    # Duplicate license check
    if db.query(models.Driver).filter(models.Driver.license_number == payload.license_number).first():
        raise HTTPException(status_code=400, detail="Driver with this license already exists")
        
    new_driver = models.Driver(**payload.model_dump())
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver