from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemamodels
from database.database import get_db

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

@router.post("/log")
def log_maintenance(maint: schemamodels.MaintenanceCreate, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == maint.vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
        
    if vehicle.status == "On Trip":
        raise HTTPException(status_code=400, detail="Cannot perform maintenance on a vehicle currently On Trip")
        
    # Automated State Transition
    vehicle.status = "In Shop"
    
    # Optional: If Karan made a MaintenanceLog table, this saves the log
    if hasattr(models, "MaintenanceLog"):
        new_log = models.MaintenanceLog(**maint.model_dump(), status="Open")
        db.add(new_log)
        
    db.commit()
    return {"message": "Vehicle placed In Shop for maintenance"}

@router.post("/{log_id}/close")
def close_maintenance(log_id: int, db: Session = Depends(get_db)):
    if not hasattr(models, "MaintenanceLog"):
        raise HTTPException(status_code=501, detail="MaintenanceLog table not implemented yet")

    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.id == log_id).first()
    if not log or log.status == "Closed":
        raise HTTPException(status_code=400, detail="Log not found or already closed")
        
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == log.vehicle_id).first()
    
    if vehicle and vehicle.status != "Retired":
        vehicle.status = "Available"
        
    log.status = "Closed"
    db.commit()
    return {"message": "Maintenance closed, vehicle is now Available"}