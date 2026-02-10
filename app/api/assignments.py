from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, require_instructor, get_current_user, require_student
from app.db.models import Course, Enrollment, User, Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentOut

from datetime import datetime, timezone

router = APIRouter(prefix="/courses", tags=["assignments"])

# a teacher can create an assignment
@router.post("/{course_id}/assignments", response_model=AssignmentOut, status_code=201)
def create_assignment(course_id: int, payload: AssignmentCreate, db: Session = Depends(get_db), instructor: User = Depends(require_instructor)):
    
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    

    assignment = Assignment(
        course_id = course_id,
        name = payload.name.strip(),
        due_date = payload.due_date,

        instructions = payload.instructions,
        instructions_file = payload.instructions_file,
    )

    db.add(assignment)
   # db.flush()

    db.commit()
    db.refresh(assignment)
    return assignment
    

@router.get("/{course_id}/assignments", response_model=list[AssignmentOut])
def get_assignments(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.owner_user_id != user.id:
        enrolled = db.scalar(
            select(Enrollment).where(
                (Enrollment.user_id == user.id) & (Enrollment.course_id == course_id)
            )
        )
        if not enrolled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in this course.")
    now = datetime.now(timezone.utc)
    query = (
        select(Assignment)
        .where(Assignment.course_id == course_id)
    )
    if user.role == "student":
        query = query.where(
            (Assignment.due_date >= now) | (Assignment.allow_late == True)
        )

    query = query.order_by(Assignment.due_date.asc())
    return list(db.scalars(query).all())

@router.delete("/{course_id}/assignments/{assignment_id}", status_code=204)
def delete_assignment(course_id: int, assignment_id: int, db: Session = Depends(get_db), instructor: User = Depends(require_instructor)):
    course = db.scalar(select(Course).where((Course.id == course_id) & (Course.owner_user_id == instructor.id)))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found or not owned by you.")
    
    assignment = db.scalar(select(Assignment).where(
                (Assignment.course_id == course_id) & (Assignment.id == assignment_id)
            )
        )
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    db.delete(assignment)
    db.commit()
    return
   