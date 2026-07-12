from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemamodels

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=schemamodels.AnalyticsResponse)
def get_dashboard_data(db: Session = Depends(get_db)):
    # 1. Summary logic (Placeholder values, tum yahan database query use karna)
    summary = schemamodels.AnalyticsSummary(
        fuel_efficiency="8.4 km/l",
        fleet_utilization="81%",
        operational_cost=34070.0,
        vehicle_roi="14.2%"
    )
    
    # 2. Mock Data for charts (Database se data fetch karke yahan list dena)
    monthly_revenue = [12000, 15000, 11000, 18000, 14000, 20000]
    
    top_vehicles = [
        schemamodels.VehicleCost(vehicle_name="TRUCK-11", cost=25000),
        schemamodels.VehicleCost(vehicle_name="MINI-03", cost=15000),
        schemamodels.VehicleCost(vehicle_name="VAN-05", cost=8000)
    ]
    
    return {
        "summary": summary,
        "monthly_revenue": monthly_revenue,
        "top_costly_vehicles": top_vehicles
    }