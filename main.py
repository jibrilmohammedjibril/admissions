from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import os
from datetime import timedelta, datetime
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
        hashed_password=hashed_password,
        uuid=str(uuid.uuid4())
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
    
    # Get all user's applications
    applications = db.query(models.Application).filter(models.Application.user_id == user.id).all()
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "uuid": user.uuid,
            "program": user.program,
            "full_name": user.full_name
        },
        "applications": applications
    }

@app.post("/application/upload", response_model=schemas.Application)
async def upload_application(
    # Required Personal Details
    nationality: str,
    gender: str,
    date_of_birth: datetime,
    phone_number: str,
    street_address: str,
    city: str,
    country: str,
    
    # Academic Details
    academic_session: str,
    program_type: str,
    selected_program: str,
    
    # Academic Qualifications
    qualification_type: str,
    grade: str,
    cgpa: str,
    subject: str,
    awarding_institution: str,
    start_date: datetime,
    end_date: datetime,
    
    # References
    first_referee_name: str,
    first_referee_email: str,
    second_referee_name: str,
    second_referee_email: str,
    
    # Required Files
    passport_photo: UploadFile = File(...),
    transcript: UploadFile = File(...),
    certificate: UploadFile = File(...),
    statement_of_purpose: UploadFile = File(...),
    payment_receipt: UploadFile = File(...),
    
    # Optional Parameters
    state_of_origin: Optional[str] = None,
    has_disability: bool = False,
    disability_description: Optional[str] = None,
    other_qualifications: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Use the user's UUID
    application_uuid = current_user.uuid
    
    # Create application directory
    app_dir = os.path.join(UPLOAD_DIR, application_uuid)
    os.makedirs(app_dir, exist_ok=True)
    
    # Save files
    passport_photo_path = os.path.join(app_dir, f"passport_{passport_photo.filename}")
    transcript_path = os.path.join(app_dir, f"transcript_{transcript.filename}")
    certificate_path = os.path.join(app_dir, f"certificate_{certificate.filename}")
    sop_path = os.path.join(app_dir, f"sop_{statement_of_purpose.filename}")
    payment_receipt_path = os.path.join(app_dir, f"payment_{payment_receipt.filename}")
    
    # Save all files
    with open(passport_photo_path, "wb") as buffer:
        shutil.copyfileobj(passport_photo.file, buffer)
    with open(transcript_path, "wb") as buffer:
        shutil.copyfileobj(transcript.file, buffer)
    with open(certificate_path, "wb") as buffer:
        shutil.copyfileobj(certificate.file, buffer)
    with open(sop_path, "wb") as buffer:
        shutil.copyfileobj(statement_of_purpose.file, buffer)
    with open(payment_receipt_path, "wb") as buffer:
        shutil.copyfileobj(payment_receipt.file, buffer)
    
    other_qualifications_path = None
    if other_qualifications:
        other_qualifications_path = os.path.join(app_dir, f"other_{other_qualifications.filename}")
        with open(other_qualifications_path, "wb") as buffer:
            shutil.copyfileobj(other_qualifications.file, buffer)
    
    # Check if application with UUID exists
    existing_app = db.query(models.Application).filter(models.Application.uuid == application_uuid).first()
    
    if existing_app:
        # Update existing application
        for field, value in locals().items():
            if field not in ['db', 'current_user', 'application_uuid', 'existing_app', 'app_dir'] and not field.endswith('_file'):
                setattr(existing_app, field, value)
        
        # Update file paths
        existing_app.passport_photo_path = passport_photo_path
        existing_app.transcript_path = transcript_path
        existing_app.certificate_path = certificate_path
        existing_app.statement_of_purpose_path = sop_path
        existing_app.payment_receipt_path = payment_receipt_path
        existing_app.other_qualifications_path = other_qualifications_path
        
        db.commit()
        db.refresh(existing_app)
        return existing_app
    
    # Create new application
    db_application = models.Application(
        uuid=application_uuid,
        user_id=current_user.id,
        # Personal Details
        nationality=nationality,
        state_of_origin=state_of_origin,
        gender=gender,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
        street_address=street_address,
        city=city,
        country=country,
        has_disability=has_disability,
        disability_description=disability_description,
        
        # Academic Details
        academic_session=academic_session,
        program_type=program_type,
        selected_program=selected_program,
        
        # Academic Qualifications
        qualification_type=qualification_type,
        grade=grade,
        cgpa=cgpa,
        subject=subject,
        awarding_institution=awarding_institution,
        start_date=start_date,
        end_date=end_date,
        
        # References
        first_referee_name=first_referee_name,
        first_referee_email=first_referee_email,
        second_referee_name=second_referee_name,
        second_referee_email=second_referee_email,
        
        # File Paths
        passport_photo_path=passport_photo_path,
        transcript_path=transcript_path,
        certificate_path=certificate_path,
        statement_of_purpose_path=sop_path,
        payment_receipt_path=payment_receipt_path,
        other_qualifications_path=other_qualifications_path
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


