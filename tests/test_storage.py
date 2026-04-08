from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from config import settings
from ingestion.storage import download_file_from_s3, upload_file_to_s3


def test_upload_file_to_s3_when_disabled(monkeypatch):
    monkeypatch.setattr(settings, "use_s3", False)

    assert upload_file_to_s3("/tmp/file", "key") is None


def test_upload_file_to_s3_success(monkeypatch):
    monkeypatch.setattr(settings, "use_s3", True)
    monkeypatch.setattr(settings, "s3_bucket", "bucket")

    client = Mock()
    monkeypatch.setattr("ingestion.storage.boto3.client", lambda *args, **kwargs: client)

    assert upload_file_to_s3("/tmp/file", "uploads/file") == "uploads/file"
    client.upload_file.assert_called_once()


def test_upload_file_to_s3_client_error(monkeypatch):
    monkeypatch.setattr(settings, "use_s3", True)
    monkeypatch.setattr(settings, "s3_bucket", "bucket")

    client = Mock()
    client.upload_file.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "boom"}},
        "UploadFile",
    )
    monkeypatch.setattr("ingestion.storage.boto3.client", lambda *args, **kwargs: client)

    assert upload_file_to_s3("/tmp/file", "uploads/file") is None


def test_download_file_from_s3_success(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "use_s3", True)
    monkeypatch.setattr(settings, "s3_bucket", "bucket")

    client = Mock()
    monkeypatch.setattr("ingestion.storage.boto3.client", lambda *args, **kwargs: client)

    dest_path = tmp_path / "file"
    assert download_file_from_s3("uploads/file", str(dest_path)) is True
    client.download_file.assert_called_once()


def test_download_file_from_s3_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "use_s3", True)
    monkeypatch.setattr(settings, "s3_bucket", "bucket")

    client = Mock()
    client.download_file.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "boom"}},
        "DownloadFile",
    )
    monkeypatch.setattr("ingestion.storage.boto3.client", lambda *args, **kwargs: client)

    dest_path = tmp_path / "file"
    assert download_file_from_s3("uploads/file", str(dest_path)) is False
