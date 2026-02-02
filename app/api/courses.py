from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user, require_instructor
from app.db.models import Course, Enrollment, User
from app.schemas.course import CourseCreate, CourseOut

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("", response_model=CourseOut, status_code=201)
def createCourse(payload: CourseCreate, db: Session = Depends(get_db), instructor: User = Depends(require_instructor)):
    course = Course(
        name = payload.name.strip(),
        owner_user_id = instructor.id,
    )
    db.add(course)
    db.flush()

    db.add(Enrollment(user_id = instructor.id, course_id=course.id))
    db.commit()
    db.refresh(course)
    return course

@router.get("", response_model=list[CourseOut])
def list_my_courses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = (
        select(Course)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .where(Enrollment.user_id == user.id)
        .order_by(Course.id.asc())
    )
    return list(db.scalars(query).all())


#TODO register for a course with a student.
@router.post("", response_model=CourseOut, status_code=201)
def register_course():
    return 0


