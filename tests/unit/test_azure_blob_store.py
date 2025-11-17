"""Unit tests for Azure Blob Storage adapter."""

from collections.abc import Iterator
from typing import Any
from unittest.mock import ANY, MagicMock, patch

import pytest
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from cli2ansible.adapters.outbound.object_store.azure_blob_store import AzureBlobStore


class TestAzureBlobStore:
    """Test suite for AzureBlobStore."""

    @pytest.fixture()
    def mock_blob_service_client(self) -> Iterator[MagicMock]:
        """Create a mock BlobServiceClient."""
        with patch(
            "cli2ansible.adapters.outbound.object_store.azure_blob_store.BlobServiceClient"
        ) as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.from_connection_string.return_value = mock_client
            yield mock_client

    @pytest.fixture()
    def azure_store(self, mock_blob_service_client: Any) -> AzureBlobStore:
        """Create AzureBlobStore instance with mocked client."""
        # Mock create_container to not raise exception
        mock_blob_service_client.create_container.return_value = None

        store = AzureBlobStore(
            connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test123==;EndpointSuffix=core.windows.net",
            container="test-container",
            account_name="testaccount",
            account_key="testkey123==",
        )
        return store

    def test_init_creates_container(self, mock_blob_service_client: Any) -> None:
        """Test that initialization creates container if it doesn't exist."""
        # Arrange
        mock_blob_service_client.create_container.return_value = None

        # Act
        store = AzureBlobStore(
            connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test123==",
            container="test-container",
        )

        # Assert
        assert store.container == "test-container"
        mock_blob_service_client.create_container.assert_called_once_with("test-container")

    def test_init_handles_existing_container(self, mock_blob_service_client: Any) -> None:
        """Test that initialization handles existing container gracefully."""
        # Arrange
        mock_blob_service_client.create_container.side_effect = ResourceExistsError()

        # Act
        store = AzureBlobStore(
            connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test123==",
            container="existing-container",
        )

        # Assert
        assert store.container == "existing-container"

    def test_upload_success(
        self, azure_store: AzureBlobStore, mock_blob_service_client: Any
    ) -> None:
        """Test successful file upload."""
        # Arrange
        mock_blob_client = MagicMock()
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        test_data = b"test file content"
        test_key = "sessions/123/recording.cast"

        # Act
        result = azure_store.upload(test_key, test_data, "application/json")

        # Assert
        assert result == f"test-container/{test_key}"
        mock_blob_service_client.get_blob_client.assert_called_once_with(
            container="test-container", blob=test_key
        )
        # Verify upload_blob was called with correct data and overwrite flag
        # ContentSettings object is created internally, so we use ANY for it
        mock_blob_client.upload_blob.assert_called_once_with(
            test_data, overwrite=True, content_settings=ANY
        )

    def test_download_success(
        self, azure_store: AzureBlobStore, mock_blob_service_client: Any
    ) -> None:
        """Test successful file download."""
        # Arrange
        mock_blob_client = MagicMock()
        mock_download_stream = MagicMock()
        test_data = b"downloaded content"
        mock_download_stream.readall.return_value = test_data
        mock_blob_client.download_blob.return_value = mock_download_stream
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        test_key = "sessions/123/recording.cast"

        # Act
        result = azure_store.download(test_key)

        # Assert
        assert result == test_data
        mock_blob_service_client.get_blob_client.assert_called_once_with(
            container="test-container", blob=test_key
        )
        mock_blob_client.download_blob.assert_called_once()

    def test_download_not_found(
        self, azure_store: AzureBlobStore, mock_blob_service_client: Any
    ) -> None:
        """Test download raises FileNotFoundError when blob doesn't exist."""
        # Arrange
        mock_blob_client = MagicMock()
        mock_blob_client.download_blob.side_effect = ResourceNotFoundError()
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        test_key = "nonexistent/file.cast"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Blob not found"):
            azure_store.download(test_key)

    def test_delete_success(
        self, azure_store: AzureBlobStore, mock_blob_service_client: Any
    ) -> None:
        """Test successful file deletion."""
        # Arrange
        mock_blob_client = MagicMock()
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        test_key = "sessions/123/recording.cast"

        # Act
        azure_store.delete(test_key)

        # Assert
        mock_blob_service_client.get_blob_client.assert_called_once_with(
            container="test-container", blob=test_key
        )
        mock_blob_client.delete_blob.assert_called_once()

    def test_delete_not_found_ignored(
        self, azure_store: AzureBlobStore, mock_blob_service_client: Any
    ) -> None:
        """Test delete handles non-existent blob gracefully."""
        # Arrange
        mock_blob_client = MagicMock()
        mock_blob_client.delete_blob.side_effect = ResourceNotFoundError()
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        test_key = "nonexistent/file.cast"

        # Act - should not raise exception
        azure_store.delete(test_key)

        # Assert
        mock_blob_client.delete_blob.assert_called_once()

    @patch("cli2ansible.adapters.outbound.object_store.azure_blob_store.generate_blob_sas")
    def test_generate_url_with_credentials(
        self, mock_generate_sas: Any, azure_store: AzureBlobStore, mock_blob_service_client: Any
    ) -> None:
        """Test SAS URL generation with account credentials."""
        # Arrange
        mock_blob_client = MagicMock()
        mock_blob_client.url = "https://testaccount.blob.core.windows.net/test-container/test.cast"
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        mock_generate_sas.return_value = (
            "sv=2021-06-08&se=2024-01-01T12%3A00%3A00Z&sr=b&sp=r&sig=abc123"
        )
        test_key = "sessions/123/recording.cast"

        # Act
        result = azure_store.generate_url(test_key, expires_in=7200)

        # Assert
        assert "?" in result
        assert "sv=" in result
        mock_generate_sas.assert_called_once()

    def test_generate_url_without_credentials(self, mock_blob_service_client: Any) -> None:
        """Test URL generation without SAS credentials falls back to unsigned URL."""
        # Arrange
        mock_blob_service_client.create_container.return_value = None
        store = AzureBlobStore(
            connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test123==",
            container="test-container",
            # No account_name or account_key provided
        )
        mock_blob_client = MagicMock()
        mock_blob_client.url = "https://testaccount.blob.core.windows.net/test-container/test.cast"
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client
        test_key = "sessions/123/recording.cast"

        # Act
        result = store.generate_url(test_key)

        # Assert
        assert result == mock_blob_client.url
        assert "?" not in result  # No SAS token
