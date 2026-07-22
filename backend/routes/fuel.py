from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import FuelLog, Vehicle,UserModel
from backend import oauth2
from backend.schemamodels import (
    FuelCreate,
    FuelUpdate,
    FuelResponse,
    
)

router = APIRouter(
    prefix="/api/fuel",
    tags=["Fuel Logs"]
)


@router.get("/",response_model=list[FuelResponse])
def get_fuel_logs(db: Session = Depends(get_db),
    current_user: UserModel = Depends(oauth2.get_current_user)):

    logs = db.query(FuelLog).all()

    return [
    FuelResponse(

        fuel_log_id=log.fuel_log_id,

        vehicle_id=log.vehicle_id,

        vehicle=log.vehicle.registration_number,

        name_model=log.vehicle.name_model,

        date=log.date,

        liters_filled=log.liters_filled,

        fuel_cost=log.fuel_cost

    )
    for log in logs]

@router.post("/",status_code=status.HTTP_201_CREATED)
def create_fuel_log(fuel: FuelCreate,db: Session = Depends(get_db),
    current_user: UserModel = Depends(oauth2.get_current_user)):
    
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Fuel logs."
        )
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == fuel.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found."
        )

    new_log = FuelLog(
        **fuel.model_dump()
    )

    db.add(new_log)

    db.commit()

    db.refresh(new_log)

    return {
        "message": "Fuel log created successfully."
    }




@router.put("/{fuel_log_id}")
def update_fuel_log(
    fuel_log_id: int,
    fuel: FuelUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(oauth2.get_current_user)):
    
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators Update fuel Logs."
        )
    log = db.query(FuelLog).filter(
        FuelLog.fuel_log_id == fuel_log_id
    ).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Fuel log not found."
        )

    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == fuel.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found."
        )

    for key, value in fuel.model_dump().items():

        setattr(log, key, value)

    db.commit()

    db.refresh(log)

    return {
        "message": "Fuel log updated successfully."
    }

@router.delete( "/{fuel_log_id}")
def delete_fuel_log(
    fuel_log_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(oauth2.get_current_user)
):
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Delete Fuel logs."
        )
    log = db.query(FuelLog).filter(
        FuelLog.fuel_log_id == fuel_log_id
    ).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Fuel log not found."
        )

    db.delete(log)

    db.commit()

    return {
        "message": "Fuel log deleted successfully."
    }