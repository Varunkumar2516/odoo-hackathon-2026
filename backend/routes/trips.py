from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import models
import schemamodels
from database.database import get_db 

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("/dispatch")
def dispatch_trip(trip: schemamodels.TripCreate, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == trip.vehicle_id).first()
    driver = db.query(models.Driver).filter(models.Driver.id == trip.driver_id).first()

    if not vehicle or not driver:
        raise HTTPException(status_code=404, detail="Vehicle or Driver not found")

    if trip.cargo_weight > vehicle.max_load:
        raise HTTPException(status_code=400, detail=f"Cargo weight exceeds vehicle capacity of {vehicle.max_load}kg")

    if vehicle.status != "Available" or driver.status != "Available":
        raise HTTPException(status_code=400, detail="Vehicle or Driver is not Available")

    if driver.license_expiry < date.today():
        raise HTTPException(status_code=400, detail="Driver license is expired")

    # Automated State Transition
    new_trip = models.Trip(**trip.model_dump(), status="Dispatched")
    vehicle.status = "On Trip"
    driver.status = "On Trip"

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return {"message": "Trip dispatched successfully", "trip": new_trip}

@router.post("/{trip_id}/complete")
def complete_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    
    if not trip or trip.status != "Dispatched":
        raise HTTPException(status_code=400, detail="Invalid trip or already completed")

    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == trip.vehicle_id).first()
    driver = db.query(models.Driver).filter(models.Driver.id == trip.driver_id).first()

    # Automated State Transition back to Available
    trip.status = "Completed"
    if vehicle:
        vehicle.status = "Available"
    if driver:
        driver.status = "Available"

    db.commit()
    return {"message": "Trip completed, assets are now Available"}