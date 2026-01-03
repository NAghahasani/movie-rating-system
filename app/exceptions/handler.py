"""Global exception handlers for consistent API error responses."""

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.logging_config import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    full_error_text = str(errors).lower()
    if "director_id" in full_error_text or "genres" in full_error_text or "type_error.integer" in full_error_text:
        message = "Invalid director_id or genres"
    elif "release_year" in full_error_text:
        message = "Invalid release_year"
    elif "score" in full_error_text:
        message = "Score must be an integer between 1 and 10"
    else:
        message = "Invalid input"
    return JSONResponse(status_code=422, content={"status": "failure", "error": {"code": 422, "message": message}})


async def global_exception_handler(request: Request, exc: Exception):
    status_code = 500
    message = "Internal server error"

    if isinstance(exc, (IntegrityError, AttributeError)):
        status_code = 400
        if "movie_id" in str(exc).lower():
            message = "Movie not found"
        else:
            message = "Invalid director_id or genres"
    elif isinstance(exc, StarletteHTTPException):
        if exc.status_code == 400:
            status_code = 422
            message = "Invalid director_id or genres"
        else:
            status_code = exc.status_code
            message = exc.detail
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail
    else:
        logger.error(f"Unhandled error: {str(exc)}", exc_info=True)

    return JSONResponse(status_code=status_code,
                        content={"status": "failure", "error": {"code": status_code, "message": message}})
