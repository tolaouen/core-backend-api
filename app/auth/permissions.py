from typing import List

def normalize_permission_list(values: List[str]) -> List[str]:
    if not isinstance(values, list):
        raise ValueError("permissions must be a list")

    unique = []
    seen = set()

    for perm in values:
        if not isinstance(perm, str) or not perm.strip():
            raise ValueError("Each permission must be a non-empty string")
        if perm not in seen:
            seen.add(perm)
            unique.append(perm)

    return unique


