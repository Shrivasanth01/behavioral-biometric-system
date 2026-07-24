from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.config import settings
from app.exceptions import UnauthorizedException, ForbiddenException, MFARequiredException

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedException("Authentication required")

    token = credentials.credentials
    if not token:
        raise UnauthorizedException("Invalid token format")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
            issuer=settings.JWT_ISSUER,
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Invalid token payload")
    except JWTError as e:
        raise UnauthorizedException(f"Invalid or expired token: {str(e)}")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException("User not found")
    if user.status in (UserStatus.SUSPENDED, UserStatus.LOCKED):
        raise ForbiddenException(f"Account is {user.status.value.lower()}")

    return user


def require_role(*roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise ForbiddenException("Insufficient permissions")
        return current_user
    return role_checker


require_admin = require_role(UserRole.ADMIN)
require_analyst = require_role(UserRole.ANALYST, UserRole.ADMIN)


async def optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if credentials is None:
        return None
    try:
        return await get_current_user(request, credentials, db)
    except Exception:
        return None


def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now.timestamp() + settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    payload = {
        "sub": user_id,
        "role": role,
        "iat": now.timestamp(),
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    expire = now.timestamp() + settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
    payload = {
        "sub": user_id,
        "iat": now.timestamp(),
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_refresh_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
        )
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")
        return payload.get("sub")
    except JWTError:
        raise UnauthorizedException("Invalid refresh token")


def create_temp_token(user_id: int, mfa_method: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now.timestamp() + 300
    payload = {
        "sub": user_id,
        "mfa_method": mfa_method,
        "iat": now.timestamp(),
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "type": "mfa_temp",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_temp_token(token: str) -> tuple[int, str]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
        )
        if payload.get("type") != "mfa_temp":
            raise UnauthorizedException("Invalid temp token")
        return payload.get("sub"), payload.get("mfa_method")
    except JWTError:
        raise UnauthorizedException("Invalid or expired temp token")
