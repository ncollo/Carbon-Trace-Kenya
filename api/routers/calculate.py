from fastapi import APIRouter, Depends
from api.auth import get_current_user
from background.queue import enqueue
from api.dependencies import get_db
from sqlalchemy.orm import Session
from db.models import JobRecord

router = APIRouter()


@router.post("/calculate/{company_id}")
async def calculate(company_id: int, _user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Protected endpoint: enqueue calculation job for company and persist job record
    job_id = enqueue(
        "ghg_engine.calc_job.perform_calculation",
        company_id,
        on_success="background.handlers.job_success",
        on_failure="background.handlers.job_failure",
    )
    job = JobRecord(rq_job_id=job_id, company_id=company_id, task_name="calculate:full", status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"status": "queued", "company_id": company_id, "job_id": job_id}
