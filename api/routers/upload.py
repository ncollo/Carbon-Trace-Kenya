from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from api.schemas.common import UploadResponse
from pathlib import Path
from config import settings
from ingestion import storage as ingest_storage
from background.queue import enqueue
from api.dependencies import get_db
from sqlalchemy.orm import Session
from db.models import JobRecord

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None, db: Session = Depends(get_db), company_id: int = None):
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

    # If configured, upload to S3 and enqueue ingestion referencing the S3 key
    if settings.use_s3 and settings.s3_bucket:
        s3_key = f"uploads/{filename}"
        uploaded = ingest_storage.upload_file_to_s3(str(dest), s3_key)
        if uploaded is None:
            raise HTTPException(status_code=500, detail="Failed to upload to S3")
        # enqueue remote S3 key with success/failure handlers
        job_id = enqueue(
            "ingestion.ingest_job.process_upload",
            s3_key,
            True,
            on_success="background.handlers.job_success",
            on_failure="background.handlers.job_failure",
        )
        # persist job record
        job = JobRecord(rq_job_id=job_id, company_id=company_id, task_name="ingest:upload", status="queued")
        db.add(job)
        db.commit()
        db.refresh(job)
        return {"status": "received", "filename": s3_key, "job_id": job_id}
    else:
        # Enqueue local path processing
        job_id = enqueue(
            "ingestion.ingest_job.process_upload",
            str(dest),
            False,
            on_success="background.handlers.job_success",
            on_failure="background.handlers.job_failure",
        )
        job = JobRecord(rq_job_id=job_id, company_id=company_id, task_name="ingest:upload", status="queued")
        db.add(job)
        db.commit()
        db.refresh(job)
        return {"status": "received", "filename": str(dest), "job_id": job_id}
