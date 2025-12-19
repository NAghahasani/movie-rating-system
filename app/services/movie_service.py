from sqlalchemy.orm import Session
from app.repositories.movie_repository import MovieRepository


class MovieService:
    def __init__(self, db: Session):
        self.movie_repo = MovieRepository(db)

    def list_movies(self, page: int = 1, size: int = 10, title: str = None, genre: str = None):
        skip = (page - 1) * size
        items, total_items = self.movie_repo.get_all_movies(skip=skip, limit=size, title=title, genre=genre)

        # Structuring response as per Doc p.7-8
        return {
            "page": page,
            "page_size": size,
            "total_items": total_items,
            "items": items
        }

    def get_movie_details(self, movie_id: int):
        return self.movie_repo.get_movie_by_id(movie_id)

    def rate_movie(self, movie_id: int, score: int):
        return self.movie_repo.add_rating(movie_id, score)