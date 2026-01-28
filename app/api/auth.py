from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session


from app.db.session import SessionLocal
from app.db.models import User
from app.schemas.auth import RegisterIn, TokenOut
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
        existing = db.scalar(select(User).where(User.email == payload.email))
        if existing:
            raise HTTPException(status_code=409, detail="email alreday exists.")
        
        if payload.role not in ("student", "instructor", "ta"):
            raise HTTPException(status_code=400, detail="Invalid role")
        
        user = User(
            email = payload.email,
            hashed_pswd= hash_password(payload.password),
            role = payload.role,
            first_name = payload.first_name,
            last_name= payload.last_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(str(user.id))

        return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.hashed_pswd):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password.",)
    token = create_access_token(str(user.id))
    return TokenOut(access_token=token)

@router.post("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }
