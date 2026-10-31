import logging
import uuid
from io import BytesIO
from typing import Iterable, Optional
from urllib.parse import quote, unquote

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_IMAGE_TYPES = ("image/jpeg", "image/png", "image/webp")
DEFAULT_MAX_SIZE = 5 * 1024 * 1024  
CHUNK_SIZE = 1024 * 1024  


class UploadService:
    """Store images in Cloudflare R2 and return persistent public URLs."""

    def __init__(self):
        self.bucket = settings.R2_BUCKET_NAME
        self.public_url = settings.R2_PUBLIC_URL.rstrip("/")
        self._client = None

    def _get_client(self):
        # Initialize only when needed so other user endpoints work without R2.
        if self._client is None:
            if not all((settings.R2_ENDPOINT_URL, settings.R2_ACCESS_KEY_ID,
                        settings.R2_SECRET_ACCESS_KEY, self.bucket, self.public_url)):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="File storage is not configured.",
                )
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.R2_ENDPOINT_URL,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                region_name="auto",
                config=Config(
                    signature_version="s3v4",
                    connect_timeout=5,
                    read_timeout=30,
                    retries={"max_attempts": 3, "mode": "standard"},
                    s3={"addressing_style": "path"},
                ),
            )
        return self._client

    def _put_image(self, key: str, content: bytes) -> None:
        try:
            self._get_client().put_object(
                Bucket=self.bucket, Key=key, Body=content, ContentType="image/webp",
            )
        except (BotoCoreError, ClientError) as exc:
            logger.warning("R2 upload failed (%s)", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to upload image to file storage.",
            ) from exc

    async def save_image(
        self,
        file: UploadFile,
        folder: str,
        prefix: str = "",
        *,
        max_size: int = DEFAULT_MAX_SIZE,
        max_dimension: int = 512,
        allowed_types: Iterable[str] = DEFAULT_IMAGE_TYPES,
    ) -> str:
        """Validate, resize and store an image as WEBP. Returns its URL."""
        if file.content_type not in set(allowed_types):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only JPEG, PNG or WEBP images are allowed.",
            )

        raw = await self._read_limited(file, max_size)
        processed = await run_in_threadpool(self._process_image, raw, max_dimension)

        filename = f"{prefix}_{uuid.uuid4().hex}.webp" if prefix else f"{uuid.uuid4().hex}.webp"
        key = f"{folder.strip('/')}/{filename}"
        await run_in_threadpool(self._put_image, key, processed)

        return f"{self.public_url}/{quote(key, safe='/')}"

    def delete(self, url: Optional[str]) -> None:
        """Best-effort cleanup of R2 objects; ignore local and foreign URLs."""
        if not url or not self.public_url or not url.startswith(f"{self.public_url}/"):
            return

        key = unquote(url[len(self.public_url) + 1:])
        if not key or any(part in ("", ".", "..") for part in key.split("/")):
            return
        try:
            self._get_client().delete_object(Bucket=self.bucket, Key=key)
        except (BotoCoreError, ClientError, HTTPException) as exc:
            logger.warning("R2 cleanup failed (%s)", type(exc).__name__)
        
    @staticmethod
    async def _read_limited(file: UploadFile, max_size: int) -> bytes:
        """Read in chunks and abort as soon as the upload exceeds max_size."""
        buffer = BytesIO()
        size = 0
        while chunk := await file.read(CHUNK_SIZE):
            size += len(chunk)
            if size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"File too large. Max size is {max_size // (1024 * 1024)} MB.",
                )
            buffer.write(chunk)
        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file.",
            )
        return buffer.getvalue()

    @staticmethod
    def _process_image(raw: bytes, max_dimension: int) -> bytes:
        """Verify it is a real image, fix rotation, resize, re-encode as WEBP.

        Re-encoding also strips EXIF/GPS metadata and any non-image payload.
        """
        try:
            with Image.open(BytesIO(raw)) as probe:
                probe.verify()
            with Image.open(BytesIO(raw)) as img:
                img = ImageOps.exif_transpose(img)
                img = img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB")
                img.thumbnail((max_dimension, max_dimension))
                out = BytesIO()
                img.save(out, format="WEBP", quality=85)
                return out.getvalue()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted image.",
            ) from exc
