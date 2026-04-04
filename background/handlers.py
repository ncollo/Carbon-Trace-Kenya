from db.session import SessionLocal
from db.models import JobRecord
from background.metrics import JOBS_SUCCEEDED, JOBS_FAILED, JOB_DURATION_SECONDS
import time


def job_success(job, connection, result, *args, **kwargs):
    db = SessionLocal()
    try:
        jr = db.query(JobRecord).filter(JobRecord.rq_job_id == job.id).one_or_none()
        if jr:
            jr.status = "finished"
            jr.result = result
            db.add(jr)
            db.commit()
            try:
                JOBS_SUCCEEDED.inc()
                # record duration if enqueued_at exists
                if job.enqueued_at and job.ended_at:
                    JOB_DURATION_SECONDS.observe((job.ended_at - job.enqueued_at).total_seconds())
            except Exception:
                pass
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
            try:
                JOBS_FAILED.inc()
            except Exception:
                pass
    finally:
        db.close()
