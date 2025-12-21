from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any

class DirectorSchema(BaseModel):
    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class MovieBaseSchema(BaseModel):
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
    title: Optional[str] = None
    director_id: Optional[int] = None
    release_year: Optional[int] = None
    cast: Optional[str] = None
    genres: Optional[List[int]] = None

class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)

class StandardResponse(BaseModel):
    status: str = "success"
    data: Any