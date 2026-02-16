from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class SubmissionMetaIn(BaseModel):
    comment: str | None = None


class SubmissionOut(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    attempt: int
    submitted_at: datetime
    submission_file: str | None

    model_config = ConfigDict(from_attributes=True)
