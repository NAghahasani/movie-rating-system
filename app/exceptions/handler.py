from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "failure",
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail
                }
            }
        )
    # For unhandled server errors
    return JSONResponse(
        status_code=500,
        content={
            "status": "failure",
            "error": {
                "code": 500,
                "message": str(exc)
            }
        }
    )