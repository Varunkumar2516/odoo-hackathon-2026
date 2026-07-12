from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import backend.models as models
import backend.schemamodels as schemamodels
from backend.database import get_db 

router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.post("/")
def register_driver(driver: schemamodels.DriverCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Driver).filter(models.Driver.license_number == driver.license_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Driver with this license number already exists")
        
    new_driver = models.Driver(**driver.model_dump(), status="Available")
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return {"message": "Driver registered successfully", "driver": new_driver}

@router.get("/")
def get_all_drivers(db: Session = Depends(get_db)):
    drivers = db.query(models.Driver).all()
    return drivers