from enum import Enum
from typing import Any, Optional

class ErrorCode(str, Enum):
    """Standard error codes for API responses"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    BAD_REQUEST = "BAD_REQUEST"


def sanitize_error_message(error_msg: str, fallback: str = "An error occurred while processing your request") -> str:
    """
    Sanitize error messages to prevent information leakage.
    Removes sensitive details like file paths, database info, etc.
    
    Args:
        error_msg: The original error message to sanitize
        fallback: Message to use if the error contains sensitive info
    
    Returns:
        Safe error message
    """
    # Return generic message for suspicious patterns
    if any(pattern in error_msg.lower() for pattern in [
        'database', 'sql', 'query', 'constraint', 'foreign key',
        'traceback', 'exception', '/path', 'password', 'token'
    ]):
        return fallback
    
    return error_msg[:100] if len(error_msg) > 100 else error_msg


def success_response(data: Any = None, message: str = "Success") -> dict:
    """
    Standard success response format.
    
    Args:
        data: Response payload
        message: Human-readable success message
    
    Returns:
        Standardized success response dict
    """
    return {
        "status": "success",
        "message": message,
        "data": data
    }


def error_response(
    message: str = "An error occurred",
    code: str = ErrorCode.INTERNAL_ERROR,
    status_code: int = 400,
    details: Optional[Any] = None
) -> dict:
    """
    Standard error response format.
    
    Args:
        message: User-friendly error message
        code: Machine-readable error code from ErrorCode enum
        status_code: HTTP status code
        details: Additional error details (not exposed to client in prod)
    
    Returns:
        Standardized error response dict
    """
    response = {
        "status": "error",
        "message": message,
        "code": code,
    }
    if details:
        response["details"] = details
    return response