import math

from app.schemas.Responses.pagination import PaginatedResponse, PaginationMeta


def paginate(query, page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size

    total = query.count()
    items = query.offset(skip).limit(page_size).all()

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedResponse(meta=meta, items=items)
