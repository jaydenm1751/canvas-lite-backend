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

