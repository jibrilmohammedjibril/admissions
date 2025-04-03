from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = "postgresql://admissions_tac1_user:vpNV7a86TTzN9KqUVsqaLBOgQ7ql07je@dpg-cvn9sqk9c44c73dkvr8g-a.oregon-postgres.render.com/admissions_tac1"

# Create engine with echo=True to see SQL statements
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
