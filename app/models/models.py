"""
Database models for movies, directors, and ratings.

This module defines the SQLAlchemy ORM models and their relationships
to represent the core entities of the movie rating system.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

# Association table for Many-to-Many relationship between Movies and Genres
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column(
        "movie_id",
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "genre_id",
        Integer,
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Director(Base):
    """
    Represent a movie director in the system.

    Attributes:
        id: Unique identifier for the director.
        name: Full name of the director.
        birth_year: Year the director was born.
        description: Biographical information.
        movies: Relationship to the Movie model.
    """

    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birth_year = Column(Integer, nullable=True)
    description = Column(String, nullable=True)

    # Relationships
    movies = relationship("Movie", back_populates="director")


class Movie(Base):
    """
    Represent a movie and its related attributes.

    Attributes:
        id: Unique identifier for the movie.
        title: Title of the movie.
        release_year: Year of cinema release.
        cast: String representation of main cast members.
        director_id: Foreign key to the director.
    """

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    cast = Column(String, nullable=True)
    director_id = Column(Integer, ForeignKey("directors.id"))

    # Relationships
    director = relationship("Director", back_populates="movies")
    genres = relationship(
        "Genre",
        secondary=movie_genres,
        back_populates="movies"
    )
    ratings = relationship(
        "MovieRating",
        back_populates="movie",
        cascade="all, delete-orphan"
    )


class Genre(Base):
    """
    Represent a movie genre.

    Attributes:
        id: Unique identifier for the genre.
        name: Name of the genre (e.g., Sci-Fi).
        description: Brief description of the genre.
    """

    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    # Relationships
    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")


class MovieRating(Base):
    """
    Represent a single rating score for a movie.

    Attributes:
        id: Unique identifier for the rating.
        movie_id: ID of the movie being rated.
        score: Integer value between 1 and 10.
        rated_at: Timestamp of when the rating was submitted.
    """

    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))
    score = Column(Integer, nullable=False)

    # Synchronized with the database schema
    rated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    movie = relationship("Movie", back_populates="ratings")