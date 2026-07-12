from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import backend.models as models
import backend.schemamodels as schemamodels
from backend.database import get_db 
 
router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post("/")
def register_vehicle(vehicle: schemamodels.VehicleCreate, db: Session = Depends(get_db)):
    # Mandatory Rule: Vehicle registration number must be unique
    existing = db.query(models.Vehicle).filter(models.Vehicle.reg_number == vehicle.reg_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle with this registration number already exists")
        
    new_vehicle = models.Vehicle(**vehicle.model_dump(), status="Available")
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return {"message": "Vehicle registered successfully", "vehicle": new_vehicle}

@router.get("/")
def get_all_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles