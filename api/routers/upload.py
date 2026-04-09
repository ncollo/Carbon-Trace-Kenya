from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from api.schemas.common import UploadResponse
from pathlib import Path
from config import settings
from background.queue import enqueue
from api.dependencies import get_db
from sqlalchemy.orm import Session
from db.models import JobRecord

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    company_id: int = None,
):
    """Upload a file and enqueue ingestion job"""
    filename = Path(file.filename).name
    dest = UPLOAD_DIR / filename
    
    try:
        with dest.open("wb") as out_file:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                out_file.write(chunk)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Determine object key (S3 or local path)
    object_key = None
    if settings.use_s3:
        key = f"uploads/{filename}"
        try:
            from ingestion.storage import upload_to_s3

            upload_to_s3(str(dest), key)
            object_key = key
        except Exception:
            # don't fail the upload if S3 is misconfigured; keep local file
            object_key = str(dest)
    else:
        object_key = str(dest)

    # Enqueue ingestion job (may be unavailable on Windows with RQ disabled)
    job_id = None
    try:
        job_id = enqueue(
            "ingestion.ingest_job.process_upload",
            object_key,
            "s3" if settings.use_s3 and object_key.startswith("uploads/") else "local",
            job_timeout=3600,
        )
        
        # Persist job record
        if company_id and job_id:
            job = JobRecord(
                rq_job_id=job_id,
                company_id=company_id,
                task_name="ingest:upload",
                status="queued",
            )
            db.add(job)
            db.commit()
            db.refresh(job)
    except Exception:
        # Queue may be unavailable in local dev; skip enqueue
        pass

    return {
        "status": "received",
        "filename": str(dest),
        "job_id": job_id,
    }
