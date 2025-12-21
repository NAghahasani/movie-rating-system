from sqlalchemy.orm import Session
from app.repositories.movie_repository import MovieRepository
from app.schemas.movie_schema import MovieCreateUpdate

class MovieService:
    def __init__(self, db: Session):
        self.movie_repo = MovieRepository(db)

    def get_all_movies(self, skip: int = 0, limit: int = 10, title: str = None, genre: str = None, release_year: int = None):
        return self.movie_repo.get_all_movies(skip, limit, title, genre, release_year)

    def get_movie_details(self, movie_id: int):
        return self.movie_repo.get_movie_details(movie_id)

    def create_movie(self, movie_data: MovieCreateUpdate):
        data = movie_data.model_dump(exclude={'genres'})
        genre_ids = movie_data.genres
        return self.movie_repo.create_movie(data, genre_ids)

    def update_movie(self, movie_id: int, movie_data: MovieCreateUpdate):
        data = movie_data.model_dump(exclude={'genres'}, exclude_unset=True)
        genre_ids = movie_data.genres
        return self.movie_repo.update_movie(movie_id, data, genre_ids)

    def delete_movie(self, movie_id: int):
        return self.movie_repo.delete_movie(movie_id)

    def add_rating(self, movie_id: int, score: int):
        movie = self.movie_repo.get_movie_details(movie_id)
        if not movie:
            return None
        return self.movie_repo.add_rating(movie_id, score)