"""Pydantic schemas for movie and rating data validation."""

from typing import List, Optional, Any

from pydantic import BaseModel, ConfigDict


class DirectorSchema(BaseModel):
    """Schema for director details."""

    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MovieBaseSchema(BaseModel):
    """Base schema for movie information displayed in responses."""

    id: int
    title: str
    release_year: int
    average_rating: Optional[float] = None
    ratings_count: int = 0
    director: Optional[Any] = None
    genres: List[str] = []
    cast: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MovieCreateUpdate(BaseModel):
    """Schema for creating or updating a movie record."""

    title: Optional[str] = None
    director_id: Optional[int] = None
    release_year: Optional[int] = None
    cast: Optional[str] = None
    genres: Optional[List[int]] = None


class RatingCreate(BaseModel):
    """
    Schema for submitting a new movie rating.
    Manual validation is performed in the controller for Phase 2 logging requirements.
    """

    score: int


class StandardResponse(BaseModel):
    """Standardized API response format."""

    status: str = "success"
    data: Any