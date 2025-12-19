from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.movie_schema import MovieResponse, MovieListResponse, RatingCreate, RatingResponse

router = APIRouter(prefix="/api/v1/movies", tags=["Movies"])

@router.get("/", response_model=MovieListResponse)
def get_movies(
    page: int = 1,
    size: int = 10,
    title: str = Query(None),
    genre: str = Query(None),
    db: Session = Depends(get_db)
):
    service = MovieService(db)
    result = service.list_movies(page=page, size=size, title=title, genre=genre)
    return {"status": "success", "data": result}

@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    service = MovieService(db)
    movie = service.get_movie_details(movie_id)
    if not movie:
        return {"status": "failure", "error": {"code": 404, "message": "Movie not found"}}
    return {"status": "success", "data": movie}

@router.post("/{movie_id}/ratings", status_code=201)
def rate_movie(movie_id: int, rating: RatingCreate, db: Session = Depends(get_db)):
    service = MovieService(db)
    if not service.get_movie_details(movie_id):
        raise HTTPException(status_code=404, detail="Movie not found")
    new_rating = service.rate_movie(movie_id, rating.score)
    return {
        "status": "success",
        "data": {
            "rating_id": new_rating.id,
            "movie_id": movie_id,
            "score": new_rating.score
        }
    }