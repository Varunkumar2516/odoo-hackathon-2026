from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
import backend.models as models
import backend.schemamodels as schemamodels
from backend.database import get_db 

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("", response_model=list[schemamodels.DriverResponse])
def get_drivers(db: Session = Depends(get_db)):

    drivers = db.query(models.Driver).all()

    return drivers
@router.post("/")
def register_driver(driver: schemamodels.DriverCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Driver).filter(models.Driver.license_number == driver.license_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Driver with this license number already exists")
        
    new_driver = models.Driver(**driver.model_dump(), status="Available")
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return {"message": "Driver registered successfully", "driver": new_driver}

@router.get("/")
def get_all_drivers(db: Session = Depends(get_db)):
    drivers = db.query(models.Driver).all()
    return drivers


@router.get("/{driver_id}", response_model=schemamodels.DriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_db)):

    driver = db.query(models.Driver).filter(
        models.Driver.driver_id == driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    return 
    
@router.post(
    "",
    response_model=schemamodels.DriverResponse,
    status_code=status.HTTP_201_CREATED
)
def create_driver(
    data: schemamodels.DriverCreate,
    db: Session = Depends(get_db)
):

    existing_license = db.query(models.Driver).filter(
        models.Driver.license_number == data.license_number
    ).first()

    if existing_license:
        raise HTTPException(
            status_code=400,
            detail="License already exists"
        )

    existing_phone = db.query(models.Driver).filter(
        models.Driver.phone == data.phone
    ).first()

    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Phone already exists"
        )

    driver = models.Driver(**data.model_dump())

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return driver







@router.put("/{driver_id}", response_model=schemamodels.DriverResponse)
def update_driver(
    driver_id: int,
    data: schemamodels.DriverUpdate,
    db: Session = Depends(get_db)
):

    driver = db.query(models.Driver).filter(
        models.Driver.driver_id == driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    for key, value in data.model_dump().items():
        setattr(driver, key, value)

    db.commit()
    db.refresh(driver)

    return driver




@router.delete("/{driver_id}")
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db)
):

    driver = db.query(models.Driver).filter(
        models.Driver.driver_id == driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    db.delete(driver)
    db.commit()

    return {
        "message": "Driver deleted successfully"
    }