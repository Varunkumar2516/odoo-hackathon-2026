from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Import ALL your route files here
from routes import trips, maintenance, user, vehicles, drivers

app = FastAPI(title="TransitOps API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Register ALL your routes here so they appear in Swagger
app.include_router(trips.router)
app.include_router(maintenance.router)
app.include_router(user.router)
app.include_router(vehicles.router)
app.include_router(drivers.router)

@app.get("/")
def root():
    return {"status": "TransitOps API is successfully running"}