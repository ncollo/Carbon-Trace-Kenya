from ingestion.storage import download_file_from_s3
from pathlib import Path
import time


def process_upload(source: str, from_s3: bool = False):
    """Process an uploaded file.

    `source` is either a local path or an S3 key (when `from_s3` is True).
    This function is intentionally simple — replace with the real pipeline.
    """
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
    return {"status": "processed", "path": str(path)}
import os
import logging
from ingestion import storage
from pathlib import Path

logger = logging.getLogger(__name__)


def process_upload(object_key: str, source: str = "s3"):
    """Background job entrypoint for processing an upload.

    `object_key` is either a local path or an S3 object key depending on `source`.
    """
    tmp_dir = Path("/tmp/carbon_ingest")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    if source == "s3":
        dest = tmp_dir / Path(object_key).name
        dest_path = str(dest)
        storage.download_from_s3(object_key, dest_path)
    else:
        # local path
        dest_path = object_key

    # Placeholder: call parsing/normalisation pipeline on `dest_path`
    logger.info(f"Processing upload at {dest_path}")

    # TODO: implement actual ingestion steps (pdf parsing, layoutlm, normaliser)

    return {"status": "processed", "path": dest_path}
