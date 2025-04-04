from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    program: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    uuid: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ApplicationBase(BaseModel):
    # Personal Details
    nationality: str
    state_of_origin: Optional[str] = None
    gender: str
    date_of_birth: datetime
    phone_number: str
    street_address: str
    city: str
    country: str
    has_disability: bool = False
    disability_description: Optional[str] = None
    
    # Academic Details
    academic_session: str
    program_type: str
    selected_program: str
    
    # Academic Qualifications
    qualification_type: str
    grade: str
    cgpa: str
    subject: str
    awarding_institution: str
    start_date: datetime
    end_date: datetime
    
    # References
    first_referee_name: str
    first_referee_email: str
    second_referee_name: str
    second_referee_email: str

class ApplicationCreate(ApplicationBase):
    pass

class Application(ApplicationBase):
    id: int
    uuid: str
    user_id: int
    passport_photo_path: Optional[str] = None
    transcript_path: Optional[str] = None
    certificate_path: Optional[str] = None
    statement_of_purpose_path: Optional[str] = None
    payment_receipt_path: Optional[str] = None
    other_qualifications_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 
