from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.movie_schema import MovieBaseSchema, MovieCreateUpdate, RatingCreate, StandardResponse

router = APIRouter(prefix="/api/v1/movies", tags=["Movies"])

def get_movie_service(db: Session = Depends(get_db)):
    return MovieService(db)

@router.get("/", response_model=StandardResponse)
def get_movies(page: int = 1, size: int = 10, title: Optional[str] = None, genre: Optional[str] = None, release_year: Optional[int] = None, service: MovieService = Depends(get_movie_service)):
    skip = (page - 1) * size
    movies, total = service.get_all_movies(skip, size, title, genre, release_year)
    return {"status": "success", "data": {"page": page, "page_size": size, "total_items": total, "items": movies}}

@router.get("/{movie_id}", response_model=StandardResponse)
def get_movie(movie_id: int, service: MovieService = Depends(get_movie_service)):
    movie = service.get_movie_details(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"status": "success", "data": movie}

@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def add_movie(movie_data: MovieCreateUpdate, service: MovieService = Depends(get_movie_service)):
    new_movie = service.create_movie(movie_data)
    return {"status": "success", "data": new_movie}

@router.put("/{movie_id}", response_model=StandardResponse)
def update_movie(movie_id: int, movie_data: MovieCreateUpdate, service: MovieService = Depends(get_movie_service)):
    updated_movie = service.update_movie(movie_id, movie_data)
    if not updated_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"status": "success", "data": updated_movie}

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, service: MovieService = Depends(get_movie_service)):
    success = service.delete_movie(movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{movie_id}/ratings", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def rate_movie(movie_id: int, rating: RatingCreate, service: MovieService = Depends(get_movie_service)):
    result = service.add_rating(movie_id, rating.score)
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"status": "success", "data": result}