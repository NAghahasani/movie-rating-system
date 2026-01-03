"""
API Controllers for movie-related endpoints.

This module handles incoming HTTP requests, performs basic validation,
and orchestrates data flow between the client and the service layer.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.logging_config import logger
from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.movie_schema import MovieCreateUpdate, RatingCreate, StandardResponse

# Create router with prefix and tags for organization [cite: 62]
router = APIRouter(prefix="/api/v1/movies", tags=["Movies"])


def get_movie_service(db: Session = Depends(get_db)) -> MovieService:
    """
    Dependency provider for MovieService using Constructor Injection. [cite: 247]

    :param db: SQLAlchemy database session [cite: 134]
    :return: An instance of MovieService
    """
    return MovieService(db)


@router.get("/", response_model=StandardResponse)
def get_movies(
    page: int = 1,
    size: int = 10,
    title: Optional[str] = None,
    genre: Optional[str] = None,
    release_year: Optional[int] = None,
    service: MovieService = Depends(get_movie_service)
) -> dict:
    """
    Retrieve a paginated list of movies with optional filters.

    :param page: Page number for pagination
    :param size: Number of items per page
    :param title: Optional title filter
    :param genre: Optional genre filter
    :param release_year: Optional release year filter
    :param service: Injected movie service [cite: 238]
    :return: Standardized response with movie data
    """
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
def get_movie(
    movie_id: int,
    service: MovieService = Depends(get_movie_service)
) -> dict:
    """
    Retrieve details of a specific movie by its ID.

    :param movie_id: Unique identifier of the movie
    :param service: Injected movie service
    :return: Movie details
    :raises HTTPException: 404 if movie not found [cite: 103]
    """
    movie = service.get_movie_details(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"status": "success", "data": movie}


@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def add_movie(
    movie_data: MovieCreateUpdate,
    service: MovieService = Depends(get_movie_service)
) -> dict:
    """
    Create a new movie record.

    :param movie_data: Data for the new movie [cite: 116]
    :param service: Injected movie service
    :return: Created movie data
    """
    new_movie = service.create_movie(movie_data)
    return {"status": "success", "data": new_movie}


@router.put("/{movie_id}", response_model=StandardResponse)
def update_movie(
    movie_id: int,
    movie_data: MovieCreateUpdate,
    service: MovieService = Depends(get_movie_service)
) -> dict:
    """
    Update an existing movie record.

    :param movie_id: ID of the movie to update
    :param movie_data: Updated movie fields
    :param service: Injected movie service
    :return: Updated movie data
    """
    updated_movie = service.update_movie(movie_id, movie_data)
    if not updated_movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"status": "success", "data": updated_movie}


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    service: MovieService = Depends(get_movie_service)
) -> Response:
    """
    Delete a movie record.

    :param movie_id: ID of the movie to remove
    :param service: Injected movie service
    :return: Empty response with 204 status
    """
    success = service.delete_movie(movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{movie_id}/ratings", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def rate_movie(
    movie_id: int,
    rating: RatingCreate,
    service: MovieService = Depends(get_movie_service)
) -> dict:
    """
    Submit a rating for a movie.

    :param movie_id: ID of the movie being rated
    :param rating: Rating data containing the score
    :param service: Injected movie service
    :return: Created rating details
    """
    route_path = f"/api/v1/movies/{movie_id}/ratings"

    # Validation and Warning Logging
    if rating.score < 1 or rating.score > 10:
        logger.warning(
            f"Invalid rating value (movie_id={movie_id}, "
            f"rating={rating.score}, route={route_path})"
        )
        raise HTTPException(
            status_code=422,
            detail="Score must be an integer between 1 and 10"
        )

    # Initial Progress Logging
    logger.info(
        f"Rating movie (movie_id={movie_id}, rating={rating.score}, "
        f"route={route_path})"
    )

    try:
        result = service.add_rating(movie_id, rating.score)

        if not result:
            logger.warning(f"Failed to save rating: Movie {movie_id} not found")
            raise HTTPException(status_code=404, detail="Movie not found")

        # Success Logging
        logger.info(
            f"Rating saved successfully (movie_id={movie_id}, rating={rating.score})"
        )
        return {"status": "success", "data": result}

    except HTTPException:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise
    except Exception as exc:
        # Error Logging
        logger.error(
            f"Failed to save rating (movie_id={movie_id}, rating={rating.score})"
        )
        raise exc