from typing import Optional

from passlib.context import CryptContext

from . import database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password for storage."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check whether a password matches its stored hash."""
    try:
        return pwd_context.verify(password, password_hash)
    except ValueError:
        return False


def authenticate(username: str, password: str) -> Optional[dict]:
    """Validate credentials and return the user object on success."""
    user = database.get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user
