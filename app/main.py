from fastapi import FastAPI
from app.controller.movie_controller import router as movie_router

app = FastAPI(title="Movie Rating System")

# Registering routes from controllers
app.include_router(movie_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Movie Rating System API"}