from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "name": user.name,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_ttl_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User | None:
    """Anonymous access is allowed - it simply maps to the `public` role."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return db.get(User, int(payload["sub"]))


def role_of(user: User | None) -> str:
    return user.role if user else "public"


def require_roles(*allowed: str):
    """Dependency factory: restricts an endpoint to the given roles (PS point 17)."""

    def _guard(user: User | None = Depends(current_user)) -> User:
        if role_of(user) not in allowed:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Requires role: {', '.join(allowed)} (you are '{role_of(user)}')",
            )
        return user

    return _guard
