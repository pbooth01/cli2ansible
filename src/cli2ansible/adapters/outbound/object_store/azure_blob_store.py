"""Azure Blob Storage adapter."""

from contextlib import suppress
from datetime import UTC, datetime, timedelta

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
)
from cli2ansible.domain.ports import ObjectStorePort


class AzureBlobStore(ObjectStorePort):
    """Azure Blob Storage implementation."""

    def __init__(
        self,
        connection_string: str,
        container: str,
        account_name: str | None = None,
        account_key: str | None = None,
    ) -> None:
        """
        Initialize Azure Blob Storage client.

        Args:
            connection_string: Azure Storage connection string
            container: Container name (equivalent to S3 bucket)
            account_name: Storage account name (for SAS URL generation)
            account_key: Storage account key (for SAS URL generation)
        """
        self.container = container
        self.account_name = account_name
        self.account_key = account_key
        self.client = BlobServiceClient.from_connection_string(connection_string)
        self._ensure_container()

    def _ensure_container(self) -> None:
        """Create container if it doesn't exist."""
        with suppress(ResourceExistsError):
            self.client.create_container(self.container)

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload artifact and return URL."""
        blob_client = self.client.get_blob_client(container=self.container, blob=key)
        content_settings = ContentSettings(content_type=content_type)
        blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
        return f"{self.container}/{key}"

    def download(self, key: str) -> bytes:
        """Download artifact."""
        blob_client = self.client.get_blob_client(container=self.container, blob=key)
        try:
            download_stream = blob_client.download_blob()
            data: bytes = download_stream.readall()
            return data
        except ResourceNotFoundError as e:
            raise FileNotFoundError(f"Blob not found: {key}") from e

    def delete(self, key: str) -> None:
        """Delete artifact."""
        blob_client = self.client.get_blob_client(container=self.container, blob=key)
        with suppress(ResourceNotFoundError):
            blob_client.delete_blob()

    def generate_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate SAS URL for blob access.

        Args:
            key: Blob key/path
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL for blob access
        """
        if not self.account_name or not self.account_key:
            # Fallback to unsigned URL if credentials not available
            blob_client = self.client.get_blob_client(container=self.container, blob=key)
            return str(blob_client.url)

        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container,
            blob_name=key,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(UTC) + timedelta(seconds=expires_in),
        )

        # Construct full URL with SAS token
        blob_client = self.client.get_blob_client(container=self.container, blob=key)
        url: str = f"{blob_client.url}?{sas_token}"
        return url
