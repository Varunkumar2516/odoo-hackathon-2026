from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Import ALL your route files here
from backend.routes import trips, maintenance, user, vehicles, drivers,auth,fuel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend import models
from backend.database import engine 
models.Base.metadata.create_all(bind = engine)

app = FastAPI(title="TransitOps API")


# 2. Register ALL your routes here so they appear in Swagger
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(drivers.router)

app.include_router(trips.router)
app.include_router(maintenance.router)

app.include_router(vehicles.router)
app.include_router(fuel.router)




app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mouting the Static Folder here
app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)

@app.get("/")
def home():
    return {"safe Running ":'Varun app'}
# login Page 
@app.get('/login')
def login():
    return FileResponse("frontend/login.html")

# dashboard Page 
@app.get('/dashboard')
def dashboard():
    return FileResponse("frontend/dashboard.html")

# users 
@app.get('/users')
def Users():
    return FileResponse('frontend/users.html')


@app.get('/drivers')
def drivers():
    return FileResponse('frontend/drivers.html')

@app.get('/vehicles')
def Vehicles():
    return FileResponse("frontend/vehicles.html")


@app.get('/trips')
def trips():
    return FileResponse("frontend/trips.html")

@app.get('/maintainence')
def maintainence():
    return FileResponse("frontend/maintainence.html")

@app.get('/fuels')
def maintainence():
    return FileResponse("frontend/fuellogs.html")
