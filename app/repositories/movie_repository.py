from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.models import Movie, MovieRating, Genre


class MovieRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_movies(self, skip: int = 0, limit: int = 10, title: str = None, genre: str = None):
        query = self.db.query(Movie).options(joinedload(Movie.director), joinedload(Movie.genres))

        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        if genre:
            query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre}%"))

        total_items = query.count()
        movies = query.offset(skip).limit(limit).all()
        return self._format_movies(movies), total_items

    def get_movie_details(self, movie_id: int):
        movie = self.db.query(Movie).options(
            joinedload(Movie.director),
            joinedload(Movie.genres)
        ).filter(Movie.id == movie_id).first()
        return self._format_single_movie(movie) if movie else None

    def create_movie(self, movie_data: dict, genre_ids: List[int]):
        new_movie = Movie(**movie_data)
        if genre_ids:
            genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            new_movie.genres = genres
        self.db.add(new_movie)
        self.db.commit()
        return self.get_movie_details(new_movie.id)

    def update_movie(self, movie_id: int, movie_data: dict, genre_ids: List[int]):
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return None

        for key, value in movie_data.items():
            setattr(movie, key, value)

        if genre_ids is not None:
            genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            movie.genres = genres

        self.db.commit()
        return self.get_movie_details(movie.id)

    def delete_movie(self, movie_id: int):
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            self.db.delete(movie)
            self.db.commit()
            return True
        return False

    def add_rating(self, movie_id: int, score: int):
        new_rating = MovieRating(movie_id=movie_id, score=score)
        self.db.add(new_rating)
        self.db.commit()
        self.db.refresh(new_rating)
        return new_rating

    def _format_movies(self, movies):
        return [self._format_single_movie(m) for m in movies]

    def _format_single_movie(self, m):
        stats = self.db.query(
            func.avg(MovieRating.score),
            func.count(MovieRating.id)
        ).filter(MovieRating.movie_id == m.id).first()

        return {
            "id": m.id,
            "title": m.title,
            "release_year": m.release_year,
            "cast": m.cast,
            "average_rating": round(float(stats[0]), 1) if stats[0] else 0.0,
            "ratings_count": stats[1],
            "director": {"id": m.director.id, "name": m.director.name} if m.director else None,
            "genres": [g.name for g in m.genres]
        }