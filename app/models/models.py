"""Database models for movies, directors, and ratings."""

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

movie_genres = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)


class Director(Base):
    """Represent a movie director in the system."""

    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birth_year = Column(Integer, nullable=True)
    description = Column(String, nullable=True)

    movies = relationship("Movie", back_populates="director")


class Movie(Base):
    """Represent a movie and its related attributes."""

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    cast = Column(String, nullable=True)
    director_id = Column(Integer, ForeignKey("directors.id"))
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now()
    )

    director = relationship("Director", back_populates="movies")
    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    ratings = relationship(
        "MovieRating",
        back_populates="movie",
        cascade="all, delete-orphan"
    )


class Genre(Base):
    """Represent a movie genre."""

    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")


class MovieRating(Base):
    """Represent a single rating score for a movie."""

    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete='CASCADE'))
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    movie = relationship("Movie", back_populates="ratings")