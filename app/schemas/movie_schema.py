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
    average_rating: Optional[float] = None  # اصلاح برای نمایش null طبق ص 15 داک
    ratings_count: int = 0
    director: Optional[Any] = None  # برای پشتیبانی از نمایش خلاصه و کامل کارگردان
    genres: List[str] = []
    cast: Optional[str] = None
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