from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20)
    full_name: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=72)


class RegisterResponse(BaseModel):
    success: bool = True
    message: str
    user_id: int
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    expires_in: Optional[int] = 3600
    user: Optional[dict] = None


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=72)
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None


class LoginResponse(BaseModel):
    success: bool = True
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    mfa_required: bool = False
    mfa_method: Optional[str] = None
    temp_token: Optional[str] = None
    risk_assessment: Optional[dict] = None


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    success: bool = True
    access_token: str
    expires_in: int


class MFASetupRequest(BaseModel):
    method: str = Field(..., pattern="^(TOTP|SMS|EMAIL)$")


class MFASetupResponse(BaseModel):
    success: bool = True
    secret: Optional[str] = None
    qr_code: Optional[str] = None
    message: str


class MFAVerifyRequest(BaseModel):
    temp_token: str
    otp_code: str


class MFAVerifyResponse(BaseModel):
    success: bool = True
    access_token: str
    refresh_token: str


class OTPVerifyRequest(BaseModel):
    temp_token: str
    otp_code: str


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=255)


class ForgotPasswordResponse(BaseModel):
    success: bool = True
    message: str
    reset_token: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8, max_length=72)


class ResetPasswordResponse(BaseModel):
    success: bool = True
    message: str


class LogoutRequest(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    success: bool = True
    message: str


class VerifyOTPRequest(BaseModel):
    temp_token: str
    otp: str


class VerifyOTPResponse(BaseModel):
    success: bool = True
    verified: bool
