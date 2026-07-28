from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
import bcrypt
from datetime import datetime, timezone, timedelta
from typing import Optional
import pyotp
import base64
import io

from app.models.user import User, UserRole, UserStatus, MFAMethod
from app.middleware.auth import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    create_temp_token,
    decode_temp_token,
)
from app.config import settings
from app.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ConflictException,
    NotFoundException,
    ForbiddenException,
    MFARequiredException,
)
from app.utils import (
    validate_password_strength,
    validate_email,
    validate_phone,
    get_client_ip,
    get_user_agent,
    hash_device_fingerprint,
)


def hash_password(password: str) -> str:
    pw_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        pw_bytes = password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, phone: str, full_name: str, password: str) -> User:
        if not validate_email(email):
            raise BadRequestException("Invalid email format")

        cleaned_phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not validate_phone(cleaned_phone):
            raise BadRequestException("Invalid phone number format")

        valid, msg = validate_password_strength(password)
        if not valid:
            raise BadRequestException(msg)

        existing = await self.db.execute(
            select(User).where(or_(User.email == email, User.phone == cleaned_phone))
        )
        if existing.scalar_one_or_none():
            raise ConflictException("User with this email or phone already exists")

        password_hash = hash_password(password)
        user = User(
            email=email,
            phone=cleaned_phone,
            password_hash=password_hash,
            full_name=full_name,
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
            device_fingerprints=[],
            trusted_devices=[],
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def login(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
    ) -> dict:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedException("Invalid email or password")

        if user.status == UserStatus.LOCKED:
            if user.locked_until and user.locked_until > datetime.now(timezone.utc):
                remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds())
                raise ForbiddenException(f"Account locked. Try again in {remaining} seconds")
            else:
                user.failed_login_attempts = 0
                user.locked_until = None

        if user.status == UserStatus.SUSPENDED:
            raise ForbiddenException("Account is suspended")

        if not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.status = UserStatus.LOCKED
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            await self.db.flush()
            remaining_attempts = 5 - user.failed_login_attempts
            raise UnauthorizedException(f"Invalid credentials. {remaining_attempts} attempts remaining")

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        user.last_login_ip = ip_address

        if device_fingerprint:
            fp_hash = hash_device_fingerprint(device_fingerprint)
            fingerprints = user.device_fingerprints or []
            if fp_hash not in fingerprints:
                fingerprints.append(fp_hash)
                user.device_fingerprints = fingerprints

        await self.db.flush()

        if user.mfa_enabled and user.mfa_method:
            temp_token = create_temp_token(user.id, user.mfa_method.value)
            return {
                "mfa_required": True,
                "mfa_method": user.mfa_method.value,
                "temp_token": temp_token,
            }

        access_token = create_access_token(user.id, user.role.value)
        refresh_token = create_refresh_token(user.id)

        return {
            "mfa_required": False,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def verify_mfa(self, temp_token: str, otp_code: str) -> dict:
        user_id, mfa_method = decode_temp_token(temp_token)

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedException("User not found")
        if not user.mfa_enabled:
            raise BadRequestException("MFA is not enabled for this user")

        valid = False
        if mfa_method == "TOTP":
            if not user.mfa_secret:
                raise BadRequestException("TOTP not configured")
            totp = pyotp.TOTP(user.mfa_secret)
            valid = totp.verify(otp_code, valid_window=settings.MFA_TOTP_VALIDITY_WINDOW)
        elif mfa_method == "SMS" or mfa_method == "EMAIL":
            valid = await self._verify_otp_code(user.id, otp_code, mfa_method)

        if not valid:
            raise UnauthorizedException("Invalid OTP code")

        access_token = create_access_token(user.id, user.role.value)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        user_id = decode_refresh_token(refresh_token)
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedException("User not found")
        if user.status in (UserStatus.SUSPENDED, UserStatus.LOCKED):
            raise ForbiddenException("Account is not active")

        access_token = create_access_token(user.id, user.role.value)
        return {
            "access_token": access_token,
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def forgot_password(self, email: str) -> str:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return "If the email exists, a reset link has been sent"

        reset_token = generate_reset_token()
        user.reset_token = hash_password(reset_token)
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await self.db.flush()

        return "If the email exists, a reset link has been sent"

    async def reset_password(self, reset_token: str, new_password: str) -> str:
        valid, msg = validate_password_strength(new_password)
        if not valid:
            raise BadRequestException(msg)

        result = await self.db.execute(
            select(User).where(
                User.reset_token_expires > datetime.now(timezone.utc)
            )
        )
        users = result.scalars().all()

        user = None
        for u in users:
            if u.reset_token and verify_password(reset_token, u.reset_token):
                user = u
                break

        if not user:
            raise BadRequestException("Invalid or expired reset token")

        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.db.flush()

        return "Password reset successfully"

    async def setup_mfa(self, user: User, method: str) -> dict:
        if method == "TOTP":
            secret = pyotp.random_base32()
            user.mfa_temp_secret = secret
            await self.db.flush()

            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user.email,
                issuer_name=settings.MFA_ISSUER_NAME,
            )

            return {
                "secret": secret,
                "qr_code": totp_uri,
                "message": "Scan QR code with authenticator app, then verify with enable-mfa",
            }
        elif method == "SMS":
            user.mfa_temp_secret = "sms_pending"
            await self.db.flush()
            return {
                "message": "SMS OTP will be sent to registered phone. Verify with enable-mfa.",
            }
        elif method == "EMAIL":
            user.mfa_temp_secret = "email_pending"
            await self.db.flush()
            return {
                "message": "Email OTP will be sent to registered email. Verify with enable-mfa.",
            }
        else:
            raise BadRequestException("Invalid MFA method")

    async def enable_mfa(self, user: User, method: str, otp_code: str) -> tuple[bool, str]:
        if method == "TOTP":
            if not user.mfa_temp_secret or user.mfa_temp_secret in ("sms_pending", "email_pending"):
                return False, "TOTP not initialized"
            totp = pyotp.TOTP(user.mfa_temp_secret)
            if not totp.verify(otp_code, valid_window=settings.MFA_TOTP_VALIDITY_WINDOW):
                return False, "Invalid OTP"
            user.mfa_secret = user.mfa_temp_secret
        else:
            valid = await self._verify_otp_code(user.id, otp_code, method)
            if not valid:
                return False, "Invalid OTP"
            user.mfa_secret = "enabled"

        user.mfa_enabled = True
        user.mfa_method = MFAMethod(method)
        user.mfa_temp_secret = None
        await self.db.flush()
        return True, "MFA enabled successfully"

    async def disable_mfa(self, user: User) -> tuple[bool, str]:
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_method = None
        user.mfa_temp_secret = None
        await self.db.flush()
        return True, "MFA disabled successfully"

    async def update_profile(self, user: User, update_data: dict) -> User:
        email = update_data.get("email")
        phone = update_data.get("phone")
        full_name = update_data.get("full_name")

        if email and email != user.email:
            if not validate_email(email):
                raise BadRequestException("Invalid email format")
            existing = await self.db.execute(select(User).where(User.email == email))
            if existing.scalar_one_or_none():
                raise ConflictException("Email already in use")
            user.email = email

        if phone and phone != user.phone:
            cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not validate_phone(cleaned):
                raise BadRequestException("Invalid phone number")
            existing = await self.db.execute(select(User).where(User.phone == cleaned))
            if existing.scalar_one_or_none():
                raise ConflictException("Phone already in use")
            user.phone = cleaned

        if full_name:
            user.full_name = full_name

        user.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def _verify_otp_code(self, user_id: int, otp_code: str, method: str) -> bool:
        from app.models.behavioral import AuditLog
        result = await self.db.execute(
            select(AuditLog).where(
                AuditLog.user_id == user_id,
                AuditLog.action == f"send_{method.lower()}_otp",
                AuditLog.created_at > datetime.now(timezone.utc) - timedelta(minutes=5),
            ).order_by(AuditLog.created_at.desc()).limit(1)
        )
        log = result.scalar_one_or_none()
        if not log:
            return False
        stored_otp = log.details.get("otp_code") if log.details else None
        return stored_otp == otp_code
