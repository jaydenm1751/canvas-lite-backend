from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, func, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
    # helps: latest submission lookup per student per assignment
        Index("ix_submissions_lookup_latest", "assignment_id", "student_id", "submitted_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    # name: Mapped[str] = mapped_column(String(255), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    submission_file: Mapped[str | None] = mapped_column(String(1024), nullable=True)