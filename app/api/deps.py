from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session


from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import User


security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally db.close()


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security),
                      db: Session = Depends(get_db),) -> User:
    
    token = creds.credentials

    try:
        payload = jwt.decode(
            token, 
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=404, detail="Invalid token")
        user_id = int(sub)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


def require_instructor(user: User = Depends(get_current_user)) -> User:
    if user.role != "instructor":
        raise HTTPException(status_code=status.HTTP_403_Forbidden,
                            detail="Instructor Only",)
    return user
        
def require_student(user: User = Depends(get_current_user)) -> User:
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student only",
            )
    return user