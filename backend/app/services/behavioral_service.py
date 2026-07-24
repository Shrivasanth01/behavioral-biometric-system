from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, text
from datetime import datetime, timezone, timedelta
from typing import Optional
import json

from app.models.behavioral import (
    BehavioralEvent,
    BehavioralFeature,
    BehavioralProfile,
    MlModel,
    RiskScore,
)
from app.exceptions import NotFoundException, BadRequestException


class BehavioralService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest_event(self, event_data: dict) -> BehavioralEvent:
        event = BehavioralEvent(
            session_id=event_data["session_id"],
            user_id=event_data.get("user_id"),
            device_type=event_data.get("device_type"),
            device_fingerprint=event_data.get("device_fingerprint"),
            event_type=event_data["event_type"],
            event_data=event_data.get("event_data") or {},
            client_timestamp=event_data.get("client_timestamp"),
            server_timestamp=datetime.now(timezone.utc),
            ip_address=event_data.get("ip_address"),
            user_agent=event_data.get("user_agent"),
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def get_session_events(self, session_id: str) -> list[BehavioralEvent]:
        result = await self.db.execute(
            select(BehavioralEvent)
            .where(BehavioralEvent.session_id == session_id)
            .order_by(BehavioralEvent.server_timestamp)
        )
        return result.scalars().all()

    async def get_user_profile(self, user_id: int) -> BehavioralProfile:
        result = await self.db.execute(
            select(BehavioralProfile).where(BehavioralProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            profile = BehavioralProfile(
                user_id=user_id,
                profile={
                    "typing_speed_avg": 0,
                    "typing_speed_std": 0,
                    "mouse_speed_avg": 0,
                    "scroll_pattern": "unknown",
                    "session_times": [],
                    "common_ips": [],
                    "common_devices": [],
                    "transaction_patterns": {
                        "avg_amount": 0,
                        "frequency": 0,
                        "preferred_time": "unknown",
                    },
                    "risk_factors": {},
                },
                model_version="1.0.0",
                session_count=0,
                drift_status="normal",
            )
            self.db.add(profile)
            await self.db.flush()
            await self.db.refresh(profile)

        return profile

    async def get_risk_history(self, user_id: int, days: int = 30) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            select(RiskScore)
            .where(
                RiskScore.user_id == user_id,
                RiskScore.created_at >= since,
            )
            .order_by(RiskScore.created_at)
        )
        scores = result.scalars().all()

        history = {}
        for score in scores:
            date_key = score.created_at.strftime("%Y-%m-%d")
            if date_key not in history:
                history[date_key] = {
                    "date": date_key,
                    "risk_scores": [],
                    "risk_bands": [],
                    "count": 0,
                }
            history[date_key]["risk_scores"].append(score.final_score)
            history[date_key]["risk_bands"].append(score.risk_band)
            history[date_key]["count"] += 1

        result_list = []
        for date_key, data in sorted(history.items()):
            avg_score = sum(data["risk_scores"]) / len(data["risk_scores"]) if data["risk_scores"] else 0
            band_counts = {}
            for band in data["risk_bands"]:
                band_counts[band] = band_counts.get(band, 0) + 1
            dominant_band = max(band_counts, key=band_counts.get) if band_counts else "LOW"
            result_list.append({
                "date": date_key,
                "risk_score": round(avg_score, 4),
                "risk_band": dominant_band,
                "transaction_count": data["count"],
                "alert_count": 0,
            })

        return result_list

    async def get_user_sessions(self, user_id: int, limit: int = 20) -> list[dict]:
        result = await self.db.execute(
            select(
                BehavioralEvent.session_id,
                BehavioralEvent.device_type,
                BehavioralEvent.ip_address,
                func.count(BehavioralEvent.id).label("event_count"),
                func.min(BehavioralEvent.server_timestamp).label("first_event"),
                func.max(BehavioralEvent.server_timestamp).label("last_event"),
            )
            .where(BehavioralEvent.user_id == user_id)
            .group_by(
                BehavioralEvent.session_id,
                BehavioralEvent.device_type,
                BehavioralEvent.ip_address,
            )
            .order_by(desc(func.max(BehavioralEvent.server_timestamp)))
            .limit(limit)
        )
        rows = result.fetchall()

        sessions = []
        for row in rows:
            risk_result = await self.db.execute(
                select(RiskScore.final_score)
                .where(RiskScore.session_id == row.session_id)
                .order_by(desc(RiskScore.created_at))
                .limit(1)
            )
            risk_score = risk_result.scalar_one_or_none()

            sessions.append({
                "session_id": row.session_id,
                "device_type": row.device_type,
                "ip_address": row.ip_address,
                "event_count": row.event_count,
                "first_event": row.first_event,
                "last_event": row.last_event,
                "risk_score": risk_score,
            })

        return sessions

    async def extract_features(self, session_id: str) -> Optional[dict]:
        result = await self.db.execute(
            select(BehavioralFeature).where(
                BehavioralFeature.session_id == session_id
            ).order_by(desc(BehavioralFeature.created_at)).limit(1)
        )
        feature = result.scalar_one_or_none()
        return feature.features if feature else None

    async def compute_session_features(self, session_id: str) -> dict:
        events = await self.get_session_events(session_id)
        if not events:
            return {}

        event_types = {}
        time_deltas = []
        mouse_events = []
        key_events = []
        prev_time = None

        for event in events:
            et = event.event_type
            event_types[et] = event_types.get(et, 0) + 1

            if et == "mousemove" or et == "mouseclick":
                mouse_events.append(event)
            elif et == "keydown" or et == "keyup":
                key_events.append(event)

            if prev_time and event.client_timestamp:
                delta = (event.client_timestamp - prev_time).total_seconds()
                if 0 < delta < 60:
                    time_deltas.append(delta)
            if event.client_timestamp:
                prev_time = event.client_timestamp

        avg_time_delta = sum(time_deltas) / len(time_deltas) if time_deltas else 0
        typing_speed = len(key_events) / (sum(time_deltas) if time_deltas else 1)

        features = {
            "total_events": len(events),
            "event_type_distribution": event_types,
            "avg_time_between_events": round(avg_time_delta, 4),
            "typing_speed_events_per_sec": round(typing_speed, 4),
            "mouse_event_count": len(mouse_events),
            "key_event_count": len(key_events),
            "session_duration_seconds": 0,
            "unique_event_types": len(event_types),
        }

        if events and len(events) >= 2:
            first = events[0]
            last = events[-1]
            if first.server_timestamp and last.server_timestamp:
                duration = (last.server_timestamp - first.server_timestamp).total_seconds()
                features["session_duration_seconds"] = round(duration, 2)

        return features

    async def update_profile_from_session(self, user_id: int, session_id: str):
        profile = await self.get_user_profile(user_id)
        features = await self.compute_session_features(session_id)

        feature_record = BehavioralFeature(
            session_id=session_id,
            user_id=user_id,
            features=features,
            model_version=profile.model_version,
        )
        self.db.add(feature_record)

        current_profile = profile.profile or {}
        current_profile["last_session_features"] = features
        current_profile["session_count"] = current_profile.get("session_count", 0) + 1
        current_profile["last_active"] = datetime.now(timezone.utc).isoformat()

        profile.profile = current_profile
        profile.session_count = (profile.session_count or 0) + 1

        await self.db.flush()
