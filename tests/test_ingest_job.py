import pytest

import ingestion.ingest_job as ingest_job


def test_process_upload_local(monkeypatch, tmp_path):
    monkeypatch.setattr(ingest_job, "get_current_job", lambda: None)
    monkeypatch.setattr(ingest_job.time, "sleep", lambda _: None)

    local_path = tmp_path / "file.txt"
    local_path.write_text("data")

    result = ingest_job.process_upload(str(local_path), from_s3=False)

    assert result == {"status": "processed", "path": str(local_path)}


def test_process_upload_from_s3_success(monkeypatch):
    monkeypatch.setattr(ingest_job, "get_current_job", lambda: None)
    monkeypatch.setattr(ingest_job.time, "sleep", lambda _: None)
    monkeypatch.setattr(ingest_job, "download_file_from_s3", lambda *args, **kwargs: True)

    result = ingest_job.process_upload("uploads/report.pdf", from_s3=True)

    assert result["status"] == "processed"
    assert result["path"].endswith("uploads/report.pdf")


def test_process_upload_from_s3_failure(monkeypatch):
    monkeypatch.setattr(ingest_job, "get_current_job", lambda: None)
    monkeypatch.setattr(ingest_job.time, "sleep", lambda _: None)
    monkeypatch.setattr(ingest_job, "download_file_from_s3", lambda *args, **kwargs: False)

    with pytest.raises(RuntimeError, match="Failed to download from S3"):
        ingest_job.process_upload("uploads/report.pdf", from_s3=True)
