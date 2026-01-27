from datetime import datetime
from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, func, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (UniqueConstraint("submission_id", name="uq_gades_submission"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    #maybe put a graded_by tag field if allowing peer grading etc...

    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(), nullable=False)

    graded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

