from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class GradeCreate(BaseModel):
    # submission_id: int
    score: float = Field(ge=0)
    feedback: str | None = None


class GradeOut(BaseModel):
    id: int
    submission_id: int
    graded_at: datetime
    graded_by: int | None = None
    score: int
    feedback: str | None

    model_config = ConfigDict(from_attributes=True)
