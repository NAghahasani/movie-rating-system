from pydantic import BaseModel
from typing import Optional

class MovieBase(BaseModel):
    id: int
    title: str
    release_year: int
    cast: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True