from db.session import SessionLocal
from db.models import JobRecord


def job_success(job, connection, result, *args, **kwargs):
    db = SessionLocal()
    try:
        jr = db.query(JobRecord).filter(JobRecord.rq_job_id == job.id).one_or_none()
        if jr:
            jr.status = "finished"
            jr.result = result
            db.add(jr)
            db.commit()
    finally:
        db.close()


def job_failure(job, connection, type, value, tb):
    db = SessionLocal()
    try:
        jr = db.query(JobRecord).filter(JobRecord.rq_job_id == job.id).one_or_none()
        if jr:
            jr.status = "failed"
            jr.result = {"error": str(value)}
            db.add(jr)
            db.commit()
    finally:
        db.close()
