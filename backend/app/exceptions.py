from fastapi import HTTPException, status
import logging
import traceback


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code or "error"


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, code="not_found")


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, code="unauthorized")


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code="forbidden")


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code="bad_request")


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, code="conflict")


class RateLimitException(AppException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail, code="rate_limit")


class MFARequiredException(AppException):
    def __init__(self, temp_token: str, mfa_method: str, detail: str = "MFA verification required"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, code="mfa_required")
        self.temp_token = temp_token
        self.mfa_method = mfa_method


class AccountFrozenException(AppException):
    def __init__(self, detail: str = "Account is frozen"):
        super().__init__(status_code=status.HTTP_423_LOCKED, detail=detail, code="account_frozen")


class InsufficientBalanceException(AppException):
    def __init__(self, detail: str = "Insufficient balance"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code="insufficient_balance")


class DailyLimitExceededException(AppException):
    def __init__(self, detail: str = "Daily transaction limit exceeded"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code="daily_limit_exceeded")


class TransactionBlockedException(AppException):
    def __init__(self, detail: str = "Transaction blocked by risk engine", risk_score: float = 0.0):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code="transaction_blocked")
        self.risk_score = risk_score


def register_exception_handlers(app):
    from fastapi import Request
    from fastapi.responses import JSONResponse

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.detail,
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Log full traceback to logger and a debug file for local inspection
        logging.exception("Unhandled exception during request processing")
        try:
            tb = traceback.format_exc()
            with open(r"c:\\Users\\shriv\\Documents\\behavioral-biometric-system\\backend\\error_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[{request.method} {request.url}]\n")
                f.write(tb + "\n\n")
        except Exception:
            pass
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "internal_error",
                    "message": "An internal error occurred",
                },
            },
        )
