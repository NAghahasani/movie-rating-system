from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.controller.movie_controller import router as movie_router
from app.exceptions.handler import global_exception_handler, validation_exception_handler

app = FastAPI(title="Movie Rating System")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(movie_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Movie Rating System API"}