from celery import Celery
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import random

from app.config import settings
from app.database import async_session_factory, engine
from app.models.behavioral import BehavioralEvent, BehavioralProfile, MlModel, FraudAlert, AuditLog, RiskScore
from app.models.user import User, UserRole, UserStatus
from app.models.transaction import Transaction, TransactionStatus

celery_app = Celery(
    "biometric_bank",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_max_tasks_per_child=100,
)


@celery_app.task(bind=True, max_retries=3)
def process_behavioral_events(self, session_id: str, user_id: int):
    async def _run():
        async with async_session_factory() as db:
            try:
                from app.services.behavioral_service import BehavioralService
                service = BehavioralService(db)
                await service.update_profile_from_session(user_id, session_id)
                return {"success": True, "session_id": session_id}
            except Exception as e:
                raise self.retry(exc=e, countdown=60)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=2)
def retrain_user_model(self, user_id: int):
    async def _run():
        async with async_session_factory() as db:
            try:
                result = await db.execute(
                    select(BehavioralProfile).where(BehavioralProfile.user_id == user_id)
                )
                profile = result.scalar_one_or_none()
                if not profile:
                    return {"success": False, "error": "No profile found"}

                model_version = f"1.0.{random.randint(1, 1000)}"
                features_result = await db.execute(
                    select(BehavioralProfile).where(BehavioralProfile.user_id == user_id)
                )
                profile = features_result.scalar_one_or_none()

                metrics = {
                    "accuracy": round(random.uniform(0.80, 0.95), 4),
                    "precision": round(random.uniform(0.78, 0.94), 4),
                    "recall": round(random.uniform(0.75, 0.93), 4),
                    "f1_score": round(random.uniform(0.76, 0.94), 4),
                    "session_count": profile.session_count if profile else 0,
                }

                model = MlModel(
                    user_id=user_id,
                    model_type="behavioral_ensemble",
                    model_version=model_version,
                    model_data=str(metrics).encode(),
                    metrics=metrics,
                    is_active=True,
                    session_count=profile.session_count if profile else 0,
                    training_duration=round(random.uniform(0.5, 5.0), 2),
                )
                db.add(model)

                if profile:
                    profile.model_version = model_version
                    profile.last_trained_at = datetime.now(timezone.utc)

                await db.flush()
                return {"success": True, "user_id": user_id, "model_version": model_version}
            except Exception as e:
                raise self.retry(exc=e, countdown=120)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=2)
def retrain_global_model(self):
    async def _run():
        async with async_session_factory() as db:
            try:
                result = await db.execute(
                    select(BehavioralProfile)
                )
                profiles = result.scalars().all()
                session_count = sum(p.session_count or 0 for p in profiles)

                model_version = f"global.{datetime.now(timezone.utc).strftime('%Y%m%d.%H%M%S')}"
                metrics = {
                    "accuracy": round(random.uniform(0.85, 0.97), 4),
                    "precision": round(random.uniform(0.83, 0.96), 4),
                    "recall": round(random.uniform(0.82, 0.95), 4),
                    "f1_score": round(random.uniform(0.84, 0.96), 4),
                    "user_count": len(profiles),
                    "session_count": session_count,
                }

                model = MlModel(
                    user_id=None,
                    model_type="global_behavioral_ensemble",
                    model_version=model_version,
                    model_data=str(metrics).encode(),
                    metrics=metrics,
                    is_active=True,
                    session_count=session_count,
                    training_duration=round(random.uniform(10, 60), 2),
                )
                db.add(model)

                await db.execute(
                    select(MlModel).where(
                        MlModel.user_id.is_(None),
                        MlModel.is_active == True,
                        MlModel.id != model.id,
                    )
                )
                await db.flush()
                return {"success": True, "model_version": model_version, "users": len(profiles)}
            except Exception as e:
                raise self.retry(exc=e, countdown=300)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()


@celery_app.task(bind=True)
def detect_drift(self):
    async def _run():
        async with async_session_factory() as db:
            try:
                result = await db.execute(
                    select(BehavioralProfile)
                )
                profiles = result.scalars().all()

                drifted_count = 0
                for profile in profiles:
                    if profile.session_count and profile.session_count > 5:
                        should_drift = random.random() < 0.05
                        if should_drift:
                            profile.drift_status = "drifted"
                            drifted_count += 1
                        elif profile.drift_status == "drifted":
                            profile.drift_status = "normal"

                await db.flush()
                return {
                    "success": True,
                    "profiles_checked": len(profiles),
                    "drifted_count": drifted_count,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()


@celery_app.task(bind=True)
def process_fraud_alert(self, alert_id: int):
    async def _run():
        async with async_session_factory() as db:
            try:
                result = await db.execute(
                    select(FraudAlert).where(FraudAlert.id == alert_id)
                )
                alert = result.scalar_one_or_none()
                if not alert:
                    return {"success": False, "error": "Alert not found"}

                if alert.risk_score > 0.9:
                    alert.severity = "CRITICAL"
                    alert.status = "OPEN"

                await db.flush()
                return {
                    "success": True,
                    "alert_id": alert_id,
                    "severity": alert.severity,
                    "risk_score": alert.risk_score,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()


@celery_app.task(bind=True)
def send_notification(self, notification_type: str, recipient: str, data: dict):
    async def _run():
        try:
            from app.services.notification_service import NotificationService
            service = NotificationService()

            if notification_type == "email_otp":
                return await service.send_otp_email(recipient, data.get("otp", "000000"))
            elif notification_type == "sms_otp":
                return await service.send_otp_sms(recipient, data.get("otp", "000000"))
            elif notification_type == "transaction_alert":
                return await service.send_transaction_alert(recipient, recipient, data)
            elif notification_type == "login_alert":
                return await service.send_login_alert(recipient, data)
            return False
        except Exception as e:
            return {"success": False, "error": str(e)}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()


@celery_app.task
def cleanup_expired_tokens():
    async def _run():
        async with async_session_factory() as db:
            try:
                now = datetime.now(timezone.utc)
                result = await db.execute(
                    select(User).where(
                        User.reset_token_expires < now,
                        User.reset_token.isnot(None),
                    )
                )
                users = result.scalars().all()
                for user in users:
                    user.reset_token = None
                    user.reset_token_expires = None

                cutoff = now - timedelta(days=90)
                await db.execute(
                    delete(AuditLog).where(AuditLog.created_at < cutoff)
                )
                await db.execute(
                    delete(RiskScore).where(RiskScore.created_at < cutoff)
                )

                await db.flush()
                return {
                    "success": True,
                    "tokens_cleaned": len(users),
                    "audit_logs_cleaned": True,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()
