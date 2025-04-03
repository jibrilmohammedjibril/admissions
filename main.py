from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import os
from datetime import timedelta
import shutil
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, engine
import models, schemas, auth
from models import Base
from dotenv import load_dotenv

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Admission System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        program=user.program,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "id": user.uuid,
            "program": user.program,
            "full_name": user.full_name
        }
    }


@app.post("/application/upload", response_model=schemas.Application)
async def upload_application(
    nationality: str,
    address: str,
    transcript: UploadFile = File(...),
    certificate: UploadFile = File(...),
    statement_of_purpose: UploadFile = File(...),
    uuid: Optional[str] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Generate new UUID if not provided
    if not uuid:
        uuid = str(uuid.uuid4())
    
    # Create application directory
    app_dir = os.path.join(UPLOAD_DIR, uuid)
    os.makedirs(app_dir, exist_ok=True)
    
    # Save files
    transcript_path = os.path.join(app_dir, f"transcript_{transcript.filename}")
    certificate_path = os.path.join(app_dir, f"certificate_{certificate.filename}")
    sop_path = os.path.join(app_dir, f"sop_{statement_of_purpose.filename}")
    
    with open(transcript_path, "wb") as buffer:
        shutil.copyfileobj(transcript.file, buffer)
    with open(certificate_path, "wb") as buffer:
        shutil.copyfileobj(certificate.file, buffer)
    with open(sop_path, "wb") as buffer:
        shutil.copyfileobj(statement_of_purpose.file, buffer)
    
    # Check if application with UUID exists
    existing_app = db.query(models.Application).filter(models.Application.uuid == uuid).first()
    
    if existing_app:
        # Update existing application
        existing_app.nationality = nationality
        existing_app.address = address
        existing_app.transcript_path = transcript_path
        existing_app.certificate_path = certificate_path
        existing_app.statement_of_purpose_path = sop_path
        db.commit()
        db.refresh(existing_app)
        return existing_app
    
    # Create new application
    db_application = models.Application(
        uuid=uuid,
        user_id=current_user.id,
        nationality=nationality,
        address=address,
        transcript_path=transcript_path,
        certificate_path=certificate_path,
        statement_of_purpose_path=sop_path
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.get("/application/{uuid}", response_model=schemas.Application)
def get_application(
    uuid: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    application = db.query(models.Application).filter(models.Application.uuid == uuid).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return application


