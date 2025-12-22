"""Service layer for movie-related business logic."""

from sqlalchemy.orm import Session

from app.repositories.movie_repository import MovieRepository
from app.schemas.movie_schema import MovieCreateUpdate


class MovieService:
    """Coordinate business operations for movies."""

    def __init__(self, db: Session):
        """Initialize service with a database session."""
        self.movie_repo = MovieRepository(db)

    def get_all_movies(
            self,
            skip: int = 0,
            limit: int = 10,
            title: str = None,
            genre: str = None,
            release_year: int = None
    ):
        """Get paginated list of movies through repository.

        :param skip: Offset for pagination
        :param limit: Number of items per page
        :param title: Optional title filter
        :param genre: Optional genre filter
        :param release_year: Optional year filter
        :return: List of movies and total count
        """
        return self.movie_repo.get_all_movies(skip, limit, title, genre, release_year)

    def get_movie_details(self, movie_id: int):
        """Retrieve full details of a movie.

        :param movie_id: Target movie ID
        :return: Movie detail dictionary or None
        """
        return self.movie_repo.get_movie_details(movie_id)

    def create_movie(self, movie_data: MovieCreateUpdate):
        """Handle logic for creating a movie.

        :param movie_data: Validated movie data from request
        :return: Created movie response
        """
        data = movie_data.model_dump(exclude={'genres'})
        genre_ids = movie_data.genres
        return self.movie_repo.create_movie(data, genre_ids)

    def update_movie(self, movie_id: int, movie_data: MovieCreateUpdate):
        """Handle partial or full update of a movie.

        :param movie_id: ID of movie to update
        :param movie_data: New data fields
        :return: Updated movie object or None
        """
        data = movie_data.model_dump(exclude={'genres'}, exclude_unset=True)
        genre_ids = movie_data.genres
        return self.movie_repo.update_movie(movie_id, data, genre_ids)

    def delete_movie(self, movie_id: int):
        """Request movie deletion from repository.

        :param movie_id: ID of movie to delete
        :return: Boolean indicating success
        """
        return self.movie_repo.delete_movie(movie_id)

    def add_rating(self, movie_id: int, score: int):
        """Validate movie existence and add a rating.

        :param movie_id: ID of movie being rated
        :param score: Numeric score (1-10)
        :return: Rating details or None if movie not found
        """
        movie = self.movie_repo.get_movie_details(movie_id)
        if not movie:
            return None

        return self.movie_repo.add_rating(movie_id, score)

