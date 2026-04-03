from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


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
