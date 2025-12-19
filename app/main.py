from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.movie_schema import MovieBase

app = FastAPI(title="Movie Rating System")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Movie Rating System API"}

@app.get("/movies", response_model=List[MovieBase])
def get_movies(page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    service = MovieService(db)
    return service.list_movies(page=page, size=size)

@app.get("/movies/{movie_id}", response_model=MovieBase)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    service = MovieService(db)
    movie = service.get_movie_details(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie