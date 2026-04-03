from pydantic import BaseModel
from typing import Optional, List


class UploadResponse(BaseModel):
    status: str
    filename: Optional[str]


class CalculateRequest(BaseModel):
    start_date: Optional[str]
    end_date: Optional[str]


class CalculateResponse(BaseModel):
    status: str
    job_id: Optional[int]


class JobStatusResponse(BaseModel):
    job_id: int
    status: str


class Anomaly(BaseModel):
    id: int
    score: float
    resolved: bool


class ReportResponse(BaseModel):
    id: int
    format: str
    url: str
