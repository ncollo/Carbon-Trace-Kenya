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
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None, db: Session = Depends(get_db)):
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
        # enqueue remote S3 key
        job_id = enqueue("ingestion.ingest_job.process_upload", s3_key, True)
        # persist job record
        job = JobRecord(rq_job_id=job_id, company_id=None, task_name="ingest:upload", status="queued")
        db.add(job)
        db.commit()
        db.refresh(job)
        return {"status": "received", "filename": s3_key, "job_id": job_id}
    else:
        # Enqueue local path processing
        job_id = enqueue("ingestion.ingest_job.process_upload", str(dest), False)
        job = JobRecord(rq_job_id=job_id, company_id=None, task_name="ingest:upload", status="queued")
        db.add(job)
        db.commit()
        db.refresh(job)
        return {"status": "received", "filename": str(dest), "job_id": job_id}
from config import settings
from ingestion import storage as ingest_storage
from background.queue import enqueue



from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from api.schemas.common import UploadResponse
import os
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
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

    from config import settings
    # If configured, upload to S3 and enqueue ingestion from S3
    object_key = None
    if settings.use_s3:
        key = f"uploads/{filename}"
        try:
            from ingestion.storage import upload_to_s3

            upload_to_s3(str(dest), key)
            object_key = key
                        # If configured, upload to S3 and enqueue ingestion referencing the S3 key
                        if settings.use_s3 and settings.s3_bucket:
                            s3_key = f"uploads/{filename}"
                            uploaded = ingest_storage.upload_file_to_s3(str(dest), s3_key)
                            if uploaded is None:
                                raise HTTPException(status_code=500, detail="Failed to upload to S3")
                            # enqueue remote S3 key
                            enqueue("ingestion.ingest_job.process_upload", s3_key, True)
                            return {"status": "received", "filename": s3_key}
                        else:
                            # Enqueue local path processing
                            enqueue("ingestion.ingest_job.process_upload", str(dest), False)
                            return {"status": "received", "filename": str(dest)}
            # don't fail the upload if S3 is misconfigured; keep local file
            object_key = str(dest)
    else:
        object_key = str(dest)

    # Enqueue ingestion job via RQ
    try:
        from ingestion.ingest_job import process_upload
        from background.queue import enqueue_ingestion

        enqueue_ingestion(process_upload, object_key, "s3" if settings.use_s3 else "local")
    except Exception:
        # queue may be unavailable in local dev; skip enqueue
        pass

    return {"status": "received", "filename": str(dest)}
