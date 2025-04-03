from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base, engine

# Drop all tables
Base.metadata.drop_all(bind=engine)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
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
    nationality = Column(String)
    address = Column(Text)
    transcript_path = Column(String)
    certificate_path = Column(String)
    statement_of_purpose_path = Column(String)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="applications")

# Create all tables
Base.metadata.create_all(bind=engine) 