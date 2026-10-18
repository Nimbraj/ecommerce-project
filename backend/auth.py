from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import pyotp
import re

from database import get_db
from models import User, UserRole
from schemas import TokenData

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be configured before using authentication")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in (UserRole.ADMIN.value, UserRole.MANAGER.value) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_current_manager_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in (UserRole.ADMIN.value, UserRole.MANAGER.value) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Admin access required"
        )
    return current_user


# ============== 2FA TOTP HELPERS ==============

def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "JN ECOMMERCE") -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def verify_totp(secret: str, token: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(token)


# ============== PASSWORD STRENGTH ==============

def check_password_strength(password: str) -> dict:
    """Returns dict with valid flag and message."""
    if len(password) < 8:
        return {"valid": False, "message": "Password must be at least 8 characters long"}
    if not re.search(r"[A-Z]", password):
        return {"valid": False, "message": "Password must contain at least one uppercase letter"}
    if not re.search(r"[a-z]", password):
        return {"valid": False, "message": "Password must contain at least one lowercase letter"}
    if not re.search(r"\d", password):
        return {"valid": False, "message": "Password must contain at least one digit"}
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return {"valid": False, "message": "Password must contain at least one special character"}
    return {"valid": True, "message": "Password is strong"}

