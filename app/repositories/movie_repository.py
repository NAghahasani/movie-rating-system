from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.models import Movie, MovieRating, Genre


class MovieRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_movies(self, skip: int = 0, limit: int = 10, title: str = None, genre: str = None):
        # Start query with eager loading for director and genres to support JOINs (Doc p.4)
        query = self.db.query(Movie).options(
            joinedload(Movie.director),
            joinedload(Movie.genres)
        )

        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))

        if genre:
            query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre}%"))

        # Total count for pagination metadata (Doc p.7)
        total_items = query.count()
        movies = query.offset(skip).limit(limit).all()

        # Attach aggregate data (Doc p.19)
        for movie in movies:
            stats = self.db.query(
                func.avg(MovieRating.score),
                func.count(MovieRating.id)
            ).filter(MovieRating.movie_id == movie.id).first()

            movie.average_rating = round(float(stats[0]), 1) if stats[0] else 0.0
            movie.ratings_count = stats[1]

        return movies, total_items

    def get_movie_by_id(self, movie_id: int):
        movie = self.db.query(Movie).options(
            joinedload(Movie.director),
            joinedload(Movie.genres)
        ).filter(Movie.id == movie_id).first()

        if movie:
            stats = self.db.query(
                func.avg(MovieRating.score),
                func.count(MovieRating.id)
            ).filter(MovieRating.movie_id == movie.id).first()
            movie.average_rating = round(float(stats[0]), 1) if stats[0] else 0.0
            movie.ratings_count = stats[1]
        return movie

    def add_rating(self, movie_id: int, score: int):
        new_rating = MovieRating(movie_id=movie_id, score=score)
        self.db.add(new_rating)
        self.db.commit()
        self.db.refresh(new_rating)
        return new_rating