import psycopg2
from psycopg2.extras import RealDictCursor
import time
import os
from dotenv import load_dotenv
# Load variables from .env into the system environment
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "config.env"

load_dotenv(ENV_PATH)



#""" Modern Way to Connect with Databases Using ORM(sqlalchemy) """
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DB_URL = os.getenv('POSTGRE_SQL_URL')
if not SQLALCHEMY_DB_URL:
    print("Error with Importing SQL string ")
engine = create_engine(SQLALCHEMY_DB_URL,
                        connect_args={"connect_timeout": 10} )


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally :
        db.close()
        
