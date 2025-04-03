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
    id: int
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
    nationality: str
    address: str

class ApplicationCreate(ApplicationBase):
    pass

class Application(ApplicationBase):
    id: int
    uuid: str
    user_id: int
    transcript_path: Optional[str] = None
    certificate_path: Optional[str] = None
    statement_of_purpose_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 