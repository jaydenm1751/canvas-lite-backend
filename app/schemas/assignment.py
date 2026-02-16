from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class AssignmentCreate(BaseModel):
   # course_id: int
    name: str = Field(min_length=1, max_length=255)
    due_date: datetime
    allow_late: bool = False

    instructions: str | None = None
    instructions_file: str | None = None

class AssignmentOut(BaseModel):
    id: int
    course_id: int
    name: str
    due_date: datetime 
    allow_late: bool

    # longer free-form text; Text is better than huge String
    instructions: str | None
    # store a path or URL, not a file type
    instructions_file: str | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AssignmentDetailOut(BaseModel):
    id: int
    course_id: int
    name: str
    due_date: datetime
    allow_late: bool
    instructions: str | None
    has_instructions_file: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)