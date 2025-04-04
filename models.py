from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base, engine

# Drop all tables
Base.metadata.drop_all(bind=engine)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    program = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    applications = relationship("Application", back_populates="user")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Personal Details
    nationality = Column(String)
    state_of_origin = Column(String, nullable=True)
    gender = Column(String)
    date_of_birth = Column(DateTime)
    phone_number = Column(String)
    street_address = Column(String)
    city = Column(String)
    country = Column(String)
    has_disability = Column(Boolean, default=False)
    disability_description = Column(String, nullable=True)
    
    # Academic Details
    academic_session = Column(String)
    program_type = Column(String)
    selected_program = Column(String)
    
    # Academic Qualifications
    qualification_type = Column(String)
    grade = Column(String)
    cgpa = Column(String)
    subject = Column(String)
    awarding_institution = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # References
    first_referee_name = Column(String)
    first_referee_email = Column(String)
    second_referee_name = Column(String)
    second_referee_email = Column(String)
    
    # File Paths
    passport_photo_path = Column(String)
    transcript_path = Column(String)
    certificate_path = Column(String)
    statement_of_purpose_path = Column(String)
    payment_receipt_path = Column(String)
    other_qualifications_path = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="applications")

# Create all tables
Base.metadata.create_all(bind=engine) 
