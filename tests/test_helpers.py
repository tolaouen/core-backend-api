from datetime import datetime
from fastapi import UploadFile

from app.utils.helpers import generate_reference, get_current_time


def test_get_current_time_returns_datetime():
    value = get_current_time()
    assert isinstance(value, datetime)


def test_generate_reference_format():
    ref = generate_reference("APT")
    assert ref.startswith("APT-")
    assert len(ref.split("-")[1]) == 8


def test_normalize_upload_files_filters_empty_uploads():
    from unittest.mock import Mock

    from app.utils.helpers import normalize_upload_files

    valid = Mock(spec=UploadFile)
    valid.filename = "photo.jpg"
    empty = Mock(spec=UploadFile)
    empty.filename = ""

    assert normalize_upload_files([valid, empty]) == [valid]
    assert normalize_upload_files(valid) == [valid]
    assert normalize_upload_files(None) == []
