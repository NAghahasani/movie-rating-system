from sqlalchemy.orm import Session
from app.repositories.movie_repository import MovieRepository

class MovieService:
    def __init__(self, db: Session):
        self.movie_repo = MovieRepository(db)

    def list_movies(self, page: int = 1, size: int = 10):
        skip = (page - 1) * size
        return self.movie_repo.get_all_movies(skip=skip, limit=size)

    def get_movie_details(self, movie_id: int):
        return self.movie_repo.get_movie_by_id(movie_id)