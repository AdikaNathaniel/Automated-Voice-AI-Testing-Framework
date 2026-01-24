"""
S3 Storage Service (TASK-113)

This module provides S3 storage functionality for the Voice AI Testing Framework.
It handles uploading, downloading, and deleting audio files from S3 (or MinIO for local dev).

Features:
- Upload audio files to S3 and get shareable URLs
- Download audio files from S3 URLs
- Delete audio files from S3
- Support for different buckets
- Async methods for non-blocking I/O
- Proper error handling and logging

Compatible with:
- AWS S3 (production)
- MinIO (local development)

Example:
    >>> storage = StorageService()
    >>> audio_data = b"audio content"
    >>> url = await storage.upload_audio(audio_data, "test.mp3")
    >>> print(url)  # s3://voice-ai-testing/test.mp3
    >>>
    >>> downloaded = await storage.download_audio(url)
    >>> assert downloaded == audio_data
    >>>
    >>> deleted = await storage.delete_audio(url)
    >>> assert deleted is True
"""

import asyncio
import boto3
from botocore.exceptions import ClientError
from typing import Optional
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class StorageService:
    """
    S3 storage service for audio files.

    This service provides async methods for uploading, downloading, and deleting
    audio files from S3-compatible storage (AWS S3 or MinIO).

    Attributes:
        s3_client: Boto3 S3 client for making API calls
        default_bucket: Default bucket name for operations

    Example:
        >>> storage = StorageService()
        >>> url = await storage.upload_audio(b"data", "file.mp3")
        >>> data = await storage.download_audio(url)
        >>> success = await storage.delete_audio(url)
    """

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        default_bucket: str = "voice-ai-testing"
    ):
        """
        Initialize the storage service.

        Args:
            aws_access_key_id: AWS access key ID (uses default credentials if None)
            aws_secret_access_key: AWS secret access key (uses default credentials if None)
            endpoint_url: Custom S3 endpoint URL (for MinIO, etc.)
            region_name: AWS region name (default: us-east-1)
            default_bucket: Default bucket name for operations
        """
        # Initialize boto3 S3 client
        client_kwargs = {
            'service_name': 's3',
            'region_name': region_name
        }

        if aws_access_key_id and aws_secret_access_key:
            client_kwargs['aws_access_key_id'] = aws_access_key_id
            client_kwargs['aws_secret_access_key'] = aws_secret_access_key

        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url

        self.s3_client = boto3.client(**client_kwargs)
        self.default_bucket = default_bucket
        self.endpoint_url = endpoint_url

        logger.info(f"StorageService initialized with bucket: {default_bucket}")

    async def upload_audio(
        self,
        file_data: bytes,
        file_name: str,
        bucket: str = "voice-ai-testing"
    ) -> str:
        """
        Upload audio file to S3 and return the HTTP URL.

        This method uploads audio data to the specified S3 bucket and returns
        an HTTP URL that can be used to access the file from a browser.

        Args:
            file_data: Raw audio data in bytes
            file_name: Name for the file in S3 (e.g., "test.mp3")
            bucket: S3 bucket name (uses default if not specified)

        Returns:
            str: HTTP URL in the format "http://localhost:9000/bucket/file" (MinIO)
                 or "https://bucket.s3.amazonaws.com/file" (AWS S3)

        Raises:
            ValueError: If file_data is empty or file_name is invalid
            RuntimeError: If upload fails

        Example:
            >>> storage = StorageService()
            >>> audio = b"audio data here"
            >>> url = await storage.upload_audio(audio, "recording.mp3")
            >>> print(url)
            http://localhost:9000/voice-ai-testing/recording.mp3
        """
        if not file_data:
            raise ValueError("file_data cannot be empty")

        if not file_name or not file_name.strip():
            raise ValueError("file_name cannot be empty")

        # Use default bucket if not specified
        if not bucket:
            bucket = self.default_bucket

        logger.info(f"Uploading {len(file_data)} bytes to {bucket}/{file_name}")

        try:
            # Run boto3 call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.put_object(
                    Bucket=bucket,
                    Key=file_name,
                    Body=file_data,
                    ContentType='audio/mpeg'  # Default to MP3, can be made configurable
                )
            )

            # Construct HTTP URL for browser access
            if self.endpoint_url:
                # MinIO or custom S3 endpoint - use endpoint URL
                # Convert internal docker hostname to external hostname for browser access
                http_url = self.endpoint_url.replace('minio:9000', 'localhost:9000')
                http_url = f"{http_url}/{bucket}/{file_name}"
            else:
                # AWS S3 - use standard S3 URL format
                http_url = f"https://{bucket}.s3.amazonaws.com/{file_name}"

            logger.debug(f"Successfully uploaded to {http_url}")

            return http_url

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = f"S3 upload failed: {error_code} - {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def download_audio(self, s3_url: str) -> bytes:
        """
        Download audio file from S3 URL.

        This method parses an S3 URL, downloads the file from S3, and returns
        the raw audio data as bytes.

        Args:
            s3_url: S3 URL in the format "s3://bucket-name/file-name"

        Returns:
            bytes: Raw audio data

        Raises:
            ValueError: If s3_url is invalid or not in S3 format
            RuntimeError: If download fails

        Example:
            >>> storage = StorageService()
            >>> url = "s3://voice-ai-testing/recording.mp3"
            >>> audio_data = await storage.download_audio(url)
            >>> len(audio_data) > 0  # True
        """
        if not s3_url or not s3_url.strip():
            raise ValueError("s3_url cannot be empty")

        # Parse S3 URL
        bucket, key = self._parse_s3_url(s3_url)

        logger.info(f"Downloading from s3://{bucket}/{key}")

        try:
            # Run boto3 call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.get_object(
                    Bucket=bucket,
                    Key=key
                )
            )

            # Read the data from the response body
            audio_data = response['Body'].read()

            logger.debug(f"Successfully downloaded {len(audio_data)} bytes from {s3_url}")

            return audio_data

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = f"S3 download failed: {error_code} - {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error during download: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def delete_audio(self, s3_url: str) -> bool:
        """
        Delete audio file from S3.

        This method parses an S3 URL and deletes the corresponding file from S3.

        Args:
            s3_url: S3 URL in the format "s3://bucket-name/file-name"

        Returns:
            bool: True if deletion was successful, False otherwise

        Raises:
            ValueError: If s3_url is invalid or not in S3 format

        Example:
            >>> storage = StorageService()
            >>> url = "s3://voice-ai-testing/old-recording.mp3"
            >>> success = await storage.delete_audio(url)
            >>> print(success)  # True
        """
        if not s3_url or not s3_url.strip():
            raise ValueError("s3_url cannot be empty")

        # Parse S3 URL
        bucket, key = self._parse_s3_url(s3_url)

        logger.info(f"Deleting s3://{bucket}/{key}")

        try:
            # Run boto3 call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=bucket,
                    Key=key
                )
            )

            logger.debug(f"Successfully deleted {s3_url}")

            return True

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 deletion failed: {error_code} - {str(e)}")
            # Don't raise exception, just return False
            return False

        except Exception as e:
            logger.error(f"Unexpected error during deletion: {str(e)}")
            # Don't raise exception, just return False
            return False

    def _parse_s3_url(self, s3_url: str) -> tuple[str, str]:
        """
        Parse S3 URL into bucket and key components.

        Args:
            s3_url: S3 URL in the format "s3://bucket-name/file-name"

        Returns:
            tuple: (bucket, key) pair

        Raises:
            ValueError: If URL is not in valid S3 format

        Example:
            >>> storage = StorageService()
            >>> bucket, key = storage._parse_s3_url("s3://my-bucket/path/to/file.mp3")
            >>> print(bucket)  # my-bucket
            >>> print(key)  # path/to/file.mp3
        """
        if not s3_url.startswith("s3://"):
            raise ValueError(f"Invalid S3 URL format: {s3_url}. Must start with 's3://'")

        # Parse the URL
        parsed = urlparse(s3_url)

        bucket = parsed.netloc
        # Remove leading slash from path
        key = parsed.path.lstrip('/')

        if not bucket:
            raise ValueError(f"Invalid S3 URL: no bucket specified in {s3_url}")

        if not key:
            raise ValueError(f"Invalid S3 URL: no key specified in {s3_url}")

        return bucket, key

    async def delete_by_key(self, key: str, bucket: Optional[str] = None) -> bool:
        """
        Delete a file from S3 by its key.

        This method is useful for rollback scenarios where we have the key
        but not the full S3 URL. It provides reliable deletion with proper
        error handling and logging for debugging.

        Args:
            key: The S3 object key (e.g., "scenarios/123/steps/456/audio-en-US.mp3")
            bucket: S3 bucket name (uses default if None)

        Returns:
            bool: True if deletion was successful or file didn't exist,
                  False if deletion failed due to an error

        Example:
            >>> storage = StorageService()
            >>> # After S3 upload succeeds but DB update fails, rollback:
            >>> success = await storage.delete_by_key("scenarios/abc/steps/def/audio.mp3")
            >>> if not success:
            ...     logger.error("Rollback failed - orphaned file may exist")
        """
        if not key or not key.strip():
            logger.error("delete_by_key called with empty key")
            return False

        if bucket is None:
            bucket = self.default_bucket

        logger.info(f"Deleting by key: {bucket}/{key}")

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=bucket,
                    Key=key
                )
            )

            logger.info(f"Successfully deleted {bucket}/{key}")
            return True

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(
                f"S3 deletion by key failed: bucket={bucket}, key={key}, "
                f"error_code={error_code}, error={str(e)}"
            )
            return False

        except Exception as e:
            logger.error(
                f"Unexpected error during delete_by_key: bucket={bucket}, "
                f"key={key}, error={str(e)}"
            )
            return False

    async def list_files(self, bucket: Optional[str] = None, prefix: str = "") -> list[str]:
        """
        List files in S3 bucket with optional prefix filter.

        Args:
            bucket: S3 bucket name (uses default if None)
            prefix: Optional prefix to filter files (e.g., "audio/")

        Returns:
            list: List of S3 URLs for matching files

        Example:
            >>> storage = StorageService()
            >>> files = await storage.list_files(prefix="recordings/")
            >>> for file_url in files:
            ...     print(file_url)
        """
        if bucket is None:
            bucket = self.default_bucket

        logger.info(f"Listing files in s3://{bucket}/{prefix}")

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix
                )
            )

            # Extract file URLs
            files = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                s3_url = f"s3://{bucket}/{key}"
                files.append(s3_url)

            logger.debug(f"Found {len(files)} files in s3://{bucket}/{prefix}")

            return files

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 list failed: {error_code} - {str(e)}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error during list: {str(e)}")
            return []
