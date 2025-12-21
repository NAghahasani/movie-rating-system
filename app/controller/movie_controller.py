from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.movie_schema import StandardResponse, MovieCreateUpdate, RatingCreate

router = APIRouter(prefix="/api/v1/movies", tags=["Movies"])


@router.get("/", response_model=StandardResponse)
def get_movies(
        page: int = 1,
        size: int = 10,
        title: str = Query(None),
        genre: str = Query(None),
        release_year: int = Query(None),
        db: Session = Depends(get_db)
):
    service = MovieService(db)
    result = service.list_movies(
        page=page,
        size=size,
        title=title,
        genre=genre,
        release_year=release_year
    )
    return StandardResponse(data=result)


@router.get("/{movie_id}", response_model=StandardResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    service = MovieService(db)
    movie = service.get_movie(movie_id)
    if not movie:
        return StandardResponse(
            status="failure",
            data={"code": 404, "message": "Movie not found"}
        )
    return StandardResponse(data=movie)


@router.post("/", status_code=201, response_model=StandardResponse)
def add_movie(movie_data: MovieCreateUpdate, db: Session = Depends(get_db)):
    service = MovieService(db)
    new_movie = service.create_movie(movie_data)
    return StandardResponse(data=new_movie)


@router.put("/{movie_id}", response_model=StandardResponse)
def update_movie(movie_id: int, movie_data: MovieCreateUpdate, db: Session = Depends(get_db)):
    service = MovieService(db)
    updated_movie = service.update_movie(movie_id, movie_data)
    if not updated_movie:
        return StandardResponse(
            status="failure",
            data={"code": 404, "message": "Movie not found"}
        )
    return StandardResponse(data=updated_movie)


@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    service = MovieService(db)
    success = service.delete_movie(movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
    return Response(status_code=204)


# Functionality #7: Rating with Trailing Slash according to Doc p.22
@router.post("/{movie_id}/ratings/", status_code=201, response_model=StandardResponse)
def rate_movie(movie_id: int, rating: RatingCreate, db: Session = Depends(get_db)):
    service = MovieService(db)
    if not service.get_movie(movie_id):
        return StandardResponse(
            status="failure",
            data={"code": 404, "message": "Movie not found"}
        )

    new_rating = service.rate_movie(movie_id, rating.score)
    return StandardResponse(data={
        "rating_id": new_rating.id,
        "movie_id": movie_id,
        "score": new_rating.score
    })