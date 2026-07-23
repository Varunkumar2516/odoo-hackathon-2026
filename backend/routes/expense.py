from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from backend.models import UserModel,Expense,Vehicle,Driver,Trip
from backend.schemamodels import ExpenseCreate,ExpenseResponse,ExpenseUpdate
from backend.database import get_db 
from typing  import List
from backend import oauth2
from backend import schemamodels
from backend.utils import hash,VerifyHash
router = APIRouter(prefix="/api/expenses", tags=["Expense"])

@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(
    db: Session =Depends(get_db),
    current_user: UserModel =Depends(oauth2.get_current_user)
):

    expenses = db.query(Expense).all()

    return [

        ExpenseResponse(

            expense_id=expense.expense_id,

            vehicle_id=expense.vehicle_id,

            vehicle=expense.vehicle.registration_number,

            name_model=expense.vehicle.name_model,

            trip_id=expense.trip_id,

            expense_type=expense.expense_type,

            amount=expense.amount,

            date=expense.date

        )

        for expense in expenses

    ]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: ExpenseCreate,
    db: Session =Depends(get_db),
    current_user: UserModel =Depends(oauth2.get_current_user)
):

    if current_user.role not in ["administrators", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create expenses."
        )

    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == expense.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found."
        )

    if expense.trip_id:

        trip = db.query(Trip).filter(
            Trip.trip_id == expense.trip_id
        ).first()
        
        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found."
            )
        expense.vehicle_id = trip.vehicle_id

    new_expense = Expense(
        **expense.model_dump()
    )

    db.add(new_expense)

    db.commit()

    db.refresh(new_expense)

    return {
        "message": "Expense created successfully."
    }


@router.put("/{expense_id}")
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session =Depends(get_db),
    current_user: UserModel =Depends(oauth2.get_current_user)
):

    if current_user.role not in ["administrators", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can update expenses."
        )

    existing = db.query(Expense).filter(
        Expense.expense_id == expense_id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Expense not found."
        )

    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == expense.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found."
        )

    if expense.trip_id:

        trip = db.query(Trip).filter(
            Trip.trip_id == expense.trip_id
        ).first()

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found."
            )

    for key, value in expense.model_dump().items():
        setattr(existing, key, value)

    db.commit()

    db.refresh(existing)

    return {
        "message": "Expense updated successfully."
    }


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session =Depends(get_db),
    current_user: UserModel =Depends(oauth2.get_current_user)
):

    if current_user.role not in ["administrators", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete expenses."
        )

    expense = db.query(Expense).filter(
        Expense.expense_id == expense_id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found."
        )

    db.delete(expense)

    db.commit()

    return {
        "message": "Expense deleted successfully."
    }