"""API Controllers for movie-related endpoints with Phase 2 Logging."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.logging_config import logger
from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.movie_schema import (
    MovieCreateUpdate,
    RatingCreate,
    StandardResponse
)

router = APIRouter(prefix="/api/v1/movies", tags=["Movies"])


def get_movie_service(db: Session = Depends(get_db)) -> MovieService:
    """Dependency provider for MovieService."""
    return MovieService(db)


@router.get("/", response_model=StandardResponse)
def get_movies(
        page: int = 1,
        size: int = 10,
        title: Optional[str] = None,
        genre: Optional[str] = None,
        release_year: Optional[int] = None,
        service: MovieService = Depends(get_movie_service)
):
    """List movies and log the list retrieval request as per Phase 2 requirements."""
    logger.info(f"Fetching movie list: page={page}, size={size}")

    skip = (page - 1) * size
    movies, total = service.get_all_movies(skip, size, title, genre, release_year)

    return {
        "status": "success",
        "data": {
            "page": page,
            "page_size": size,
            "total_items": total,
            "items": movies
        }
    }


@router.get("/{movie_id}", response_model=StandardResponse)
def get_movie(movie_id: int, service: MovieService = Depends(get_movie_service)):
    """Retrieve details of a single movie by ID."""
    movie = service.get_movie_details(movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"status": "success", "data": movie}


@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def add_movie(
        movie_data: MovieCreateUpdate,
        service: MovieService = Depends(get_movie_service)
):
    """Create a new movie record."""
    new_movie = service.create_movie(movie_data)
    return {"status": "success", "data": new_movie}


@router.put("/{movie_id}", response_model=StandardResponse)
def update_movie(
        movie_id: int,
        movie_data: MovieCreateUpdate,
        service: MovieService = Depends(get_movie_service)
):
    """Update movie information."""
    updated_movie = service.update_movie(movie_id, movie_data)

    if not updated_movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"status": "success", "data": updated_movie}


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, service: MovieService = Depends(get_movie_service)):
    """Delete a movie by its ID."""
    success = service.delete_movie(movie_id)

    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{movie_id}/ratings",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED
)
def rate_movie(
        movie_id: int,
        rating: RatingCreate,
        service: MovieService = Depends(get_movie_service)
):
    """Submit rating with strict Phase 2 logging requirements."""
    route_path = f"/api/v1/movies/{movie_id}/ratings"

    # Manual validation to allow logging of invalid values as warnings
    if rating.score < 1 or rating.score > 10:
        logger.warning(
            f"Invalid rating value (movie_id={movie_id}, rating={rating.score}, route={route_path})"
        )
        raise HTTPException(
            status_code=422,
            detail="Score must be an integer between 1 and 10"
        )

    # Log initial rating attempt [cite: 957-958]
    logger.info(f"rating {rating.score}, route={route_path}")
    logger.info(f"Rating movie (movie_id={movie_id}, rating={rating.score}, route={route_path})")

    try:
        result = service.add_rating(movie_id, rating.score)

        if not result:
            logger.warning(f"Invalid rating attempt: Movie {movie_id} not found")
            raise HTTPException(status_code=404, detail="Movie not found")

        # Log successful save [cite: 960]
        logger.info(f"Rating saved successfully (movie_id={movie_id}, rating={rating.score})")
        return {"status": "success", "data": result}

    except HTTPException:
        raise
    except Exception:
        # Log unexpected errors as per Phase 2 [cite: 969-970]
        logger.error(f"Failed to save rating (movie_id={movie_id}, rating={rating.score})")
        raise HTTPException(status_code=500, detail="Internal server error")