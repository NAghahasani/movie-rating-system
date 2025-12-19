from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

# Association Table for Many-to-Many relationship between Movies and Genres
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birth_year = Column(Integer, nullable=True)
    description = Column(String, nullable=True)

    movies = relationship("Movie", back_populates="director")

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    director_id = Column(Integer, ForeignKey("directors.id", ondelete="CASCADE"))
    cast = Column(String, nullable=True)
    description = Column(String, nullable=True)

    director = relationship("Director", back_populates="movies")
    genres = relationship("Genre", secondary=movie_genres)
    ratings = relationship("MovieRating", back_populates="movie", cascade="all, delete-orphan")

class MovieRating(Base):
    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))
    score = Column(Integer, nullable=False) # Should be between 1-10
    rated_at = Column(DateTime(timezone=True), server_default=func.now())

    movie = relationship("Movie", back_populates="ratings")