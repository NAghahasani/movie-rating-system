from sqlalchemy.orm import Session
from app.repositories.movie_repository import MovieRepository
from app.schemas.movie_schema import MovieCreateUpdate

class MovieService:
    def __init__(self, db: Session):
        self.movie_repo = MovieRepository(db)

    # Updated to include release_year filter per Doc p.10 & p.21
    def list_movies(self, page: int = 1, size: int = 10, title: str = None, genre: str = None, release_year: int = None):
        skip = (page - 1) * size
        items, total_items = self.movie_repo.get_all_movies(
            skip=skip, limit=size, title=title, genre=genre, release_year=release_year
        )
        return {
            "page": page,
            "page_size": size,
            "total_items": total_items,
            "items": items
        }

    # ... other methods remain the same ...
    def get_movie(self, movie_id: int):
        return self.movie_repo.get_movie_details(movie_id)

    def create_movie(self, movie_data: MovieCreateUpdate):
        data = movie_data.model_dump()
        genre_ids = data.pop("genres", [])
        return self.movie_repo.create_movie(data, genre_ids)

    def update_movie(self, movie_id: int, movie_data: MovieCreateUpdate):
        data = movie_data.model_dump()
        genre_ids = data.pop("genres", [])
        return self.movie_repo.update_movie(movie_id, data, genre_ids)

    def delete_movie(self, movie_id: int):
        return self.movie_repo.delete_movie(movie_id)

    def rate_movie(self, movie_id: int, score: int):
        return self.movie_repo.add_rating(movie_id, score)