from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, require_student
from app.db.models import Course, Enrollment, User
from app.schemas.enrollment import EnrollIn, EnrollOut

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post("/", response_model=EnrollOut, status_code=201)
def enroll_in_course(payload: EnrollIn, db: Session = Depends(get_db), student: User = Depends(require_student)):
    # email = payload.email.strip().lower()
    course = db.scalar(select(Course).where(Course.id == payload.course_id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = db.scalar(select(Enrollment).
                         where(
                            (Enrollment.user_id == student.id) & (Enrollment.course_id == payload.course_id)
                         )
                        )
    if existing:
        raise HTTPException(status_code=409, detail="Student already enrolled.")

    enrolled = Enrollment(
        course_id = payload.course_id,
        user_id = student.id,
    )
    db.add(enrolled)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Student already enrolled.")
    #db.flush()
    db.refresh(enrolled)
    return enrolled

@router.delete("/{course_id}", status_code=204)
def drop_course(course_id: int, db: Session = Depends(get_db), student: User = Depends(require_student)):
    # email = payload.email.strip().lower()
    enrollment = db.scalar(
        select(Enrollment).where(
            (Enrollment.user_id == student.id) & (Enrollment.course_id == course_id)
        )
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course.")

    db.delete(enrollment)
    db.commit()
    return