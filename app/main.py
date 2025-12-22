"""Main application entry point for Movie Rating System."""

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.logging_config import logger
from app.controller.movie_controller import router as movie_router
from app.exceptions.handler import global_exception_handler, validation_exception_handler


# Initialize the FastAPI application
app = FastAPI(title="Movie Rating System")

<<<<<<< Updated upstream
# Register custom exception handlers for structured failure responses
=======
>>>>>>> Stashed changes
app.add_exception_handler(HTTPException, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

<<<<<<< Updated upstream
# Include the movie router
app.include_router(movie_router)


=======
app.include_router(movie_router)

>>>>>>> Stashed changes
@app.get("/", include_in_schema=False)
def read_root():
    """
    Root endpoint for service welcome message.
    Hidden from Swagger documentation.
    """
    return {"message": "Welcome to Movie Rating System API"}