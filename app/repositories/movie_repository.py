"""
Repository layer for handling database operations for movies.

This module encapsulates all direct database interactions using SQLAlchemy,
providing a clean API for the service layer.
"""

from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.models import Movie, MovieRating, Genre


class MovieRepository:
    """
    Handle CRUD operations for Movie model.

    This class uses Constructor Injection to receive the database session.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the repository with a database session.

        :param db: SQLAlchemy database session
        """
        self.db = db

    def get_all_movies(
            self,
            skip: int = 0,
            limit: int = 10,
            title: Optional[str] = None,
            genre: Optional[str] = None,
            release_year: Optional[int] = None
    ) -> Tuple[List[dict], int]:
        """
        Retrieve a list of movies with optional filters.

        :param skip: Number of records to skip
        :param limit: Maximum number of records to return
        :param title: Filter by movie title
        :param genre: Filter by genre name
        :param release_year: Filter by release year
        :return: Tuple containing formatted movie list and total count
        """
        query = self.db.query(Movie).options(
            joinedload(Movie.director),
            selectinload(Movie.genres)
        )

        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))

        if release_year:
            query = query.filter(Movie.release_year == release_year)

        if genre:
            query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre}%"))

        total_items = query.distinct().count()
        movies = (
            query.distinct()
            .order_by(Movie.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        formatted_movies = [
            self._format_movie_response(movie, full_director=False)
            for movie in movies
        ]

        return formatted_movies, total_items

    def get_movie_details(self, movie_id: int) -> Optional[dict]:
        """
        Get detailed information about a specific movie.

        :param movie_id: The unique identifier of the movie
        :return: Dictionary of movie details or None if not found
        """
        movie = self.db.query(Movie).options(
            joinedload(Movie.director),
            selectinload(Movie.genres)
        ).filter(Movie.id == movie_id).first()

        if not movie:
            return None

        return self._format_movie_response(movie, full_director=True)

    def create_movie(self, movie_data: dict, genre_ids: List[int]) -> dict:
        """
        Create a new movie record in the database.

        :param movie_data: Attributes for the new movie
        :param genre_ids: List of genre IDs to associate with the movie
        :return: Formatted dictionary of the created movie
        """
        new_movie = Movie(**movie_data)

        if genre_ids:
            new_movie.genres = (
                self.db.query(Genre)
                .filter(Genre.id.in_(genre_ids))
                .all()
            )

        self.db.add(new_movie)
        self.db.commit()
        self.db.refresh(new_movie)

        return self._format_movie_response(new_movie, full_director=False)

    def update_movie(
            self,
            movie_id: int,
            movie_data: dict,
            genre_ids: Optional[List[int]]
    ) -> Optional[dict]:
        """
        Update an existing movie and its associations.

        :param movie_id: The ID of the movie to update
        :param movie_data: Dictionary of fields to update
        :param genre_ids: New list of genre IDs to link
        :return: Updated formatted movie dictionary or None
        """
        movie = self.db.query(Movie).options(
            selectinload(Movie.genres)
        ).filter(Movie.id == movie_id).first()

        if not movie:
            return None

        # Update base attributes
        for key, value in movie_data.items():
            if value is not None:
                setattr(movie, key, value)

        # Update relationships
        if genre_ids is not None:
            movie.genres = (
                self.db.query(Genre)
                .filter(Genre.id.in_(genre_ids))
                .all()
            )

        self.db.commit()
        self.db.refresh(movie)

        return self.get_movie_details(movie.id)

    def delete_movie(self, movie_id: int) -> bool:
        """
        Remove a movie and its cascade-related ratings.

        :param movie_id: The ID of the movie to delete
        :return: True if deletion was successful, False otherwise
        """
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()

        if movie:
            # Explicitly delete ratings if not handled by DB cascade
            self.db.query(MovieRating).filter(
                MovieRating.movie_id == movie_id
            ).delete()

            self.db.delete(movie)
            self.db.commit()
            return True

        return False

    def add_rating(self, movie_id: int, score: int) -> dict:
        """
        Add a new rating score for a movie.

        :param movie_id: ID of the movie
        :param score: Numeric score (1-10)
        :return: Dictionary containing the new rating record
        """
        new_rating = MovieRating(movie_id=movie_id, score=score)
        self.db.add(new_rating)
        self.db.commit()
        self.db.refresh(new_rating)

        return {
            "rating_id": new_rating.id,
            "movie_id": new_rating.movie_id,
            "score": new_rating.score,
            "rated_at": new_rating.rated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    def _format_movie_response(
            self,
            movie: Movie,
            full_director: bool = False
    ) -> dict:
        """
        Internal helper to format a Movie object into a standardized dict.

        :param movie: The SQLAlchemy Movie instance
        :param full_director: Whether to include full director bio
        :return: Formatted response dictionary
        """
        # Calculate statistics using aggregation [cite: 108]
        stats = self.db.query(
            func.avg(MovieRating.score),
            func.count(MovieRating.id)
        ).filter(MovieRating.movie_id == movie.id).first()

        response = {
            "id": movie.id,
            "title": movie.title,
            "release_year": movie.release_year,
            "director": None,
            "genres": [genre.name for genre in movie.genres],
            "cast": movie.cast,
            "average_rating": round(float(stats[0]), 1) if stats[0] else None,
            "ratings_count": stats[1]
        }

        if movie.director:
            # Inline director data formatting
            director_data = {
                "id": movie.director.id,
                "name": movie.director.name
            }
            if full_director:
                director_data.update({
                    "birth_year": movie.director.birth_year,
                    "description": movie.director.description
                })
            response["director"] = director_data

        return response