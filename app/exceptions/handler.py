from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = errors[0].get("msg") if errors else "Invalid input"

    for error in errors:
        loc = str(error.get("loc"))
        if "release_year" in loc:
            message = "Invalid release_year"
            break
        elif "score" in loc:
            message = "Score must be an integer between 1 and 10"
            break

    return JSONResponse(
        status_code=422,
        content={
            "status": "failure",
            "error": {
                "code": 422,
                "message": message
            }
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    status_code = 500
    message = str(exc)

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "failure",
            "error": {
                "code": status_code,
                "message": message
            }
        }
    )