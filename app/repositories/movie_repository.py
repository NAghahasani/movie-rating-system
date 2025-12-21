from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.models import Movie, MovieRating, Genre


class MovieRepository:
    def __init__(self, db: Session):
        self.db = db

    # Covers Functionality #1 & #2 (List, Pagination, Filter with AND logic)
    def get_all_movies(self, skip: int = 0, limit: int = 10, title: str = None, genre: str = None,
                       release_year: int = None):
        query = self.db.query(Movie).options(joinedload(Movie.director), joinedload(Movie.genres))

        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        if release_year:
            query = query.filter(Movie.release_year == release_year)
        if genre:
            query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre}%"))

        total_items = query.count()
        movies = query.offset(skip).limit(limit).all()
        return self._format_movies(movies), total_items

    # Covers Functionality #3 & #8 (Details with Computed Fields)
    def get_movie_details(self, movie_id: int):
        movie = self.db.query(Movie).options(joinedload(Movie.director), joinedload(Movie.genres)).filter(
            Movie.id == movie_id).first()
        if not movie: return None

        stats = self.db.query(func.avg(MovieRating.score), func.count(MovieRating.id)).filter(
            MovieRating.movie_id == movie.id).first()

        return {
            "id": movie.id, "title": movie.title, "release_year": movie.release_year, "cast": movie.cast,
            "average_rating": round(float(stats[0]), 1) if stats[0] else 0.0,
            "ratings_count": stats[1],
            "director": {"id": movie.director.id, "name": movie.director.name, "birth_year": movie.director.birth_year,
                         "description": movie.director.description} if movie.director else None,
            "genres": [g.name for g in movie.genres]
        }

    # Covers Functionality #4 (Add Movie)
    def create_movie(self, movie_data: dict, genre_ids: List[int]):
        new_movie = Movie(**movie_data)
        if genre_ids:
            genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            new_movie.genres = genres
        self.db.add(new_movie)
        self.db.commit()
        return self.get_movie_details(new_movie.id)

    # Covers Functionality #5 (Update & Sync Genres)
    def update_movie(self, movie_id: int, movie_data: dict, genre_ids: List[int]):
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie: return None
        for key, value in movie_data.items(): setattr(movie, key, value)
        if genre_ids is not None:
            movie.genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
        self.db.commit()
        return self.get_movie_details(movie.id)

    # Covers Functionality #6 (Cascade Delete)
    def delete_movie(self, movie_id: int):
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            movie.genres = []
            self.db.query(MovieRating).filter(MovieRating.movie_id == movie_id).delete()
            self.db.delete(movie)
            self.db.commit()
            return True
        return False

    # Covers Functionality #7 (Rate Movie)
    def add_rating(self, movie_id: int, score: int):
        new_rating = MovieRating(movie_id=movie_id, score=score)
        self.db.add(new_rating)
        self.db.commit()
        return new_rating

    def _format_movies(self, movies):
        return [self._format_list_movie(m) for m in movies]

    def _format_list_movie(self, m):
        stats = self.db.query(func.avg(MovieRating.score), func.count(MovieRating.id)).filter(
            MovieRating.movie_id == m.id).first()
        return {
            "id": m.id, "title": m.title, "release_year": m.release_year,
            "average_rating": round(float(stats[0]), 1) if stats[0] else 0.0,
            "ratings_count": stats[1],
            "director": {"id": m.director.id, "name": m.director.name} if m.director else None,
            "genres": [g.name for g in m.genres]
        }