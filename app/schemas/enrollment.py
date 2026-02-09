from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EnrollIn(BaseModel):
    course_id: int

class EnrollOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)