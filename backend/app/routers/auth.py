from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..security import create_token, current_user, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower().strip()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return {
        "access_token": create_token(user),
        "token_type": "bearer",
        "user": {"name": user.name, "email": user.email, "role": user.role,
                 "organisation": user.organisation},
    }


@router.get("/me")
def me(user: User | None = Depends(current_user)):
    if not user:
        return {"role": "public", "name": "Guest", "email": None, "organisation": ""}
    return {"name": user.name, "email": user.email, "role": user.role,
            "organisation": user.organisation}
