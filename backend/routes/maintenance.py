from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import backend.models as models
import backend.schemamodels as schemamodels
from backend.database import get_db 
from backend import oauth2
router = APIRouter(prefix="/api", tags=["Maintenance"])



# get all Maintenance Record 
@router.get( "/maintenance",response_model=list[schemamodels.MaintenanceResponse])
def get_all_maintenance(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):

    logs = db.query(models.MaintenanceLog).all()

    result = []

    for log in logs:

        result.append({

            "maintenance_id": log.maintenance_id,

            "vehicle_id": log.vehicle_id,

            "vehicle": log.vehicle.registration_number,

            "service_type": log.service_type,

            "service_date": log.service_date,

            "cost": log.cost,

            "status": log.status

        })

    return result


#get one Maintenance Record 
@router.get("/maintenance/{maintenance_id}",response_model=schemamodels.MaintenanceResponse)
def get_one_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):

    log = db.query(models.MaintenanceLog).filter(

        models.MaintenanceLog.maintenance_id == maintenance_id

    ).first()

    if not log:

        raise HTTPException(
            status_code=404,
            detail="Maintenance log not found."
        )

    return {

        "maintenance_id": log.maintenance_id,

        "vehicle_id": log.vehicle_id,

        "vehicle": log.vehicle.registration_number,

        "service_type": log.service_type,

        "service_date": log.service_date,

        "cost": log.cost,

        "status": log.status

    }


@router.post("/maintenance",response_model=schemamodels.MaintenanceResponse)
def create_maintenance(
    data: schemamodels.MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):

    if current_user.role not in ["admin"]:

        raise HTTPException(

            status_code=403,

            detail="Only administrators can create maintenance logs."

        )

    vehicle = db.query(models.Vehicle).filter(

        models.Vehicle.vehicle_id == data.vehicle_id

    ).first()

    if not vehicle:

        raise HTTPException(

            status_code=404,

            detail="Vehicle not found."

        )

    if vehicle.status != "Available":

        raise HTTPException(

            status_code=400,

            detail="Vehicle is not available."

        )
    
    existing = db.query(models.MaintenanceLog).filter( models.MaintenanceLog.vehicle_id == data.vehicle_id,
    models.MaintenanceLog.status == "Active").first()

    if existing: 
       raise HTTPException(
                status_code=400,
                detail="Vehicle already has an active maintenance record."
            )
    log = models.MaintenanceLog(

        **data.model_dump()

    )

    vehicle.status = "In Shop"

    db.add(log)

    db.commit()

    db.refresh(log)

    return {

        "maintenance_id": log.maintenance_id,

        "vehicle_id": log.vehicle_id,

        "vehicle": vehicle.registration_number,

        "service_type": log.service_type,

        "service_date": log.service_date,

        "cost": log.cost,

        "status": log.status

    }

@router.put("/maintenance/{maintenance_id}",response_model=schemamodels.MaintenanceResponse)
def update_maintenance(
    maintenance_id: int,
    data: schemamodels.MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only administrators can update maintenance logs."
        )

    log = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.maintenance_id == maintenance_id
    ).first()

    if not log:

        raise HTTPException(
            status_code=404,
            detail="Maintenance log not found."
        )

    if log.status != "Active":

        raise HTTPException(
            status_code=400,
            detail="Completed maintenance cannot be edited."
        )

    vehicle = log.vehicle

    log.service_type = data.service_type
    log.service_date = data.service_date
    log.cost = data.cost

    db.commit()
    db.refresh(log)

    return {

        "maintenance_id": log.maintenance_id,

        "vehicle_id": log.vehicle_id,

        "vehicle": vehicle.registration_number,

        "service_type": log.service_type,

        "service_date": log.service_date,

        "cost": log.cost,

        "status": log.status

    }

# complete Maintenance
@router.patch("/maintenance/{maintenance_id}/complete")
def complete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only administrators can complete maintenance."
        )

    log = db.query(models.MaintenanceLog).filter(
        models.MaintenanceLog.maintenance_id == maintenance_id
    ).first()

    if not log:

        raise HTTPException(
            status_code=404,
            detail="Maintenance log not found."
        )

    if log.status == "Closed":

        raise HTTPException(
            status_code=400,
            detail="Maintenance already completed."
        )

    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_id == log.vehicle_id
    ).first()

    log.status = "Closed"

    if vehicle:

        vehicle.status = "Available"

    db.commit()

    return {

        "message": "Maintenance completed successfully."

    }


# delete Routes that are not completed
@router.delete("/maintenance/{maintenance_id}")
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete maintenance logs."
        )

    log = db.query(models.MaintenanceLog).filter(
        models.MaintenanceLog.maintenance_id == maintenance_id
    ).first()

    if not log:

        raise HTTPException(
            status_code=404,
            detail="Maintenance log not found."
        )

    if log.status == "Closed":

        raise HTTPException(
            status_code=400,
            detail="Completed maintenance logs cannot be deleted."
        )

    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_id == log.vehicle_id
    ).first()

    if vehicle:

        vehicle.status = "Available"

    db.delete(log)

    db.commit()

    return {

        "message": "Maintenance log deleted successfully."

    }