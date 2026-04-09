from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    users = relationship("User", back_populates="company")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(String, default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    company = relationship("Company", back_populates="users")


class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    filename = Column(String)
    uploaded_at = Column(DateTime)


class Emission(Base):
    __tablename__ = "emissions"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    scope = Column(String)
    value = Column(Float)


class AnomalyFlag(Base):
    __tablename__ = "anomaly_flags"
    id = Column(Integer, primary_key=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"))
    resolved = Column(Boolean, default=False)


class JobRecord(Base):
    __tablename__ = "job_records"
    id = Column(Integer, primary_key=True)
    rq_job_id = Column(String, nullable=False, unique=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    task_name = Column(String, nullable=True)
    enqueued_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=True)
    result = Column(JSON, nullable=True)

