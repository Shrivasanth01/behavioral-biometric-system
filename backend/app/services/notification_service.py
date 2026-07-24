from typing import Optional
import random
import string

from app.config import settings


class NotificationService:
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        try:
            import httpx
            if settings.ENVIRONMENT == "production":
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.email-service.com/send",
                        json={
                            "to": to,
                            "subject": subject,
                            "body": body,
                        },
                        timeout=10,
                    )
                    return response.status_code == 200
            else:
                print(f"[EMAIL] To: {to}, Subject: {subject}")
                return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False

    async def send_sms(self, to: str, message: str) -> bool:
        try:
            import httpx
            if settings.ENVIRONMENT == "production":
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.sms-service.com/send",
                        json={
                            "to": to,
                            "message": message,
                        },
                        timeout=10,
                    )
                    return response.status_code == 200
            else:
                print(f"[SMS] To: {to}, Message: {message}")
                return True
        except Exception as e:
            print(f"SMS send failed: {e}")
            return False

    async def send_otp_email(self, email: str, otp: str) -> bool:
        subject = f"{settings.MFA_ISSUER_NAME}: Your OTP Code"
        body = f"""
        Your OTP code is: {otp}

        This code expires in 5 minutes.
        If you did not request this, please ignore this email.

        - {settings.MFA_ISSUER_NAME} Security Team
        """
        return await self.send_email(email, subject, body)

    async def send_otp_sms(self, phone: str, otp: str) -> bool:
        message = f"Your {settings.MFA_ISSUER_NAME} OTP is: {otp}. Valid for 5 minutes."
        return await self.send_sms(phone, message)

    async def send_transaction_alert(self, email: str, phone: str, details: dict) -> bool:
        subject = f"{settings.MFA_ISSUER_NAME}: Transaction Alert"
        body = f"""
        Transaction Alert

        Amount: ₹{details.get('amount', 0):,.2f}
        Type: {details.get('type', 'N/A')}
        Reference: {details.get('reference', 'N/A')}
        Status: {details.get('status', 'N/A')}
        Time: {details.get('time', 'N/A')}

        If you did not perform this transaction, please contact support immediately.
        """
        return await self.send_email(email, subject, body)

    async def send_login_alert(self, email: str, device_info: dict) -> bool:
        subject = f"{settings.MFA_ISSUER_NAME}: New Login Detected"
        body = f"""
        A new login was detected on your account.

        Device: {device_info.get('device', 'Unknown')}
        IP Address: {device_info.get('ip', 'Unknown')}
        Time: {device_info.get('time', 'Unknown')}

        If this was you, no action is needed.
        If you did not login, please secure your account immediately.
        """
        return await self.send_email(email, subject, body)

    def generate_otp(self, length: int = 6) -> str:
        return "".join(random.choices(string.digits, k=length))
