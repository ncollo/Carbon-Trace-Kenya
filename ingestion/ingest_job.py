from ingestion.storage import download_file_from_s3
from pathlib import Path
import time
from rq import get_current_job
from db.session import SessionLocal
from db.models import JobRecord
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


def process_upload(source: str, from_s3: bool = False):
    """Process an uploaded file.

    `source` is either a local path or an S3 key (when `from_s3` is True).
    The job will update the `job_records` table with status/result.
    """
    job = get_current_job()
    rq_id = job.id if job else None
    start = time.time()
    try:
        if rq_id:
            _update_job_record(rq_id, status="started")

        if from_s3:
            # download to a temp location
            dest = Path("data/ingest") / source
            dest.parent.mkdir(parents=True, exist_ok=True)
            ok = download_file_from_s3(source, str(dest))
            if not ok:
                raise RuntimeError("Failed to download from S3")
            path = dest
        else:
            path = Path(source)

        # Placeholder: simulate work
        time.sleep(1)

        # TODO: call ingestion pipeline components (pdf_parser, layoutlm_extractor, normaliser)
        result = {"status": "processed", "path": str(path)}


        if rq_id:
            _update_job_record(rq_id, status="finished", result=result)
            try:
                from background.metrics import JOB_DURATION_SECONDS

                JOB_DURATION_SECONDS.observe(time.time() - start)
            except Exception:
                pass

        return result
    except Exception as exc:
        tb = traceback.format_exc()
        if rq_id:
            _update_job_record(rq_id, status="failed", result={"error": str(exc), "trace": tb})
            try:
                from background.metrics import JOB_DURATION_SECONDS

                JOB_DURATION_SECONDS.observe(time.time() - start)
            except Exception:
                pass
        raise
