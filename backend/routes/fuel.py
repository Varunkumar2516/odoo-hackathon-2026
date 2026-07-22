from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import FuelLog, Vehicle,UserModel,Trip,MaintenanceLog
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

        trip_id=log.trip_id,

        maintenance_id=log.maintenance_id,

        date=log.date,

        liters_filled=log.liters_filled,

        fuel_cost=log.fuel_cost

    )

    for log in logs
]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_fuel_log(
    fuel: FuelCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(oauth2.get_current_user)
):


    if current_user.role not in ["administrators", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create fuel logs."
        )


    context_count = sum([
        fuel.vehicle_id is not None,
        fuel.trip_id is not None,
        fuel.maintenance_id is not None
    ])

    if context_count != 1:
        raise HTTPException(
            status_code=400,
            detail="Exactly one fuel context must be selected."
        )

   
    if fuel.vehicle_id is not None:

        vehicle = db.query(Vehicle).filter(
            Vehicle.vehicle_id == fuel.vehicle_id
        ).first()

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found."
            )

   
    elif fuel.trip_id is not None:

        trip = db.query(Trip).filter(
            Trip.trip_id == fuel.trip_id
        ).first()

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found."
            )

        if trip.status != "Dispatched":
            raise HTTPException(
                status_code=400,
                detail="Fuel can only be added to dispatched trips."
            )

        vehicle = trip.vehicle

        # Automatically store vehicle
        fuel.vehicle_id = vehicle.vehicle_id


    elif fuel.maintenance_id is not None:

        maintenance = db.query(MaintenanceLog).filter(
            MaintenanceLog.maintenance_id == fuel.maintenance_id
        ).first()

        if not maintenance:
            raise HTTPException(
                status_code=404,
                detail="Maintenance record not found."
            )

        if maintenance.status != "Active":
            raise HTTPException(
                status_code=400,
                detail="Fuel can only be added to active maintenance."
            )

        vehicle = maintenance.vehicle

        # Automatically store vehicle
        fuel.vehicle_id = vehicle.vehicle_id

        # Optional:
        # If maintenance belongs to a trip,
        # automatically copy the trip_id.
        if maintenance.trip_id:
            fuel.trip_id = maintenance.trip_id

    # -------------------------------
    # Save Fuel Log
    # -------------------------------
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
    current_user: UserModel = Depends(oauth2.get_current_user)
):

    # -------------------------------
    # Authorization
    # -------------------------------
    if current_user.role not in ["administrators", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can update fuel logs."
        )

    # -------------------------------
    # Find Fuel Log
    # -------------------------------
    log = db.query(FuelLog).filter(
        FuelLog.fuel_log_id == fuel_log_id
    ).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Fuel log not found."
        )

    # -------------------------------
    # Validate Context
    # -------------------------------
    context_count = sum([
        fuel.vehicle_id is not None,
        fuel.trip_id is not None,
        fuel.maintenance_id is not None
    ])

    if context_count != 1:
        raise HTTPException(
            status_code=400,
            detail="Exactly one fuel context must be selected."
        )

    # -------------------------------
    # General Refueling
    # -------------------------------
    if fuel.vehicle_id is not None:

        vehicle = db.query(Vehicle).filter(
            Vehicle.vehicle_id == fuel.vehicle_id
        ).first()

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found."
            )

        fuel.trip_id = None
        fuel.maintenance_id = None

    # -------------------------------
    # Trip Refueling
    # -------------------------------
    elif fuel.trip_id is not None:

        trip = db.query(Trip).filter(
            Trip.trip_id == fuel.trip_id
        ).first()

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found."
            )

        if trip.status != "Dispatched":
            raise HTTPException(
                status_code=400,
                detail="Fuel can only be assigned to dispatched trips."
            )

        fuel.vehicle_id = trip.vehicle_id
        fuel.maintenance_id = None

    # -------------------------------
    # Maintenance Refueling
    # -------------------------------
    elif fuel.maintenance_id is not None:

        maintenance = db.query(MaintenanceLog).filter(
            MaintenanceLog.maintenance_id == fuel.maintenance_id
        ).first()

        if not maintenance:
            raise HTTPException(
                status_code=404,
                detail="Maintenance record not found."
            )

        if maintenance.status != "Active":
            raise HTTPException(
                status_code=400,
                detail="Fuel can only be assigned to active maintenance."
            )

        fuel.vehicle_id = maintenance.vehicle_id

        if maintenance.trip_id:
            fuel.trip_id = maintenance.trip_id
        else:
            fuel.trip_id = None

    # -------------------------------
    # Update Record
    # -------------------------------
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