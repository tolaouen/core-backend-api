from datetime import datetime, UTC
from typing import List, Union

from fastapi import UploadFile


def get_current_time():
    return datetime.now(UTC)


def generate_reference(prefix: str):
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def normalize_upload_files(
    files: Union[UploadFile, List[UploadFile], None],
) -> List[UploadFile]:
    if files is None:
        return []
    if isinstance(files, UploadFile):
        return [files] if files.filename else []
    return [file for file in files if file.filename]


def parse_form_array(value: Union[str, List[str], None]) -> List[str]:
    import json
    if not value:
        return []
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed]
            except Exception:
                pass
        return [x.strip() for x in value.split(",") if x.strip()]

    if isinstance(value, list):
        result = []
        for item in value:
            if not isinstance(item, str):
                result.append(str(item))
                continue
            item = item.strip()
            if item.startswith("[") and item.endswith("]"):
                try:
                    parsed = json.loads(item)
                    if isinstance(parsed, list):
                        result.extend([str(x).strip() for x in parsed])
                        continue
                except Exception:
                    pass
            if "," in item:
                result.extend([x.strip() for x in item.split(",") if x.strip()])
            elif item:
                result.append(item)
        return result

    return []
