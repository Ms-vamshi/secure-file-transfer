import mimetypes
import os
from typing import Optional, Dict
from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


AWS_REGION = (os.getenv("AWS_REGION", "ap-south-1") or "").strip()  # ✅ default to ap-south-1
AWS_ACCESS_KEY_ID = (os.getenv("AWS_ACCESS_KEY_ID") or "").strip()
AWS_SECRET_ACCESS_KEY = (os.getenv("AWS_SECRET_ACCESS_KEY") or "").strip()
AWS_SESSION_TOKEN = (os.getenv("AWS_SESSION_TOKEN") or "").strip()


def _build_session(region_name: str) -> boto3.session.Session:
    """Create a boto3 Session explicitly from environment credentials and region.

    This avoids surprises from implicit profile resolution and ensures
    presigning and uploads use the same credentials and region.
    """
    return boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=region_name,
    )


def _get_s3_client(region_name: str = None):
    """Return an S3 client using SigV4 signing and the specified region."""
    region = region_name or AWS_REGION
    sess = _build_session(region)
    return sess.client("s3", config=Config(signature_version="s3v4"))


def _get_bucket_region(bucket: str) -> str:
    """Resolve the bucket's region using GetBucketLocation; fall back to HeadBucket header.

    If permissions are missing, attempt HeadBucket and read 'x-amz-bucket-region'
    from the error/response headers. Finally, fall back to AWS_REGION.
    """
    try:
        s3 = _get_s3_client(AWS_REGION)
        resp = s3.get_bucket_location(Bucket=bucket)
        region = resp.get("LocationConstraint") or "us-east-1"
        return region
    except ClientError as e:
        # Try HeadBucket to capture region header even on 301/403
        try:
            s3 = _get_s3_client(AWS_REGION)
            s3.head_bucket(Bucket=bucket)
        except ClientError as he:
            headers = he.response.get("ResponseMetadata", {}).get("HTTPHeaders", {})
            region = headers.get("x-amz-bucket-region")
            if region:
                return region
        return AWS_REGION


def _guess_content_type(file_path: str) -> str:
    """Guess MIME type of a file, default to binary stream if unknown."""
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or "application/octet-stream"


def upload_to_s3(
    file_path: str,
    bucket: str,
    object_key: Optional[str] = None,
    key_prefix: str = "",
    extra_args: Optional[Dict[str, str]] = None,
) -> str:
    """Upload a file to S3 with private ACL.

    Args:
        file_path: Local path to file to upload.
        bucket: Target S3 bucket.
        object_key: Optional explicit object key. If None, one is generated.
        key_prefix: Optional prefix to prepend to the object key.
        extra_args: Optional dict of extra S3 args (e.g., ACL, metadata).

    Returns:
        str: The S3 object key used.
    """
    # Use the bucket's actual region to avoid SignatureDoesNotMatch
    bucket_region = _get_bucket_region(bucket)
    s3 = _get_s3_client(bucket_region)

    if not object_key:
        basename = os.path.basename(file_path)
        uuid_part = uuid4().hex
        prefix = key_prefix.strip("/")
        object_key = f"{uuid_part}_{basename}" if not prefix else f"{prefix}/{uuid_part}_{basename}"

    content_type = _guess_content_type(file_path)
    extra = {"ACL": "private", "ContentType": content_type}
    if extra_args:
        extra.update(extra_args)

    s3.upload_file(
        Filename=file_path,
        Bucket=bucket,
        Key=object_key,
        ExtraArgs=extra,
    )
    return object_key


def generate_presigned_url(
    bucket: str,
    object_key: str,
    expiry: int = 600,
    response_headers: Optional[Dict[str, str]] = None,
) -> str:
    """Generate a presigned GET URL for an S3 object.

    Args:
        bucket: Bucket name
        object_key: Object key
        expiry: Expiration seconds
        response_headers: Optional mapping of S3 response overrides, e.g.,
          {"ResponseContentType": "application/octet-stream",
           "ResponseContentDisposition": "attachment; filename=\"name\""}

    Returns:
        str: The presigned URL.
    """
    # Use the bucket's actual region to avoid SignatureDoesNotMatch
    bucket_region = _get_bucket_region(bucket)
    s3 = _get_s3_client(bucket_region)
    params = {"Bucket": bucket, "Key": object_key}
    if response_headers:
        params.update(response_headers)

    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params=params,
        ExpiresIn=expiry,
    )


def delete_from_s3(bucket: str, object_key: str) -> None:
    """Delete an object from S3."""
    s3 = _get_s3_client()
    s3.delete_object(Bucket=bucket, Key=object_key)
