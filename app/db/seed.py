from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models import User, Course, Enrollment
from app.core.security import hash_password

def get_or_create_user(db, **kwargs) -> User:
    existing = db.scalar(select(User).where(User.email == kwargs["email"]))
    if existing:
        return existing
    u = User(**kwargs)
    db.add(u)
    db.flush() # assigns id without full commit
    return u

def get_or_create_course(db, **kwargs) -> Course:
    c = Course(**kwargs)
    db.add(c)
    db.flush()
    return c

def enrollment_exists(db, user_id: int, course_id: int) -> bool:
    return db.scalar(
        select(Enrollment.id).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
        )
    ) is not None


def main():
    db = SessionLocal()
    try:
        instructor = get_or_create_user(
            db,
            email="prof@uni.edu",
            hashed_pswd=hash_password("password123"),
            role="instructor",
            first_name="Herbert",
            last_name="Garrison",
        )


        students = [
            get_or_create_user(
                db,
                email="stanmarsh@uni.edu",
                hashed_pswd=hash_password("password123"),
                role="student",
                first_name="Stan",
                last_name="Marsh",
            ),
            get_or_create_user(
                db,
                email="ericcartman@uni.edu",
                hashed_pswd=hash_password("password123"),
                role="student",
                first_name="Eric",
                last_name="Cartman",
            ),
            get_or_create_user(
                db,
                email="kylebrovlowski@uni.edu",
                hashed_pswd=hash_password("password123"),
                role="student",
                first_name="Kyle",
                last_name="Brovlowski",
            ),
        ]

        course1 = get_or_create_course(db, name="Math", owner_user_id=instructor.id)
        course2 = get_or_create_course(db, name="English", owner_user_id=instructor.id)
        courses = [course1, course2]

        for s in students:
            for c in courses:
                if not enrollment_exists(db, s.id, c.id):
                    db.add(Enrollment(user_id=s.id,course_id=c.id))
        
        db.commit()
        print("Seed complete ✅")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


    