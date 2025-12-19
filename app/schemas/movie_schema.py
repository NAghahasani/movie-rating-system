from pydantic import BaseModel, Field
from typing import List, Optional

class DirectorSchema(BaseModel):
    id: int
    name: str
    class Config: from_attributes = True

class GenreSchema(BaseModel):
    name: str
    class Config: from_attributes = True

class MovieBaseSchema(BaseModel):
    id: int
    title: str
    release_year: int
    average_rating: float
    ratings_count: int
    director: Optional[DirectorSchema]
    genres: List[GenreSchema]
    class Config: from_attributes = True

class MovieListResponse(BaseModel):
    status: str
    data: dict # Will contain page, page_size, total_items, items

class MovieResponse(BaseModel):
    status: str
    data: MovieBaseSchema

class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)

class RatingResponse(BaseModel):
    status: str
    data: dict