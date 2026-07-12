from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend import models, schemamodels
from backend.database import get_db

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance Logs"]
)

@router.get("/", response_model=List[schemamodels.MaintenanceLog]) 
def read_maintenance_logs(db: Session = Depends(get_db)):
    return db.query(models.MaintenanceLog).all()

@router.post("/", response_model=schemamodels.MaintenanceLog) 
def create_maintenance_log(log: schemamodels.MaintenanceLogCreate, db: Session = Depends(get_db)):
   
    db_log = models.MaintenanceLog(**log.dict()) 
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log