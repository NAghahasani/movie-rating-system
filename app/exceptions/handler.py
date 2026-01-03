"""
Global exception handlers for consistent API error responses.

This module provides centralized error handling to ensure all API errors
follow a standardized JSON format.
"""

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging_config import logger


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
) -> JSONResponse:
    """
    Handle FastAPI validation errors and return custom messages.

    :param request: The incoming HTTP request object
    :param exc: The validation error details
    :return: Standardized failure response with 422 status code
    """
    errors = exc.errors()
    full_error_text = str(errors).lower()

    # Map validation errors to specific user-friendly messages
    if any(field in full_error_text for field in ["director_id", "genres", "integer"]):
        message = "Invalid director_id or genres"
    elif "release_year" in full_error_text:
        message = "Invalid release_year"
    elif "score" in full_error_text:
        message = "Score must be an integer between 1 and 10"
    else:
        message = "Invalid input"

    return JSONResponse(
        status_code=422,
        content={
            "status": "failure",
            "error": {"code": 422, "message": message}
        }
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all exception handler for application-wide errors.

    :param request: The incoming HTTP request object
    :param exc: The raised exception
    :return: Standardized JSON response based on exception type
    """
    status_code: int = 500
    message: str = "Internal server error"

    # Database integrity and attribute access errors [cite: 291]
    if isinstance(exc, (IntegrityError, AttributeError)):
        status_code = 400
        message = (
            "Movie not found" if "movie_id" in str(exc).lower()
            else "Invalid director_id or genres"
        )

    # Starlette specific HTTP exceptions
    elif isinstance(exc, StarletteHTTPException):
        if exc.status_code == 400:
            status_code = 422
            message = "Invalid director_id or genres"
        else:
            status_code = exc.status_code
            message = exc.detail

    # FastAPI and custom HTTP exceptions
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail

    # Unhandled unexpected errors
    else:
        logger.error(f"Unhandled error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "failure",
            "error": {"code": status_code, "message": message}
        }
    )