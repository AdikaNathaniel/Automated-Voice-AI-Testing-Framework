"""
Voice AI Testing Framework - Exception Handling
Custom exceptions and global exception handlers for FastAPI
"""

from typing import Optional, Dict, Any
import re
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.logging_config import get_logger, get_request_id
from api.config import get_settings

# Initialize logger
logger = get_logger(__name__)


# ============================================================================
# Custom Exception Classes
# ============================================================================

class APIException(Exception):
    """
    Base exception class for all API exceptions

    Attributes:
        status_code: HTTP status code
        detail: Error detail message
        headers: Optional HTTP headers
    """

    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        headers: Optional[Dict[str, str]] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers or {}
        super().__init__(detail)


class ValidationError(APIException):
    """
    Exception raised when request validation fails

    HTTP Status Code: 400 Bad Request

    Example:
        ```python
        from api.exceptions import ValidationError

        if not email.endswith('@example.com'):
            raise ValidationError("Email must be from example.com domain")
        ```
    """

    def __init__(self, detail: str, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=headers
        )


class NotFoundError(APIException):
    """
    Exception raised when a resource is not found

    HTTP Status Code: 404 Not Found

    Example:
        ```python
        from api.exceptions import NotFoundError

        user = db.get_user(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        ```
    """

    def __init__(self, detail: str, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            headers=headers
        )


class UnauthorizedError(APIException):
    """
    Exception raised when authentication is required but not provided

    HTTP Status Code: 401 Unauthorized

    Example:
        ```python
        from api.exceptions import UnauthorizedError

        if not token:
            raise UnauthorizedError(
                "Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        ```
    """

    def __init__(self, detail: str, headers: Optional[Dict[str, str]] = None):
        # Default WWW-Authenticate header for 401 responses
        default_headers = {"WWW-Authenticate": "Bearer"}
        if headers:
            default_headers.update(headers)

        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers=default_headers
        )


class ForbiddenError(APIException):
    """
    Exception raised when user is authenticated but lacks permission

    HTTP Status Code: 403 Forbidden

    Example:
        ```python
        from api.exceptions import ForbiddenError

        if not user.is_admin:
            raise ForbiddenError("Admin privileges required")
        ```
    """

    def __init__(self, detail: str, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            headers=headers
        )


class ConflictError(APIException):
    """
    Exception raised when a resource conflict occurs

    HTTP Status Code: 409 Conflict

    Example:
        ```python
        from api.exceptions import ConflictError

        existing_user = db.get_user_by_email(email)
        if existing_user:
            raise ConflictError(f"User with email {email} already exists")
        ```
    """

    def __init__(self, detail: str, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            headers=headers
        )


class InternalServerError(APIException):
    """
    Exception raised for internal server errors

    HTTP Status Code: 500 Internal Server Error

    Example:
        ```python
        from api.exceptions import InternalServerError

        try:
            result = external_api.call()
        except Exception as e:
            raise InternalServerError(f"External API error: {str(e)}")
        ```
    """

    def __init__(self, detail: str, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=headers
        )


# ============================================================================
# Error Message Sanitization
# ============================================================================

# Patterns that indicate sensitive information
SENSITIVE_PATTERNS = [
    # Database connection strings
    r'(?:mysql|postgresql|postgres|mongodb|redis)://[^\s]+',
    # Password patterns
    r'password[=:]\s*[^\s,}]+',
    r'pwd[=:]\s*[^\s,}]+',
    # API keys and tokens
    r'(?:api[_-]?key|token|secret|bearer)[=:\s]+[^\s,}]+',
    r'sk-[a-zA-Z0-9]+',
    r'AKIA[A-Z0-9]+',
    # File paths that might be sensitive
    r'/(?:etc|var|home|root)/[^\s]+(?:\.(?:key|pem|env|conf|json|yml|yaml))?',
    # Internal IP addresses
    r'(?:192\.168|10\.0|172\.(?:1[6-9]|2[0-9]|3[0-1]))\.\d+\.\d+(?::\d+)?',
    # Stack traces
    r'Traceback \(most recent call last\):[\s\S]*?(?:Error|Exception):',
    r'File "[^"]+", line \d+',
]

# Compiled patterns for performance
COMPILED_SENSITIVE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in SENSITIVE_PATTERNS]


def sanitize_error_detail(
    detail: str,
    is_production: bool,
    status_code: int = 400
) -> str:
    """
    Sanitize error detail message based on environment.

    In production, sensitive information is removed or replaced with generic messages.
    In development, full error details are preserved for debugging.

    Args:
        detail: The original error detail message
        is_production: Whether running in production environment
        status_code: HTTP status code for the error

    Returns:
        Sanitized error message safe for client response

    Example:
        >>> sanitize_error_detail(
        ...     "Database error: password=secret123",
        ...     is_production=True,
        ...     status_code=500
        ... )
        'An internal server error occurred'
    """
    if not is_production:
        return detail

    # For 500 errors, always return generic message in production
    if status_code >= 500:
        return "An internal server error occurred"

    # Check for sensitive patterns
    for pattern in COMPILED_SENSITIVE_PATTERNS:
        if pattern.search(detail):
            # Log the original for debugging (server-side only)
            logger.debug("Sanitized sensitive content from error message")

            # Return generic message based on status code
            if status_code == 400:
                return "Invalid request"
            elif status_code == 401:
                return "Authentication failed"
            elif status_code == 403:
                return "Access denied"
            elif status_code == 404:
                return "Resource not found"
            elif status_code == 409:
                return "Resource conflict"
            else:
                return "Request failed"

    # If no sensitive patterns found, return original message
    return detail


# ============================================================================
# Exception Response Builder
# ============================================================================

def build_error_response(
    status_code: int,
    detail: str,
    error_type: str,
    headers: Optional[Dict[str, str]] = None
) -> JSONResponse:
    """
    Build a standardized error response

    Args:
        status_code: HTTP status code
        detail: Error detail message
        error_type: Type of error (e.g., "ValidationError", "NotFoundError")
        headers: Optional HTTP headers

    Returns:
        JSONResponse with standardized error format
    """
    # Build error response body
    error_body: Dict[str, Any] = {
        "detail": detail,
        "error_type": error_type,
    }

    # Add request ID if available from context
    request_id = get_request_id()
    if request_id:
        error_body["request_id"] = request_id

    # Log the error
    logger.error(
        f"API Error: {error_type} - {detail}",
        extra={
            "error_type": error_type,
            "status_code": status_code,
            "request_id": request_id,
        }
    )

    return JSONResponse(
        status_code=status_code,
        content=error_body,
        headers=headers or {}
    )


# ============================================================================
# Exception Handlers
# ============================================================================

async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle ValidationError exceptions

    Args:
        request: The incoming request
        exc: The ValidationError exception

    Returns:
        JSONResponse with 400 status code

    Example:
        This handler is automatically called when a ValidationError is raised:
        ```python
        raise ValidationError("Invalid email format")
        # Returns: {"detail": "Invalid email format", "error_type": "ValidationError", ...}
        ```
    """
    return build_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_type="ValidationError",
        headers=exc.headers
    )


async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """
    Handle NotFoundError exceptions

    Args:
        request: The incoming request
        exc: The NotFoundError exception

    Returns:
        JSONResponse with 404 status code
    """
    return build_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_type="NotFoundError",
        headers=exc.headers
    )


async def unauthorized_error_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    """
    Handle UnauthorizedError exceptions

    Args:
        request: The incoming request
        exc: The UnauthorizedError exception

    Returns:
        JSONResponse with 401 status code
    """
    return build_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_type="UnauthorizedError",
        headers=exc.headers
    )


async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    """
    Handle ForbiddenError exceptions

    Args:
        request: The incoming request
        exc: The ForbiddenError exception

    Returns:
        JSONResponse with 403 status code
    """
    return build_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_type="ForbiddenError",
        headers=exc.headers
    )


async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    """
    Handle ConflictError exceptions

    Args:
        request: The incoming request
        exc: The ConflictError exception

    Returns:
        JSONResponse with 409 status code
    """
    return build_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_type="ConflictError",
        headers=exc.headers
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException exceptions

    Args:
        request: The incoming request
        exc: The HTTPException

    Returns:
        JSONResponse with appropriate status code

    Note:
        This handler catches FastAPI's built-in HTTPException and converts
        it to our standardized error response format. In production, error
        details are sanitized to prevent information disclosure.
    """
    # Get the original detail
    original_detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    # Log the full error details server-side
    logger.error(
        f"HTTPException: {exc.status_code} - {original_detail}",
        extra={
            "status_code": exc.status_code,
            "path": str(request.url.path),
        }
    )

    # Sanitize the detail based on environment
    settings = get_settings()
    sanitized_detail = sanitize_error_detail(
        original_detail,
        is_production=settings.is_production(),
        status_code=exc.status_code
    )

    return build_error_response(
        status_code=exc.status_code,
        detail=sanitized_detail,
        error_type="HTTPException",
        headers=getattr(exc, 'headers', None)
    )


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle FastAPI request validation errors

    Args:
        request: The incoming request
        exc: The RequestValidationError

    Returns:
        JSONResponse with 422 status code

    Note:
        This handler is for Pydantic validation errors on request bodies,
        query parameters, and path parameters.
    """
    # Format validation errors
    errors = exc.errors()
    error_details = []

    for error in errors:
        error_details.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        })

    # Build detailed error message
    detail = f"Request validation failed: {len(errors)} error(s)"

    # Build error response with validation details
    error_body: Dict[str, Any] = {
        "detail": detail,
        "error_type": "RequestValidationError",
        "validation_errors": error_details,
    }

    # Add request ID if available
    request_id = get_request_id()
    if request_id:
        error_body["request_id"] = request_id

    # Log the validation error
    logger.warning(
        f"Request validation error: {detail}",
        extra={
            "error_type": "RequestValidationError",
            "validation_errors": error_details,
            "request_id": request_id,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_body
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse with 500 status code

    Note:
        This is a catch-all handler for any exceptions not caught by
        more specific handlers. It logs the full exception and returns
        a generic error message to avoid exposing internal details.
    """
    # Log the exception with full traceback
    logger.exception(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=exc
    )

    # Return generic error message (don't expose internal details)
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An internal server error occurred",
        error_type=type(exc).__name__
    )


# ============================================================================
# Exception Handler Registration
# ============================================================================

def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application

    Args:
        app: The FastAPI application instance

    Example:
        ```python
        from fastapi import FastAPI
        from api.exceptions import register_exception_handlers

        app = FastAPI()
        register_exception_handlers(app)
        ```

    Note:
        This function should be called during application initialization,
        typically in main.py after creating the FastAPI app instance.
    """
    # Register custom exception handlers
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(UnauthorizedError, unauthorized_error_handler)
    app.add_exception_handler(ForbiddenError, forbidden_error_handler)
    app.add_exception_handler(ConflictError, conflict_error_handler)

    # Register FastAPI/Starlette exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)

    # Register generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered successfully")


# ============================================================================
# Export public API
# ============================================================================

__all__ = [
    # Custom exceptions
    'APIException',
    'ValidationError',
    'NotFoundError',
    'UnauthorizedError',
    'ForbiddenError',
    'ConflictError',
    'InternalServerError',

    # Exception handlers
    'validation_error_handler',
    'not_found_error_handler',
    'unauthorized_error_handler',
    'forbidden_error_handler',
    'conflict_error_handler',
    'http_exception_handler',
    'request_validation_error_handler',
    'generic_exception_handler',

    # Registration function
    'register_exception_handlers',

    # Utility functions
    'build_error_response',
    'sanitize_error_detail',
]
