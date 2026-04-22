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


class MatatuSacco(Base):
    __tablename__ = "matatu_saccos"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    registration_number = Column(String, unique=True)
    contact_phone = Column(String)
    contact_email = Column(String)
    office_location = Column(String)
    fleet_size = Column(Integer, default=0)
    established_year = Column(Integer)
    ntsa_compliance_rating = Column(Float)  # 1-5 rating from NTSA reviews
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    vehicles = relationship("MatatuVehicle", back_populates="sacco")


class MatatuVehicle(Base):
    __tablename__ = "matatu_vehicles"
    id = Column(Integer, primary_key=True)
    sacco_id = Column(Integer, ForeignKey("matatu_saccos.id"), nullable=False)
    registration_number = Column(String, nullable=False, unique=True)
    make = Column(String)  # e.g., Toyota, Nissan
    model = Column(String)  # e.g., Hiace, Caravan
    year_of_manufacture = Column(Integer)
    vehicle_type = Column(String)  # 14-seater, 25-seater, 33-seater, bus
    engine_capacity = Column(Integer)  # in CC
    fuel_type = Column(String)  # petrol, diesel, electric, hybrid
    seating_capacity = Column(Integer)
    route_number = Column(String)
    ntsa_inspection_expiry = Column(DateTime)
    insurance_expiry = Column(DateTime)
    road_license_expiry = Column(DateTime)
    emission_rating = Column(String)  # EURO 2, EURO 3, EURO 4, etc.
    last_service_date = Column(DateTime)
    mileage = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sacco = relationship("MatatuSacco", back_populates="vehicles")
    inspections = relationship("NtsaInspection", back_populates="vehicle")


class NtsaInspection(Base):
    __tablename__ = "ntsa_inspections"
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("matatu_vehicles.id"), nullable=False)
    inspection_date = Column(DateTime, nullable=False)
    inspector_id = Column(String)
    inspection_type = Column(String)  # annual, quarterly, special
    roadworthiness_score = Column(Float)  # 0-100
    safety_score = Column(Float)  # 0-100
    emissions_score = Column(Float)  # 0-100
    overall_rating = Column(String)  # Pass, Fail, Conditional
    violations_found = Column(JSON)  # array of violation descriptions
    recommendations = Column(JSON)  # array of recommendations
    next_inspection_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    vehicle = relationship("MatatuVehicle", back_populates="inspections")

