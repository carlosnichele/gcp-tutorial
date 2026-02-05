from pydantic import BaseModel, Field, validator
from typing import Optional

class ItemCreate(BaseModel):
    id: int = Field(..., gt=0, description="ID must be a positive integer")
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

    @validator("name")
    def name_must_be_clean(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v

class ItemRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
