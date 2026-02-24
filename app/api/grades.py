from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select, func
# from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, require_instructor, get_current_user, require_student
from app.db.models import Assignment, Course, Submission, User, Enrollment, Grade
from app.schemas.grade import GradeCreate, GradeOut

from datetime import datetime, timezone

router = APIRouter( tags=["grades"])

@router.put("/submissions/{submission_id}/grades", response_model=GradeOut)
def upsert_grade(
    submission_id: int,
    payload: GradeCreate,
    db: Session = Depends(get_db),
    instructor: User = Depends(require_instructor),
):
    submission = db.scalar(select(Submission).where(Submission.id == submission_id))
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    
    # assignment = db.scalar(select(Assignment).where(Assignment.id == submission.assignment_id))
    # if not assignment:
    #     raise HTTPException(status_code=404, detail="Assignment not found.")
    
    latest_submission_id = db.scalar(
        select(Submission.id)
        .where(
            (Submission.assignment_id == submission.assignment_id) & (Submission.student_id ==submission.student_id)
        )
        .order_by(Submission.submitted_at.desc(), Submission.id.desc())
        .limit(1)
    )

    if latest_submission_id != submission.id:
        raise HTTPException(status_code=409, detail=f"Can only grade lastest submission: {latest_submission_id}")
    

    grade = db.scalar(select(Grade).where(Grade.submission_id == submission_id))
    if grade:
        grade.score = payload.score
        grade.feedback = payload.feedback
        grade.graded_by = instructor.id
    else:
        grade = Grade(
            submission_id=submission.id,
            score=payload.score,
            feedback=payload.feedback,
            graded_by=instructor.id,
        )
        db.add(grade)
    
    db.commit()
    db.refresh(grade)
    return grade

@router.get("/submissions/{submission_id}/grades/me", response_model=GradeOut)
def view_my_grade(
    submission_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    submission = db.scalar(select(Submission).where(Submission.id == submission_id))
    if not submission:
        raise HTTPException(status_code=404, detail="Submission does not exist.")
    
    if submission.student_id != student.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this submission.")
    
    grade = db.scalar(select(Grade).where(Grade.submission_id == submission_id))

    if not grade:
        raise HTTPException(status_code=404, detail="Grade not available yet.")
    
    return grade
        
@router.get("/assignments/{assignment_id}/grades", response_model=list[GradeOut])
def view_class_grades_for_assigment(
    assignment_id: int,
    db: Session = Depends(get_db),
    instructor: User = Depends(require_instructor),
):
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    
    query = (
        select(Grade)
        .join(Submission, Submission.id == Grade.submission_id)
        .where(Submission.assignment_id == assignment_id)
        .order_by(Submission.student_id.desc())
    )
    return list(db.scalars(query).all())

@router.get("/assignments/{assignment_id}/grades/{student_id}", response_model=GradeOut)
def view_a_students_grade(
    assignment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    instructor: User = Depends(require_instructor),
):
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    
    student = db.scalar(select(User).where(User.id == student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    enrolled = db.scalar(select(Enrollment).where(
        (Enrollment.user_id == student_id) & (Enrollment.course_id == assignment.course_id)
    ))

    if not enrolled:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course.")
    
    latest_sub = db.scalar(
        select(Submission)
        .where(
            (Submission.assignment_id == assignment_id) & (Submission.student_id == student_id)
        )
        .order_by(Submission.submitted_at.desc(), Submission.id.desc())
        .limit(1)
    )
    if not latest_sub:
        raise HTTPException(status_code=404, detail="No submissions yet.")
    
    grade = db.scalar(select(Grade).where(Grade.submission_id == latest_sub.id))
    if not grade:
        raise HTTPException(status_code=404, detail="Submission has not been graded.")

    return grade