from pydantic import BaseModel, EmailStr

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str  # "student" | "instructor"

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"