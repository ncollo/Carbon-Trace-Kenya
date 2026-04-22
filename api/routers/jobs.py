from fastapi import APIRouter, HTTPException, Depends
from background.queue import get_redis_conn, _rq_available
from api.dependencies import get_db
from sqlalchemy.orm import Session
from db.models import JobRecord

# Conditional RQ import for Windows compatibility
if _rq_available:
    import rq
else:
    rq = None

router = APIRouter()


@router.get("/jobs/{job_id}/status")
async def job_status(job_id: str):
    if not _rq_available:
        raise HTTPException(
            status_code=503,
            detail="Job queue not available on Windows. Use Unix/Linux for background jobs."
        )
    conn = get_redis_conn()
    try:
        job = rq.job.Job.fetch(job_id, connection=conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")

    status = job.get_status()
    result = None
    if status == "finished":
        result = job.result
    elif status == "failed":
        result = {"exc_info": str(job.exc_info)}

    return {"job_id": job_id, "status": status, "result": result}


@router.get("/companies/{company_id}/jobs")
async def list_company_jobs(company_id: int, db: Session = Depends(get_db)):
    records = db.query(JobRecord).filter(JobRecord.company_id == company_id).order_by(JobRecord.enqueued_at.desc()).all()
    conn = get_redis_conn()
    out = []
    for r in records:
        status = r.status or "unknown"
        result = r.result
        try:
            job = rq.job.Job.fetch(r.rq_job_id, connection=conn)
            status = job.get_status()
            if status == "finished":
                result = job.result
            elif status == "failed":
                result = {"exc_info": str(job.exc_info)}
        except Exception:
            # leave DB-stored status/result if RQ fetch fails
            pass

        out.append({
            "id": r.id,
            "rq_job_id": r.rq_job_id,
            "task_name": r.task_name,
            "enqueued_at": r.enqueued_at.isoformat() if r.enqueued_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "status": status,
            "result": result,
        })

    return {"company_id": company_id, "jobs": out}
