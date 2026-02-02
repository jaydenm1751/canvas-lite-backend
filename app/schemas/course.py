from pydantic import BaseModel, Field
from datetime import datetime

class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

class CourseOut(BaseModel):
    id: int
    name: str
    owner_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
