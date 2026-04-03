from fastapi import APIRouter, HTTPException
import rq
from background.queue import get_redis_conn

router = APIRouter()


@router.get("/jobs/{job_id}/status")
async def job_status(job_id: str):
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
