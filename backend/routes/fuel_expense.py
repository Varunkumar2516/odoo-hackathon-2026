from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from backend import models, schemamodels
from backend.database import get_db

router = APIRouter(prefix="/fuel-expenses", tags=["Fuel & Expenses"])

@router.post("/fuel", response_model=schemamodels.FuelLogResponse)
def create_fuel_log(payload: schemamodels.FuelLogCreate, db: Session = Depends(get_db)):
    new_log = models.FuelLog(**payload.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.get("/fuel", response_model=List[schemamodels.FuelLogResponse])
def get_fuel_logs(db: Session = Depends(get_db)):
    return db.query(models.FuelLog).options(joinedload(models.FuelLog.vehicle)).all()

@router.post("/expenses", response_model=schemamodels.ExpenseResponse)
def create_expense(payload: schemamodels.ExpenseCreate, db: Session = Depends(get_db)):
    new_expense = models.Expense(**payload.model_dump())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/expenses", response_model=List[schemamodels.ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return db.query(models.Expense).options(joinedload(models.Expense.vehicle)).all()