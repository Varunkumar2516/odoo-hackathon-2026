from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
import backend.models as models
import backend.schemamodels as schemamodels
from backend.database import get_db 
from typing import List
from backend import oauth2
router = APIRouter(prefix="/api", tags=["Vehicles"])

# get All vehicles
@router.get('/vehicles',response_model=List[schemamodels.VehicleResponse])
def get_vehicle(db:Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles

# Register New Vehicle
@router.post('/vehicles')
def register_vehicle( vehicledata : schemamodels.VehicleCreate,
                     db: Session = Depends(get_db),
                     current_user :models.UserModel = Depends(oauth2.get_current_user)):

    if current_user.role not in ["admin", "administrators"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create vehicles."
        )  

    existed_vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.registration_number == vehicledata.registration_number
    ).first()

    if existed_vehicle:
        raise HTTPException(
            status_code=409,
            detail="Vehicle already exists."
        )
    vehicle = models.Vehicle(**vehicledata.model_dump())

    db.add(vehicle)

    db.commit()

    db.refresh(vehicle)

    return vehicle          



# update vehicle
@router.put(
    "/vehicles/{vehicle_id}",
    response_model=schemamodels.VehicleResponse
)
def update_vehicle(
    vehicle_id: int,
    data: schemamodels.VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):

    if current_user.role not in ["admin", "administrators"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can update vehicles."
        )

    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_id == vehicle_id
    )

    existing = vehicle.first()

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found."
        )

    vehicle.update(
        data.model_dump(exclude_unset=True),
        synchronize_session=False
    )

    db.commit()

    db.refresh(existing)

    return existing

# delete Vehicle
@router.delete("/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
    try:
        if current_user.role not in ["admin", "administrators"]:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can delete vehicles."
            )

        vehicle = db.query(models.Vehicle).filter(
            models.Vehicle.vehicle_id == vehicle_id
        ).first()

        if vehicle is None:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found."
            )

        db.delete(vehicle)

        db.commit()

        return {
            "message": "Vehicle deleted successfully."
        }
    except Exception as e:
        
        raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Cannot Delete vehicle due to {e}"
            ) 
        



# load All available Vehicles
@router.get("/vehicles/available", response_model=list[schemamodels.VehicleResponse])
def get_available_vehicles(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):

    vehicles = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.status == "Available")
        .all()
    )

    return vehicles