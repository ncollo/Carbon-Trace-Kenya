import boto3
from botocore.exceptions import BotoCoreError, ClientError
from pathlib import Path
from typing import Optional
from config import settings


def upload_file_to_s3(local_path: str, key: str) -> Optional[str]:
    """Upload a local file to S3 and return the S3 key or None on failure."""
    if not settings.use_s3:
        return None

    s3 = boto3.client(
        "s3",
        region_name=settings.s3_region or None,
        aws_access_key_id=settings.s3_access_key or None,
        aws_secret_access_key=settings.s3_secret_key or None,
    )

    try:
        s3.upload_file(local_path, settings.s3_bucket, key)
        return key
    except (BotoCoreError, ClientError):
        return None


def download_file_from_s3(key: str, dest_path: str) -> bool:
    if not settings.use_s3:
        return False
    s3 = boto3.client(
        "s3",
        region_name=settings.s3_region or None,
        aws_access_key_id=settings.s3_access_key or None,
        aws_secret_access_key=settings.s3_secret_key or None,
    )
    try:
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        s3.download_file(settings.s3_bucket, key, dest_path)
        return True
    except (BotoCoreError, ClientError):
        return False
import os
from config import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def upload_to_s3(local_path: str, key: str) -> str:
    """Upload local file to S3 and return object key."""
    import boto3

    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=settings.s3_region or None,
        aws_access_key_id=settings.s3_access_key or None,
        aws_secret_access_key=settings.s3_secret_key or None,
        endpoint_url=settings.s3_endpoint or None,
    )
    bucket = settings.s3_bucket
    client.upload_file(local_path, bucket, key)
    return key


def download_from_s3(key: str, dest_path: str) -> str:
    import boto3

    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=settings.s3_region or None,
        aws_access_key_id=settings.s3_access_key or None,
        aws_secret_access_key=settings.s3_secret_key or None,
        endpoint_url=settings.s3_endpoint or None,
    )
    bucket = settings.s3_bucket
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    client.download_file(bucket, key, dest_path)
    return dest_path
