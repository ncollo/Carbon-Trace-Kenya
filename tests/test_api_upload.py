from config import settings


def test_upload_local_file(app_client, monkeypatch):
    monkeypatch.setattr(settings, "use_s3", False)
    monkeypatch.setattr("api.routers.upload.enqueue", lambda *args, **kwargs: "job-123")

    response = app_client.post(
        "/api/upload?company_id=1",
        files={"file": ("sample.txt", b"data", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "received"
    assert payload["filename"].endswith("sample.txt")


def test_upload_s3_success(app_client, monkeypatch):
    monkeypatch.setattr(settings, "use_s3", True)
    monkeypatch.setattr(settings, "s3_bucket", "test-bucket")
    monkeypatch.setattr("api.routers.upload.enqueue", lambda *args, **kwargs: "job-456")
    monkeypatch.setattr("api.routers.upload.ingest_storage.upload_file_to_s3", lambda *args, **kwargs: "uploads/sample.txt")

    response = app_client.post(
        "/api/upload?company_id=1",
        files={"file": ("sample.txt", b"data", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "received"
    assert payload["filename"] == "uploads/sample.txt"


def test_upload_s3_failure(app_client, monkeypatch):
    monkeypatch.setattr(settings, "use_s3", True)
    monkeypatch.setattr(settings, "s3_bucket", "test-bucket")
    monkeypatch.setattr("api.routers.upload.ingest_storage.upload_file_to_s3", lambda *args, **kwargs: None)

    response = app_client.post(
        "/api/upload?company_id=1",
        files={"file": ("sample.txt", b"data", "text/plain")},
    )

    assert response.status_code == 500
