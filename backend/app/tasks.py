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
                from app.models.behavioral import BehavioralProfile, BehavioralEvent, MlModel, RiskScore
                from sqlalchemy import desc, func
                import time

                result = await db.execute(
                    select(BehavioralProfile).where(BehavioralProfile.user_id == user_id)
                )
                profile = result.scalar_one_or_none()
                if not profile:
                    return {"success": False, "error": "No profile found"}

                # 1. Fetch recent sessions
                session_result = await db.execute(
                    select(BehavioralEvent.session_id)
                    .where(BehavioralEvent.user_id == user_id)
                    .group_by(BehavioralEvent.session_id)
                    .order_by(desc(func.max(BehavioralEvent.server_timestamp)))
                    .limit(100)
                )
                session_ids = [row[0] for row in session_result.fetchall()]
                
                if not session_ids:
                    return {"success": False, "error": "No events found"}
                    
                events_result = await db.execute(
                    select(BehavioralEvent)
                    .where(BehavioralEvent.session_id.in_(session_ids))
                    .order_by(BehavioralEvent.server_timestamp)
                )
                events = events_result.scalars().all()
                
                from collections import defaultdict
                session_batches = defaultdict(list)
                for e in events:
                    evt_dict = {
                        "session_id": e.session_id,
                        "type": e.event_type,
                        "timestamp": e.client_timestamp.timestamp() if e.client_timestamp else e.server_timestamp.timestamp(),
                    }
                    if e.event_data:
                        evt_dict.update(e.event_data)
                    session_batches[e.session_id].append(evt_dict)
                    
                event_batches = list(session_batches.values())
                
                risk_result = await db.execute(
                    select(RiskScore.session_id, RiskScore.final_score)
                    .where(RiskScore.session_id.in_(session_ids))
                )
                risk_map = {row[0]: row[1] for row in risk_result.fetchall()}
                session_risk_scores = [risk_map.get(sid, 0.0) for sid in session_batches.keys()]

                # Run ML training
                import asyncio
                import concurrent.futures
                from ml.training_pipeline import TrainingPipeline
                from ml.config import MLConfig
                
                start_time = time.time()
                def _train():
                    pipeline = TrainingPipeline(MLConfig())
                    return pipeline.train_for_user(
                        str(user_id), 
                        event_batches, 
                        session_risk_scores
                    )
                    
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    train_result = await loop.run_in_executor(pool, _train)
                    
                if not train_result.get("trained"):
                    return {"success": False, "reason": train_result.get("reason", "unknown")}

                model_version = str(train_result.get("version", "1"))
                metrics = {
                    "n_samples": train_result.get("n_samples", 0),
                    "threshold": train_result.get("threshold", 0.0),
                    "session_count": len(session_ids),
                }

                model = MlModel(
                    user_id=user_id,
                    model_type=train_result.get("model_type", "isolation_forest"),
                    model_version=model_version,
                    model_data=b"",
                    metrics=metrics,
                    is_active=True,
                    session_count=len(session_ids),
                    training_duration=round(time.time() - start_time, 2),
                )
                db.add(model)

                if profile:
                    profile.model_version = model_version
                    profile.last_trained_at = datetime.now(timezone.utc)
                    profile.session_count = len(session_ids)
                    if "feature_statistics" in train_result:
                        current_prof = profile.profile or {}
                        current_prof["feature_statistics"] = train_result["feature_statistics"]
                        profile.profile = current_prof

                await db.flush()
                return {"success": True, "user_id": user_id, "model_version": model_version}
            except Exception as e:
                import traceback
                traceback.print_exc()
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
                from app.models.behavioral import BehavioralEvent, BehavioralProfile, MlModel
                from sqlalchemy import desc, func
                import time
                
                result = await db.execute(
                    select(BehavioralProfile)
                )
                profiles = result.scalars().all()
                if not profiles:
                     return {"success": False, "error": "No users found"}
                     
                user_ids = [p.user_id for p in profiles]
                
                # Fetch recent events for all users (limit to max 500 sessions overall)
                session_result = await db.execute(
                    select(BehavioralEvent.session_id, BehavioralEvent.user_id)
                    .group_by(BehavioralEvent.session_id, BehavioralEvent.user_id)
                    .order_by(desc(func.max(BehavioralEvent.server_timestamp)))
                    .limit(500)
                )
                session_rows = session_result.fetchall()
                session_ids = [row[0] for row in session_rows]
                
                if not session_ids:
                    return {"success": False, "error": "No events found"}
                    
                events_result = await db.execute(
                    select(BehavioralEvent)
                    .where(BehavioralEvent.session_id.in_(session_ids))
                    .order_by(BehavioralEvent.server_timestamp)
                )
                events = events_result.scalars().all()
                
                from collections import defaultdict
                all_user_batches = defaultdict(list)
                session_evt_map = defaultdict(list)
                
                for e in events:
                    evt_dict = {
                        "session_id": e.session_id,
                        "type": e.event_type,
                        "timestamp": e.client_timestamp.timestamp() if e.client_timestamp else e.server_timestamp.timestamp(),
                    }
                    if e.event_data:
                        evt_dict.update(e.event_data)
                    session_evt_map[e.session_id].append(evt_dict)
                    
                # map back to users
                user_session_map = {row[0]: row[1] for row in session_rows}
                for sid, evts in session_evt_map.items():
                    uid = user_session_map.get(sid)
                    if uid:
                        all_user_batches[str(uid)].append(evts)
                
                import asyncio
                import concurrent.futures
                from ml.training_pipeline import TrainingPipeline
                from ml.config import MLConfig
                
                start_time = time.time()
                def _train_global():
                    pipeline = TrainingPipeline(MLConfig())
                    return pipeline.retrain_global_model(all_user_batches)
                    
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    train_result = await loop.run_in_executor(pool, _train_global)
                    
                if not train_result.get("trained"):
                    return {"success": False, "reason": train_result.get("reason", "unknown")}

                model_version = str(train_result.get("version", "1"))
                metrics = {
                    "n_samples": train_result.get("n_samples", 0),
                    "threshold": train_result.get("threshold", 0.0),
                    "user_count": len(all_user_batches),
                    "session_count": len(session_ids),
                }

                model = MlModel(
                    user_id=None,
                    model_type=train_result.get("model_type", "global_behavioral_ensemble"),
                    model_version=model_version,
                    model_data=b"",
                    metrics=metrics,
                    is_active=True,
                    session_count=len(session_ids),
                    training_duration=round(time.time() - start_time, 2),
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
                return {"success": True, "model_version": model_version, "users": len(all_user_batches)}
            except Exception as e:
                import traceback
                traceback.print_exc()
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
                from app.models.behavioral import BehavioralProfile, BehavioralFeature
                from sqlalchemy import desc
                from ml.drift_detection import DriftDetector
                from ml.config import MLConfig
                import json
                
                result = await db.execute(select(BehavioralProfile))
                profiles = result.scalars().all()
                
                detector = DriftDetector(MLConfig())
                drifted_count = 0
                
                for profile in profiles:
                    if profile.session_count and profile.session_count > 5:
                        feat_result = await db.execute(
                            select(BehavioralFeature.features)
                            .where(BehavioralFeature.user_id == profile.user_id)
                            .order_by(desc(BehavioralFeature.created_at))
                            .limit(1)
                        )
                        latest_feature = feat_result.scalar_one_or_none()
                        
                        if latest_feature and profile.profile and "feature_statistics" in profile.profile:
                            baseline_stats = profile.profile["feature_statistics"]
                            report = detector.get_user_drift_status(
                                str(profile.user_id), 
                                latest_feature, 
                                baseline_stats
                            )
                            if report.has_drifted:
                                profile.drift_status = "drifted"
                                drifted_count += 1
                            else:
                                profile.drift_status = "normal"

                await db.flush()
                return {
                    "success": True,
                    "profiles_checked": len(profiles),
                    "drifted_count": drifted_count,
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
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
