from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any


class DirectorSchema(BaseModel):
    id: int
    name: str
    birth_year: Optional[int] = None  # Added per Doc p.13
    description: Optional[str] = None  # Added per Doc p.13
    model_config = ConfigDict(from_attributes=True)


class MovieBaseSchema(BaseModel):
    id: int
    title: str
    release_year: int
    average_rating: float = 0.0
    ratings_count: int = 0  # Required per Doc p.13
    director: Optional[DirectorSchema] = None
    genres: List[str] = []
    cast: Optional[str] = None  # Required per Doc p.13

    model_config = ConfigDict(from_attributes=True)


class MovieCreateUpdate(BaseModel):
    title: str = Field(..., example="The Godfather")
    director_id: int
    release_year: int
    cast: Optional[str] = None
    genres: List[int] = []


class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)


class StandardResponse(BaseModel):
    status: str = "success"
    data: Any