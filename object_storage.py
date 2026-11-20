"""Read and write files in Akamai/Linode Object Storage (S3-compatible)."""
import csv
import io
import os
from typing import Any

import boto3
from botocore.config import Config


def _s3_client():
    endpoint_url = os.environ["S3_ENDPOINT_URL"]
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name=os.getenv("S3_REGION", "us-east-1"),
        config=Config(signature_version="s3v4"),
    )


def read_csv_from_object_storage(object_key: str) -> list[dict[str, Any]]:
    """Download a CSV object and return its rows as dictionaries."""
    bucket = os.environ["S3_BUCKET"]
    response = _s3_client().get_object(Bucket=bucket, Key=object_key)
    raw = response["Body"].read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(raw)))


def write_json_to_object_storage(object_key: str, payload: dict[str, Any]) -> None:
    """Write a JSON approval record to object storage."""
    import json

    bucket = os.environ["S3_BUCKET"]
    _s3_client().put_object(
        Bucket=bucket,
        Key=object_key,
        Body=json.dumps(payload, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
