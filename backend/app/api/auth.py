from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    TokenRefreshRequest, TokenRefreshResponse,
    MFASetupRequest, MFASetupResponse,
    MFAVerifyRequest, MFAVerifyResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
    LogoutRequest, LogoutResponse,
    VerifyOTPRequest, VerifyOTPResponse,
)
from app.schemas.user import UserProfileResponse, UserUpdate
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user, create_access_token
from app.middleware.audit import audit_logger
from app.models.user import User
from app.exceptions import BadRequestException
from app.utils import get_client_ip, get_user_agent, parse_device_fingerprint

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register")
async def register(
    request: Request,
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.middleware.auth import create_access_token, create_refresh_token
        service = AuthService(db)
        user = await service.register(req.email, req.phone, req.full_name, req.password)
        role_str = str(user.role.value if hasattr(user.role, "value") else user.role)
        access_token = create_access_token(user.id, role_str)
        refresh_token = create_refresh_token(user.id)
        await audit_logger(request, "user_registered", "user", str(user.id), {"email": req.email}, db, None)
        return {
            "success": True,
            "user_id": user.id,
            "data": {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.full_name,
                    "phone": user.phone,
                    "role": role_str.lower(),
                    "mfaEnabled": user.mfa_enabled,
                    "behavioralProfileStatus": "pending",
                    "trustedDevices": [],
                    "notificationPreferences": {
                        "email": True, "sms": True, "push": False,
                        "transactionAlerts": True, "loginAlerts": True,
                        "marketingEmails": False, "securityAlerts": True,
                    },
                    "createdAt": user.created_at.isoformat() if user.created_at else "",
                    "updatedAt": user.updated_at.isoformat() if user.updated_at else "",
                },
                "tokens": {
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                    "expiresIn": 3600,
                },
            },
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("Unhandled exception in register endpoint")
        # Include a brief error detail for debugging; remove in production.
        return JSONResponse(status_code=500, content={"success": False, "error": {"code": "internal_error", "message": "An internal error occurred", "details": str(e)}})


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    ip = get_client_ip(request)
    result = await service.login(
        email=req.email,
        password=req.password,
        ip_address=ip,
        device_fingerprint=req.device_fingerprint,
    )

    if result.get("mfa_required"):
        await audit_logger(request, "login_mfa_required", "user", None, {"email": req.email}, db, None)
        return LoginResponse(
            access_token="",
            refresh_token="",
            expires_in=0,
            mfa_required=True,
            mfa_method=result["mfa_method"],
            temp_token=result["temp_token"],
        )

    await audit_logger(request, "user_login", "user", None, {"email": req.email}, db, None)
    return LoginResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        expires_in=result["expires_in"],
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: Request,
    req: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.refresh_token(req.refresh_token)
    return TokenRefreshResponse(
        access_token=result["access_token"],
        expires_in=result["expires_in"],
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    req: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await audit_logger(request, "user_logout", "user", str(current_user.id), None, db, current_user)
    return LogoutResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: Request,
    req: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    message = await service.forgot_password(req.email)
    return ForgotPasswordResponse(message=message)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: Request,
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    message = await service.reset_password(req.reset_token, req.new_password)
    return ResetPasswordResponse(message=message)


@router.post("/setup-mfa", response_model=MFASetupResponse)
async def setup_mfa(
    request: Request,
    req: MFASetupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.setup_mfa(current_user, req.method)
    await audit_logger(request, "mfa_setup_initiated", "user", str(current_user.id),
                       {"method": req.method}, db, current_user)
    return MFASetupResponse(
        secret=result.get("secret"),
        qr_code=result.get("qr_code"),
        message=result.get("message", "MFA setup initiated"),
    )


@router.post("/enable-mfa", response_model=MFASetupResponse)
async def enable_mfa(
    request: Request,
    req: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    mfa_method = current_user.mfa_method.value if hasattr(current_user.mfa_method, "value") else (str(current_user.mfa_method) if current_user.mfa_method else "TOTP")
    success, message = await service.enable_mfa(current_user, mfa_method, req.otp_code)
    if not success:
        raise BadRequestException(message)
    await audit_logger(request, "mfa_enabled", "user", str(current_user.id), None, db, current_user)
    return MFASetupResponse(message=message)


@router.post("/disable-mfa", response_model=MFASetupResponse)
async def disable_mfa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    success, message = await service.disable_mfa(current_user)
    await audit_logger(request, "mfa_disabled", "user", str(current_user.id), None, db, current_user)
    return MFASetupResponse(message=message)


@router.post("/verify-mfa", response_model=MFAVerifyResponse)
async def verify_mfa(
    request: Request,
    req: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.verify_mfa(req.temp_token, req.otp_code)
    await audit_logger(request, "mfa_verified", "user", None, None, db, None)
    return MFAVerifyResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.put("/me", response_model=UserProfileResponse)
async def update_me(
    request: Request,
    req: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.update_profile(current_user, req.model_dump(exclude_unset=True))
    await audit_logger(request, "profile_updated", "user", str(user.id), None, db, current_user)
    return user


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(
    request: Request,
    req: VerifyOTPRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.middleware.auth import decode_temp_token
    try:
        user_id, mfa_method = decode_temp_token(req.temp_token)
        service = AuthService(db)
        if mfa_method == "TOTP":
            from app.models.user import User as UserModel
            result = await db.get(UserModel, user_id)
            if result and result.mfa_secret:
                import pyotp
                totp = pyotp.TOTP(result.mfa_secret)
                verified = totp.verify(req.otp, valid_window=1)
                return VerifyOTPResponse(verified=verified)
            return VerifyOTPResponse(verified=False)
        verified = await service._verify_otp_code(user_id, req.otp, mfa_method)
        return VerifyOTPResponse(verified=verified)
    except Exception:
        return VerifyOTPResponse(verified=False)
