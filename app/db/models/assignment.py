from datetime import datetime
from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Assignment(Base):
    __tablename__= "assignments"
    __table_args__ = (UniqueConstraint("course_id", "name", name="uq_assignment_course_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    allow_late: Mapped[bool] = mapped_column(default=False, nullable=False) 

    # longer free-form text; Text is better than huge String
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    # store a path or URL, not a file type
    instructions_file: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        )

