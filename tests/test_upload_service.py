import asyncio
from io import BytesIO
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile
from PIL import Image
from starlette.datastructures import Headers

from app.core.config import settings
from app.services.uploads.upload_service import UploadService
from app.services.app_user.users import UserService


def test_client_uses_r2_endpoint_and_explicit_credentials(monkeypatch):
    for name, value in {
        "R2_ENDPOINT_URL": "https://account.r2.cloudflarestorage.com",
        "R2_ACCESS_KEY_ID": "test-key",
        "R2_SECRET_ACCESS_KEY": "test-secret",
        "R2_BUCKET_NAME": "test-images",
        "R2_PUBLIC_URL": "https://images.example.com",
    }.items():
        monkeypatch.setattr(settings, name, value)
    factory = Mock()
    monkeypatch.setattr("app.services.uploads.upload_service.boto3.client", factory)
    service = UploadService()
    factory.assert_not_called()
    assert service._get_client() is factory.return_value
    args = factory.call_args.kwargs
    assert args["endpoint_url"] == "https://account.r2.cloudflarestorage.com"
    assert args["region_name"] == "auto"
    assert args["aws_access_key_id"] == "test-key"
    assert args["aws_secret_access_key"] == "test-secret"


@pytest.fixture
def uploader(monkeypatch):
    monkeypatch.setattr(settings, "R2_BUCKET_NAME", "test-images")
    monkeypatch.setattr(settings, "R2_PUBLIC_URL", "https://images.example.com")
    service = UploadService()
    service._client = Mock()
    return service


def image_file(content=None, content_type="image/png"):
    if content is None:
        buffer = BytesIO()
        Image.new("RGB", (800, 400)).save(buffer, format="PNG")
        content = buffer.getvalue()
    return UploadFile(file=BytesIO(content), filename="photo.png",
                      headers=Headers({"content-type": content_type}))


def test_upload_stores_resized_webp_and_returns_public_url(uploader):
    url = asyncio.run(uploader.save_image(image_file(), "profiles", prefix="42"))
    args = uploader._client.put_object.call_args.kwargs
    assert args["Bucket"] == "test-images"
    assert args["ContentType"] == "image/webp"
    assert args["Key"].startswith("profiles/42_")
    assert url == f'https://images.example.com/{args["Key"]}'
    with Image.open(BytesIO(args["Body"])) as image:
        assert image.format == "WEBP"
        assert image.size == (512, 256)
    uploader.delete(url)
    uploader._client.delete_object.assert_called_once_with(
        Bucket="test-images", Key=args["Key"])


@pytest.mark.parametrize("content,content_type,limit,expected", [
    (b"", "image/png", 100, 400),
    (b"corrupt", "image/png", 100, 400),
    (b"12345", "image/png", 4, 413),
    (b"text", "text/plain", 100, 415),
])
def test_invalid_upload_does_not_write(uploader, content, content_type, limit, expected):
    with pytest.raises(HTTPException) as error:
        asyncio.run(uploader.save_image(image_file(content, content_type), "profiles", max_size=limit))
    assert error.value.status_code == expected
    uploader._client.put_object.assert_not_called()


@pytest.mark.parametrize("url", [None, "", "/uploads/profiles/old.webp",
    "https://other.example.com/photo.webp", "https://images.example.com.evil/photo.webp",
    "https://images.example.com/../photo.webp"])
def test_delete_ignores_unowned_urls(uploader, url):
    uploader.delete(url)
    uploader._client.delete_object.assert_not_called()


def test_storage_failure_returns_generic_error(uploader):
    uploader._client.put_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "secret details"}}, "PutObject")
    with pytest.raises(HTTPException) as error:
        asyncio.run(uploader.save_image(image_file(), "profiles"))
    assert error.value.status_code == 502
    assert "secret details" not in error.value.detail


def test_missing_configuration_is_lazy_and_returns_503(monkeypatch):
    monkeypatch.setattr(settings, "R2_ACCESS_KEY_ID", "")
    service = UploadService()
    with pytest.raises(HTTPException) as error:
        asyncio.run(service.save_image(image_file(), "profiles"))
    assert error.value.status_code == 503


@pytest.mark.parametrize("failure", [None, "commit", "refresh"])
def test_profile_cleanup_respects_commit(uploader, failure):
    db = Mock()
    if failure:
        getattr(db, failure).side_effect = RuntimeError("database error")
    user = Mock(id=42, profile="https://images.example.com/profiles/old.webp")
    service = UserService(db, uploader)
    service.get_all_user_id = Mock(return_value=user)
    if failure:
        with pytest.raises(RuntimeError):
            asyncio.run(service.upload_profile(42, image_file()))
    else:
        assert asyncio.run(service.upload_profile(42, image_file())) is user
    new_key = uploader._client.put_object.call_args.kwargs["Key"]
    deleted_key = uploader._client.delete_object.call_args.kwargs["Key"]
    assert deleted_key == (new_key if failure == "commit" else "profiles/old.webp")


def test_cleanup_failure_does_not_fail_saved_profile(uploader):
    uploader._client.delete_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied"}}, "DeleteObject")
    uploader.delete("https://images.example.com/profiles/old.webp")


def test_failed_upload_keeps_existing_profile(uploader):
    uploader._client.put_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied"}}, "PutObject")
    db = Mock()
    user = Mock(id=42, profile="https://images.example.com/profiles/old.webp")
    service = UserService(db, uploader)
    service.get_all_user_id = Mock(return_value=user)
    with pytest.raises(HTTPException):
        asyncio.run(service.upload_profile(42, image_file()))
    assert user.profile == "https://images.example.com/profiles/old.webp"
    db.commit.assert_not_called()
    uploader._client.delete_object.assert_not_called()
