from fastapi import APIRouter, Depends, HTTPException ,Response ,status
from sqlalchemy.orm import Session
from datetime import date
import backend.models as models
import backend.schemamodels as schemamodels
from backend.database import get_db 
from backend import oauth2
router = APIRouter(prefix="/api", tags=["Trips"])

# for Validation
def validate_trip(vehicle, driver, cargo_weight):
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Driver not found.")

    if vehicle.status != "Available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Vehicle is not available.")

    if driver.status != "Available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Driver is not available.")

    if driver.license_expiry_date < date.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Driver license has expired.")

    if cargo_weight > vehicle.max_load_capacity_kg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = f"Maximum load is {vehicle.max_load_capacity_kg} kg."
        )
    

# get Users
@router.get("/trips", response_model=list[schemamodels.TripResponse])
def get_trips(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
    
    trips = db.query(models.Trip).all()

    result = []

    for trip in trips:

        result.append({

            "trip_id": trip.trip_id,

            "source": trip.source,

            "destination": trip.destination,

            "vehicle_id": trip.vehicle_id,

            "driver_id": trip.driver_id,

            "vehicle": trip.vehicle.registration_number,

            "driver": trip.driver.user.name,

            "cargo_weight_kg": trip.cargo_weight_kg,

            "planned_distance_km": trip.planned_distance_km,

            "status": trip.status,

            "created_at": trip.created_at

        })

    return result

# create New Trip
@router.post("/trips", response_model=schemamodels.TripResponse)
def create_trip(
    data: schemamodels.TripCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)):

    # only Administrators Can Create the Trips
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Create trip."
        )
    # vehicle 
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_id == data.vehicle_id
    ).first()
    # driver
    driver = db.query(models.Driver).filter(
        models.Driver.driver_id == data.driver_id
    ).first()
    # Validating the Vehicle and driver
    validate_trip(vehicle=vehicle,driver=driver,cargo_weight=data.cargo_weight_kg)
    
    trip = models.Trip(

    trip_id=data.trip_id,

    source=data.source,

    destination=data.destination,

    vehicle_id=data.vehicle_id,

    driver_id=data.driver_id,

    cargo_weight_kg=data.cargo_weight_kg,

    planned_distance_km=data.planned_distance_km,

    status="Draft"
)

    db.add(trip)

    db.commit()

    db.refresh(trip)

    return {
    "trip_id": trip.trip_id,
    "source": trip.source,
    "destination": trip.destination,

    "vehicle_id": trip.vehicle_id,
    "driver_id": trip.driver_id,

    "vehicle": vehicle.registration_number,
    "driver": driver.user.name,

    "cargo_weight_kg": trip.cargo_weight_kg,
    "planned_distance_km": trip.planned_distance_km,

    "status": trip.status,

    "created_at": trip.created_at
}


# updating the Trips 
# only the Drafted Trips can be Edited , Dispatched and Completed trips cannot be edited
@router.put("/trips/{trip_id}",response_model=schemamodels.TripResponse)
def update_trip(
    trip_id: str,
    data: schemamodels.TripUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
    # only Administrators Can Create the Trips
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Edit trip."
        )
    trip = db.query(models.Trip).filter(
        models.Trip.trip_id == trip_id
    ).first()

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found."
        )
    if trip.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Only Draft trips can be edited."
        )
    
    
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_id == data.vehicle_id
    ).first()
    
    
    driver = db.query(models.Driver).filter(
        models.Driver.driver_id == data.driver_id
    ).first()
    
     # Validating the Vehicle and driver
    validate_trip(vehicle=vehicle,driver=driver,cargo_weight=data.cargo_weight_kg)
    
    


    trip.source = data.source

    trip.destination = data.destination

    trip.vehicle_id = data.vehicle_id

    trip.driver_id = data.driver_id

    trip.cargo_weight_kg = data.cargo_weight_kg

    trip.planned_distance_km = data.planned_distance_km

    db.commit()

    db.refresh(trip)
    return {
        "trip_id": trip.trip_id,

        "source": trip.source,

        "destination": trip.destination,

        "vehicle_id": trip.vehicle_id,

        "driver_id": trip.driver_id,

        "vehicle": trip.vehicle.registration_number,

        "driver": trip.driver.user.name,

        "cargo_weight_kg": trip.cargo_weight_kg,

        "planned_distance_km": trip.planned_distance_km,

        "status": trip.status,

        "created_at": trip.created_at
    }




# delete Trip Api
@router.delete("/trips/{trip_id}")
def delete_trip( trip_id: str,db: Session = Depends(get_db),current_user: models.UserModel = Depends(oauth2.get_current_user)):
    # only Administrators Can Delete the Trips
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Delete trip."
        )
    trip = db.query(models.Trip).filter(
        models.Trip.trip_id == trip_id
    ).first()

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found."
        )

    if trip.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Only Draft trips can be deleted."
        )
    
    db.delete(trip)
    db.commit()
    return {''}




# dispatch Api
@router.patch("/trips/{trip_id}/dispatch")
def dispatch_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
     # only Administrators Can Delete the Trips
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Dispatch trip."
        )
    trip = db.query(models.Trip).filter(
        models.Trip.trip_id == trip_id
    ).first()

    if not trip:
        raise HTTPException(404, "Trip not found.")

    if trip.status != "Draft":
        raise HTTPException(400, "Only Draft trips can be dispatched.")

    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_id == trip.vehicle_id
    ).first()

    
    driver = db.query(models.Driver).filter(
        models.Driver.driver_id == trip.driver_id
    ).first()

    validate_trip(vehicle, driver, trip.cargo_weight_kg)

    trip.status = "Dispatched"
    vehicle.status = "On Trip"
    driver.status = "On Trip"

    db.commit()
    db.refresh(trip)

    return {
        "message": "Trip dispatched successfully.",
        "trip_id": trip.trip_id,
        "status": trip.status
    }



# complete Api
@router.patch("/trips/{trip_id}/complete")
def complete_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
     # only Administrators Can Delete the Trips
    if current_user.role not in ["administrators",'admin']:
        raise HTTPException(
        status_code=403,
        detail="Only administrators can Dispatch trip."
        )
    trip = db.query(models.Trip).filter(
        models.Trip.trip_id == trip_id
    ).first()

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found."
        )

    if trip.status != "Dispatched":
        raise HTTPException(
            status_code=400,
            detail="Only dispatched trips can be completed."
        )

    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_id == trip.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found."
        )

    driver = db.query(models.Driver).filter(
        models.Driver.driver_id == trip.driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found."
        )

    trip.status = "Completed"

    vehicle.status = "Available"

    driver.status = "Available"

    db.commit()

    db.refresh(trip)

    return {
        "message": "Trip completed successfully.",
        "trip_id": trip.trip_id,
        "status": trip.status
    }