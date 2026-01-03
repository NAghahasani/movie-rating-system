"""Repository layer for handling database operations for movies."""

from typing import List

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, distinct

from app.models.models import Movie, MovieRating, Genre


class MovieRepository:
    """Handle CRUD operations for Movie model."""

    def __init__(self, db: Session):
        self.db = db

    def get_all_movies(
            self,
            skip: int = 0,
            limit: int = 10,
            title: str = None,
            genre: str = None,
            release_year: int = None
    ):
        """Retrieve a list of movies with optional filters.

        :param skip: Number of records to skip
        :param limit: Maximum number of records to return
        :param title: Filter by movie title
        :param genre: Filter by genre name
        :param release_year: Filter by release year
        :return: Tuple of (movie list, total count)
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
        movies = query.distinct().order_by(Movie.id.asc()).offset(skip).limit(limit).all()

        return [self._format_movie_response(m, full_director=False) for m in movies], total_items

    def get_movie_details(self, movie_id: int):
        """Get detailed information about a specific movie.

        :param movie_id: The ID of the movie
        :return: Dictionary of movie details or None
        """
        movie = self.db.query(Movie).options(
            joinedload(Movie.director),
            selectinload(Movie.genres)
        ).filter(Movie.id == movie_id).first()

        if not movie:
            return None

        return self._format_movie_response(movie, full_director=True)

    def create_movie(self, movie_data: dict, genre_ids: List[int]):
        """Create a new movie record.

        :param movie_data: Dictionary containing movie attributes
        :param genre_ids: List of genre IDs to associate
        :return: Formatted movie dictionary
        """
        new_movie = Movie(**movie_data)

        if genre_ids:
            new_movie.genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()

        self.db.add(new_movie)
        self.db.commit()
        self.db.refresh(new_movie)
        return self._format_movie_response(new_movie, full_director=False)

    def update_movie(self, movie_id: int, movie_data: dict, genre_ids: List[int]):
        """Update an existing movie record.

        :param movie_id: The ID of the movie to update
        :param movie_data: Updated attributes
        :param genre_ids: New list of genre IDs
        :return: Updated formatted movie or None
        """
        movie = self.db.query(Movie).options(
            selectinload(Movie.genres)
        ).filter(Movie.id == movie_id).first()

        if not movie:
            return None

        for key, value in movie_data.items():
            if value is not None:
                setattr(movie, key, value)

        if genre_ids is not None:
            movie.genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()

        self.db.commit()
        self.db.refresh(movie)
        return self.get_movie_details(movie.id)

    def delete_movie(self, movie_id: int) -> bool:
        """Delete a movie and its ratings.

        :param movie_id: The ID of the movie
        :return: True if deleted, False otherwise
        """
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()

        if movie:
            self.db.query(MovieRating).filter(MovieRating.movie_id == movie_id).delete()
            self.db.delete(movie)
            self.db.commit()
            return True

        return False

    def add_rating(self, movie_id: int, score: int) -> dict:
        """Add a rating score to a movie.

        :param movie_id: ID of the movie
        :param score: Rating score (1-10)
        :return: Dictionary with rating details
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

    def _format_movie_response(self, m: Movie, full_director: bool = False) -> dict:
        """Format the movie object into a standard response dictionary."""
        stats = self.db.query(
            func.avg(MovieRating.score),
            func.count(MovieRating.id)
        ).filter(MovieRating.movie_id == m.id).first()

        response = {
            "id": m.id,
            "title": m.title,
            "release_year": m.release_year,
            "director": None,
            "genres": [g.name for g in m.genres],
            "cast": m.cast,
            "average_rating": round(float(stats[0]), 1) if stats[0] else None,
            "ratings_count": stats[1],
             #"updated_at": m.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ") if m.updated_at else None
        }

        if m.director:
            if full_director:
                response["director"] = {
                    "id": m.director.id,
                    "name": m.director.name,
                    "birth_year": m.director.birth_year,
                    "description": m.director.description
                }
            else:
                response["director"] = {
                    "id": m.director.id,
                    "name": m.director.name
                }
        return response