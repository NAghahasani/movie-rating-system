from fastapi import FastAPI
from app.controller.movie_controller import router as movie_router
from app.exceptions.handler import global_exception_handler

app = FastAPI(title="Movie Rating System")

# Register the global exception handler for all Exception types
app.add_exception_handler(Exception, global_exception_handler)

# Include routers with versioning prefix as per Doc p.22
app.include_router(movie_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Movie Rating System API"}