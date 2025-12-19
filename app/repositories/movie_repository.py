from sqlalchemy.orm import Session
from app.models.models import Movie, Genre, Director

class MovieRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_movies(self, skip: int = 0, limit: int = 10):
        return self.db.query(Movie).offset(skip).limit(limit).all()

    def get_movie_by_id(self, movie_id: int):
        return self.db.query(Movie).filter(Movie.id == movie_id).first()