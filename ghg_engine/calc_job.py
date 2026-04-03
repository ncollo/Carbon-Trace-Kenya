from rq import get_current_job
from db.session import SessionLocal
from db.models import JobRecord
import time
import traceback


def _update_job_record(rq_job_id: str, **fields):
    db = SessionLocal()
    try:
        jr = db.query(JobRecord).filter(JobRecord.rq_job_id == rq_job_id).one_or_none()
        if jr:
            for k, v in fields.items():
                setattr(jr, k, v)
            db.add(jr)
            db.commit()
    finally:
        db.close()


def perform_calculation(company_id: int):
    job = get_current_job()
    rq_id = job.id if job else None
    try:
        if rq_id:
            _update_job_record(rq_id, status="started")

        # Placeholder: run core GHG calculations here
        time.sleep(2)
        result = {"company_id": company_id, "emissions": 123.45}

        if rq_id:
            _update_job_record(rq_id, status="finished", result=result)

        return result
    except Exception as exc:
        tb = traceback.format_exc()
        if rq_id:
            _update_job_record(rq_id, status="failed", result={"error": str(exc), "trace": tb})
        raise
