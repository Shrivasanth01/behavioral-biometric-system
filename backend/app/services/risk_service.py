from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, or_
from datetime import datetime, timezone, timedelta
from typing import Optional
import random
import math

from app.models.user import User, UserStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.behavioral import (
    BehavioralEvent,
    BehavioralProfile,
    FraudAlert,
    RiskScore,
    ExplainabilityResult,
    SeverityLevel,
    AlertStatus,
    MlModel,
)
from app.config import settings
from app.exceptions import NotFoundException, BadRequestException


class RiskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def assess_risk(
        self,
        user_id: int,
        session_id: Optional[str] = None,
        transaction_id: Optional[int] = None,
        transaction_amount: Optional[float] = None,
        transaction_type: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        ml_score = await self._ml_risk_score(user_id, session_id)
        rules_score = await self._rules_risk_score(
            user_id, transaction_amount, transaction_type, ip_address
        )
        heuristic_score = await self._heuristic_risk_score(
            user_id, transaction_amount, session_id
        )

        weights = {"ml": 0.65, "rules": 0.25, "heuristic": 0.10}
        final_score = (
            ml_score * weights["ml"]
            + rules_score * weights["rules"]
            + heuristic_score * weights["heuristic"]
        )

        if final_score > settings.RISK_HIGH_RISK_THRESHOLD:
            risk_band = "CRITICAL" if final_score > 0.85 else "HIGH"
        elif final_score > settings.RISK_MEDIUM_RISK_THRESHOLD:
            risk_band = "MEDIUM"
        else:
            risk_band = "LOW"

        features_contribution = {
            "ml_score": round(ml_score, 4),
            "rules_score": round(rules_score, 4),
            "heuristic_score": round(heuristic_score, 4),
            "ml_weight": weights["ml"],
            "rules_weight": weights["rules"],
            "heuristic_weight": weights["heuristic"],
        }

        risk_record = RiskScore(
            session_id=session_id,
            transaction_id=transaction_id,
            user_id=user_id,
            ml_score=ml_score,
            rules_score=rules_score,
            heuristic_score=heuristic_score,
            final_score=final_score,
            risk_band=risk_band,
            features_contribution=features_contribution,
        )
        self.db.add(risk_record)
        await self.db.flush()

        reasons = await self._generate_reasons(
            ml_score, rules_score, heuristic_score, final_score, risk_band,
            transaction_amount, transaction_type,
        )

        explainability = ExplainabilityResult(
            risk_score_id=risk_record.id,
            reasons=reasons,
            feature_contributions=features_contribution,
        )
        self.db.add(explainability)

        should_block = final_score > settings.RISK_HIGH_RISK_THRESHOLD + 0.1 or risk_band == "CRITICAL"
        requires_mfa = final_score > settings.RISK_HIGH_RISK_THRESHOLD
        requires_approval = risk_band == "HIGH"

        if should_block and transaction_id:
            txn_result = await self.db.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            txn = txn_result.scalar_one_or_none()
            if txn:
                txn.status = TransactionStatus.BLOCKED
                txn.risk_score = final_score
                txn.risk_band = risk_band

        if risk_band in ("HIGH", "CRITICAL"):
            await self._create_alert(
                user_id=user_id,
                session_id=session_id,
                transaction_id=transaction_id,
                alert_type="high_risk_transaction" if transaction_id else "high_risk_session",
                severity=SeverityLevel.CRITICAL if risk_band == "CRITICAL" else SeverityLevel.HIGH,
                risk_score=final_score,
                details={
                    "reasons": reasons,
                    "features": features_contribution,
                    "transaction_amount": transaction_amount,
                    "transaction_type": transaction_type,
                },
            )

        await self.db.flush()

        return {
            "session_id": session_id,
            "risk_score": round(final_score, 4),
            "risk_band": risk_band,
            "should_block": should_block,
            "requires_mfa": requires_mfa,
            "requires_approval": requires_approval,
            "reasons": reasons,
            "ml_score": round(ml_score, 4),
            "rules_score": round(rules_score, 4),
            "heuristic_score": round(heuristic_score, 4),
        }

    async def get_risk_score(self, session_id: str) -> RiskScore:
        result = await self.db.execute(
            select(RiskScore)
            .where(RiskScore.session_id == session_id)
            .order_by(desc(RiskScore.created_at))
            .limit(1)
        )
        score = result.scalar_one_or_none()
        if not score:
            raise NotFoundException("No risk score found for this session")
        return score

    async def get_explainability(self, session_id: str) -> ExplainabilityResult:
        risk_score = await self.get_risk_score(session_id)
        result = await self.db.execute(
            select(ExplainabilityResult)
            .where(ExplainabilityResult.risk_score_id == risk_score.id)
            .order_by(desc(ExplainabilityResult.created_at))
            .limit(1)
        )
        explanation = result.scalar_one_or_none()
        if not explanation:
            raise NotFoundException("No explainability data found")
        return explanation

    async def get_alerts(
        self,
        status: Optional[AlertStatus] = None,
        severity: Optional[SeverityLevel] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[FraudAlert], int]:
        query = select(FraudAlert)

        if status:
            query = query.where(FraudAlert.status == status)
        if severity:
            query = query.where(FraudAlert.severity == severity)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(desc(FraudAlert.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_alert(self, alert_id: int) -> FraudAlert:
        result = await self.db.execute(
            select(FraudAlert).where(FraudAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise NotFoundException("Alert not found")
        return alert

    async def update_alert_status(
        self,
        alert_id: int,
        status: AlertStatus,
        assigned_to: Optional[int] = None,
        resolved_by: Optional[int] = None,
    ) -> FraudAlert:
        alert = await self.get_alert(alert_id)
        alert.status = status
        if assigned_to:
            alert.assigned_to = assigned_to
        if resolved_by and status in (AlertStatus.RESOLVED, AlertStatus.DISMISSED):
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert

    async def get_dashboard_summary(self) -> dict:
        now = datetime.now(timezone.utc)

        user_count = await self.db.execute(select(func.count(User.id)))
        total_users = user_count.scalar() or 0

        active_users_result = await self.db.execute(
            select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
        )
        active_users = active_users_result.scalar() or 0

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        txn_count = await self.db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.created_at >= today_start
            )
        )
        total_txns = txn_count.scalar() or 0

        blocked_count = await self.db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.created_at >= today_start,
                Transaction.status == TransactionStatus.BLOCKED,
            )
        )
        blocked_txns = blocked_count.scalar() or 0

        open_alerts_count = await self.db.execute(
            select(func.count(FraudAlert.id)).where(
                FraudAlert.status == AlertStatus.OPEN
            )
        )
        open_alerts = open_alerts_count.scalar() or 0

        critical_alerts_count = await self.db.execute(
            select(func.count(FraudAlert.id)).where(
                FraudAlert.status == AlertStatus.OPEN,
                FraudAlert.severity == SeverityLevel.CRITICAL,
            )
        )
        critical = critical_alerts_count.scalar() or 0

        avg_risk = await self.db.execute(
            select(func.avg(RiskScore.final_score)).where(
                RiskScore.created_at >= today_start
            )
        )
        avg_risk_score = float(avg_risk.scalar() or 0.0)

        high_risk_sessions = await self.db.execute(
            select(func.count(RiskScore.id)).where(
                RiskScore.created_at >= today_start,
                RiskScore.risk_band.in_(["HIGH", "CRITICAL"]),
            )
        )
        high_sessions = high_risk_sessions.scalar() or 0

        fraud_saved_result = await self.db.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.created_at >= today_start,
                Transaction.status == TransactionStatus.BLOCKED,
            )
        )
        total_fraud_saved = float(fraud_saved_result.scalar() or 0.0)
        
        models_result = await self.db.execute(
            select(MlModel.metrics).where(MlModel.is_active == True)
        )
        metrics_list = models_result.scalars().all()
        accuracies = [m.get("accuracy", 0.90) for m in metrics_list if isinstance(m, dict)]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.90

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_transactions": total_txns,
            "blocked_transactions": blocked_txns,
            "open_alerts": open_alerts,
            "critical_alerts": critical,
            "high_risk_sessions": high_sessions,
            "avg_risk_score": round(avg_risk_score, 4),
            "total_fraud_saved": round(total_fraud_saved, 2),
            "model_accuracy": round(avg_accuracy, 4),
        }

    async def get_risk_trends(self, days: int = 7) -> list[dict]:
        trends = []
        for i in range(days - 1, -1, -1):
            day_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)

            txn_count = await self.db.execute(
                select(func.count(Transaction.id)).where(
                    Transaction.created_at.between(day_start, day_end)
                )
            )
            txns = txn_count.scalar() or 0

            alert_count = await self.db.execute(
                select(func.count(FraudAlert.id)).where(
                    FraudAlert.created_at.between(day_start, day_end)
                )
            )
            alerts = alert_count.scalar() or 0

            blocked_count = await self.db.execute(
                select(func.count(Transaction.id)).where(
                    Transaction.created_at.between(day_start, day_end),
                    Transaction.status == TransactionStatus.BLOCKED,
                )
            )
            blocked = blocked_count.scalar() or 0

            avg_result = await self.db.execute(
                select(func.avg(RiskScore.final_score)).where(
                    RiskScore.created_at.between(day_start, day_end)
                )
            )
            avg_score = float(avg_result.scalar() or 0.0)

            trends.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "avg_risk_score": round(avg_score, 4),
                "transaction_count": txns,
                "alert_count": alerts,
                "blocked_count": blocked,
            })

        return trends

    async def get_risk_distribution(self) -> dict:
        result = await self.db.execute(
            select(
                RiskScore.risk_band,
                func.count(RiskScore.id),
            ).group_by(RiskScore.risk_band)
        )
        rows = result.fetchall()

        distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0, "total": 0}
        for row in rows:
            band = row[0] if row[0] in distribution else "LOW"
            distribution[band] = row[1]
            distribution["total"] += row[1]

        return distribution

    async def _ml_risk_score(self, user_id: int, session_id: Optional[str] = None) -> float:
        if not session_id:
            return 0.5
            
        result = await self.db.execute(
            select(BehavioralEvent)
            .where(BehavioralEvent.session_id == session_id)
            .order_by(BehavioralEvent.server_timestamp)
        )
        events = result.scalars().all()
        
        if not events:
            return 0.5
            
        event_dicts = []
        for e in events:
            evt_dict = {
                "session_id": e.session_id,
                "type": e.event_type,
                "timestamp": e.client_timestamp.timestamp() if e.client_timestamp else e.server_timestamp.timestamp(),
            }
            if e.event_data:
                evt_dict.update(e.event_data)
            event_dicts.append(evt_dict)
            
        import asyncio
        import concurrent.futures
        from ml.inference_pipeline import InferencePipeline
        from ml.config import MLConfig
        
        def _run_inference():
            pipeline = InferencePipeline(MLConfig())
            return pipeline.score(str(user_id), event_dicts)
            
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            score_result = await loop.run_in_executor(pool, _run_inference)
            
        ml_score_0_100 = score_result.get("ml_score", 50.0)
        return ml_score_0_100 / 100.0

    async def _rules_risk_score(
        self,
        user_id: int,
        transaction_amount: Optional[float] = None,
        transaction_type: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> float:
        score = 0.0

        if transaction_amount and transaction_amount > settings.RISK_MAX_SINGLE_TRANSACTION:
            score += 0.3

        if transaction_amount and transaction_amount > settings.RISK_MAX_DAILY_TRANSACTION:
            score += 0.2

        if transaction_type == "UPI":
            score += 0.05

        recent_txns = await self.db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.from_account_id.in_(
                    select(User.id).where(User.id == user_id)
                ),
                Transaction.created_at >= datetime.now(timezone.utc) - timedelta(
                    minutes=settings.RISK_VELOCITY_CHECK_MINUTES
                ),
            )
        )
        recent_count = recent_txns.scalar() or 0
        if recent_count > settings.RISK_VELOCITY_CHECK_COUNT:
            score += 0.2

        return min(score, 1.0)

    async def _heuristic_risk_score(
        self,
        user_id: int,
        transaction_amount: Optional[float] = None,
        session_id: Optional[str] = None,
    ) -> float:
        score = 0.0

        profile_result = await self.db.execute(
            select(BehavioralProfile).where(BehavioralProfile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()

        if profile and profile.drift_status == "drifted":
            score += 0.2

        if session_id:
            events_result = await self.db.execute(
                select(func.count(BehavioralEvent.id)).where(
                    BehavioralEvent.session_id == session_id
                )
            )
            event_count = events_result.scalar() or 0
            if event_count < 3:
                score += 0.15

        hourly_result = await self.db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.from_account_id.in_(
                    select(User.id).where(User.id == user_id)
                ),
                Transaction.created_at >= datetime.now(timezone.utc) - timedelta(hours=1),
            )
        )
        hourly_count = hourly_result.scalar() or 0
        if hourly_count > 10:
            score += 0.15

        return min(score, 1.0)

    async def _generate_reasons(
        self,
        ml_score: float,
        rules_score: float,
        heuristic_score: float,
        final_score: float,
        risk_band: str,
        transaction_amount: Optional[float] = None,
        transaction_type: Optional[str] = None,
    ) -> list[str]:
        reasons = []

        if ml_score > 0.6:
            reasons.append("ML model detected anomalous behavioral pattern")
        if rules_score > 0.5:
            reasons.append("Transaction exceeds standard risk thresholds")
        if heuristic_score > 0.4:
            reasons.append("Unusual activity pattern detected")
        if transaction_amount and transaction_amount > settings.RISK_MAX_SINGLE_TRANSACTION:
            reasons.append(f"Transaction amount (₹{transaction_amount:,.2f}) exceeds single transaction limit")
        if final_score > settings.RISK_HIGH_RISK_THRESHOLD:
            reasons.append(f"Overall risk score ({final_score:.2f}) exceeds high-risk threshold")

        if not reasons:
            if transaction_amount and transaction_amount > 50000:
                reasons.append(f"Transaction amount (₹{transaction_amount:,.2f}) flagged for review")
            else:
                reasons.append("Transaction within normal parameters")

        return reasons

    async def _create_alert(
        self,
        user_id: int,
        session_id: Optional[str],
        transaction_id: Optional[int],
        alert_type: str,
        severity: SeverityLevel,
        risk_score: float,
        details: dict,
    ):
        alert = FraudAlert(
            user_id=user_id,
            session_id=session_id,
            transaction_id=transaction_id,
            alert_type=alert_type,
            severity=severity,
            risk_score=risk_score,
            status=AlertStatus.OPEN,
            details=details,
        )
        self.db.add(alert)
