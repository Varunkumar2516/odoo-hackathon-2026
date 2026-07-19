from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
import backend.models as models
import backend.schemamodels as schemamodels
from backend.database import get_db 
from typing  import List
from backend import oauth2
from backend import schemamodels
from backend.utils import hash,VerifyHash
router = APIRouter(prefix="/api", tags=["Drivers"])

# helper Function for Driver Data 
def Helper(driver):
    return {"driver_id": driver.driver_id,

            "user_id": driver.user_id,

            "name": driver.user.name,

            "email": driver.user.email,

            "contact_number": driver.user.contact_number,

            "license_number": driver.license_number,

            "license_category": driver.license_category,

            "license_expiry_date": driver.license_expiry_date,

            "safety_score": driver.safety_score,

            "status": driver.status}


# get ALl Drivers
@router.get('/drivers',response_model=list[schemamodels.DriverResponse])
def getDrivers(db:Session = Depends(get_db),
               current_user = Depends(oauth2.get_current_user)):
    
    drivers = db.query(models.Driver).all()

    result = []

    for driver in drivers:

        result.append(Helper(driver))

    return result
    

# create Driver 
from sqlalchemy.exc import SQLAlchemyError

@router.post("/drivers", response_model=schemamodels.DriverResponse)
def create_driver(
    data: schemamodels.DriverCreate,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
    if current_user.role not in ["admin", "administrators"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create drivers."
        )

    # Check if user already exists
    user = db.query(models.UserModel).filter(
        models.UserModel.email == data.email
    ).first()

    if user:
        raise HTTPException(
            status_code=409,
            detail="User already exists."
        )

    # Check if license already exists
    license_exists = db.query(models.Driver).filter(
        models.Driver.license_number == data.license_number
    ).first()

    if license_exists:
        raise HTTPException(
            status_code=409,
            detail="License already exists."
        )

    try:
        # Create User
        new_user = models.UserModel(
            name=data.name,
            email=data.email,
            password=hash(data.password),
            contact_number=data.contact_number,
            role="Driver"
        )

        db.add(new_user)
        db.flush()          # Generates user_id without committing

        # Create Driver
        driver = models.Driver(
            user_id=new_user.user_id,
            license_number=data.license_number,
            license_category=data.license_category,
            license_expiry_date=data.license_expiry_date,
            safety_score=data.safety_score,
            status=data.status
        )

        db.add(driver)

        # Commit both together
        db.commit()

        db.refresh(driver)

        return Helper(driver)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected Error: {str(e)}"
        )



@router.put("/drivers/{driver_id}", response_model=schemamodels.DriverResponse)
def update_driver(
    driver_id: int,
    data: schemamodels.DriverUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
    if current_user.role not in ["admin", "administrators"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create drivers.")
    driver = db.query(models.Driver).filter(models.Driver.driver_id == driver_id).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found."
        )
    
    duplicate = db.query(models.Driver).filter(models.Driver.license_number == data.license_number
                                               ,models.Driver.driver_id != driver_id).first()

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="License already exists."
        )
    for key, value in data.model_dump().items():
         setattr(driver, key, value)

    db.commit()

    db.refresh(driver)

    return Helper(driver)

@router.delete("/drivers/{driver_id}")
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
    if current_user.role not in ["admin", "administrators"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create drivers."
        )
    
    driver = db.query(models.Driver).filter(
    models.Driver.driver_id == driver_id).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found."
        )
    
    db.delete(driver)

    db.commit()

    return {
        "message": "Driver deleted successfully."
}



# load only Available Drivers
@router.get("/drivers/available", response_model=list[schemamodels.DriverResponse])
def get_available_drivers(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(oauth2.get_current_user)
):
    
    drivers = (
        db.query(models.Driver)
        .filter(models.Driver.status == "Available")
        .all()
    )
    result = []

    for driver in drivers:

        result.append(Helper(driver))
    return result