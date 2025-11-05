"""S3/MinIO object store adapter."""
import boto3
from botocore.client import Config

from cli2ansible.domain.ports import ObjectStorePort


class S3ObjectStore(ObjectStorePort):
    """S3-compatible object store implementation."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
    ) -> None:
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:
            self.client.create_bucket(Bucket=self.bucket)

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload artifact and return URL."""
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
        )
        return f"{self.bucket}/{key}"

    def download(self, key: str) -> bytes:
        """Download artifact."""
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        body_data: bytes = response["Body"].read()
        return body_data

    def delete(self, key: str) -> None:
        """Delete artifact."""
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def generate_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL."""
        url: str = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url
