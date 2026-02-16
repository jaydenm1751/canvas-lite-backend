from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select, func
# from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, require_instructor, get_current_user, require_student
from app.db.models import Assignment, Course, Submission, User, Enrollment
from app.schemas.submission import SubmissionOut, SubmissionMetaIn
from app.schemas.assignment import AssignmentDetailOut

from datetime import datetime, timezone

router = APIRouter( tags=["submissions"])

UPLOAD_ROOT = Path("uploads/submissions")

@router.get("/assignments/{assignment_id}", response_model=AssignmentDetailOut)
def view_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.scalar(select(Course).where(Course.id == assignment.course_id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # allow if owner OR enrolled
    if course.owner_user_id != user.id:
        enrolled = db.scalar(
            select(Enrollment).where(
                (Enrollment.user_id == user.id) & (Enrollment.course_id == course.id)
            )
        )
        if not enrolled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in this course")

    # build detail response without exposing file path
    return {
        "id": assignment.id,
        "course_id": assignment.course_id,
        "name": assignment.name,
        "due_date": assignment.due_date,
        "allow_late": assignment.allow_late,
        "instructions": assignment.instructions,
        "has_instructions_file": bool(assignment.instructions_file),
        "created_at": assignment.created_at,
    }

@router.post("/assignments/{assignment_id}/submissions", response_model=SubmissionOut, status_code=201)
def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    
    enrolled = db.scalar(select(Enrollment).
                        where( (Enrollment.user_id == student.id) & (Enrollment.course_id == Assignment.course_id)))
    
    if not enrolled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in this course.")

    now = datetime.now(timezone.utc)
    if (assignment.due_date < now) and (not getattr(assignment, "allow_late", False)):
        raise HTTPException(status_code=400, detail="Late submissions not allowed.")
    
    last_attempt = db.scalar(
        select(func.max(Submission.attempt)).where(
            (Submission.assignment_id == assignment_id) & (Submission.student_id == student.id)
        )
    )

    next_attempt = (last_attempt or 0) + 1

    orig_name = Path(file.filename or "submission").name
    course_id = assignment.course_id
    target_dir = UPLOAD_ROOT / f"course_{course_id}" / f"assignment_{assignment_id}" / f"user_{student.id}"
    target_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"attempt_{next_attempt}_{orig_name}"
    stored_path = target_dir / stored_name

    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    stored_path.write_bytes(contents)

    # 6) create DB row
    submission = Submission(
        assignment_id=assignment_id,
        student_id=student.id,
        attempt=next_attempt,
        submission_file=str(stored_path),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/assignments/{assignment_id}/submissions/me/latest", response_model=SubmissionOut, status_code=201)
def my_latest_submission(assignment_id: int, db: Session = Depends(get_db), student: User = Depends(get_current_user)):
    assert_can_access_assignment(db, assignment_id, student)
    sub = get_latest_submission(db, assignment_id, student.id)
    if not sub:
        raise HTTPException(status_code=404, detail="No submissions yet")
    return sub

@router.get("/assignments/{assignment_id}/submissions/me", response_model=list[SubmissionOut])
def my_submission_history(
    assignment_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    assert_can_access_assignment(db, assignment_id, student)
    return get_submission_history(db, assignment_id, student.id)

@router.get("/assignments/{assignment_id}/submissions/{student_id}", response_model=list[SubmissionOut])
def student_submission_history(
    assignment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    instructor: User = Depends(require_instructor),
):
    assignment = assert_can_access_assignment(db, assignment_id, instructor)  # owner check already ok
    # you also might want to ensure student_id is enrolled in assignment.course_id
    student_enrolled = db.scalar(select(Enrollment).
                                 where((Enrollment.user_id == student_id) & (Enrollment.course_id == assignment.course_id)))
    if not student_enrolled:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course.")
    return get_submission_history(db, assignment_id, student_id)

@router.get("/assignments/{assignment_id}/submissions/{student_id}/latest", response_model=SubmissionOut)
def student_latest_submission(
    assignment_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    instructor: User = Depends(require_instructor),
):
    assignment = assert_can_access_assignment(db, assignment_id, instructor)
    student_enrolled = db.scalar(select(Enrollment).
                                 where((Enrollment.user_id == student_id) & (Enrollment.course_id == assignment.course_id)))
    if not student_enrolled:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course.")

    sub = get_latest_submission(db, assignment_id, student_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No submissions yet")
    
    return sub


    
    



def assert_can_access_assignment(db: Session, assignment_id: int, user: User) -> Assignment:
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.scalar(select(Course).where(Course.id == assignment.course_id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # owner can always access
    if course.owner_user_id == user.id:
        return assignment

    enrolled = db.scalar(
        select(Enrollment).where(
            (Enrollment.user_id == user.id) & (Enrollment.course_id == course.id)
        )
    )
    if not enrolled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in this course")

    return assignment


def get_latest_submission(db: Session, assignment_id: int, student_id: int) -> Submission | None:
    q = (
        select(Submission)
        .where((Submission.assignment_id == assignment_id) & (Submission.student_id == student_id))
        .order_by(Submission.submitted_at.desc())
        .limit(1)
    )
    return db.scalar(q)


def get_submission_history(db: Session, assignment_id: int, student_id: int) -> list[Submission]:
    q = (
        select(Submission)
        .where((Submission.assignment_id == assignment_id) & (Submission.student_id == student_id))
        .order_by(Submission.submitted_at.desc())
    )
    return list(db.scalars(q).all())