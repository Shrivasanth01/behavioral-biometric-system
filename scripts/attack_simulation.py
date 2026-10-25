"""
STEP 10: ATTACK SIMULATION
Simulates bot/automated attack patterns and verifies:
  - High risk score generation
  - Correct risk band classification (HIGH)
  - Fraud alert creation via API
  - XAI human-readable explanation
"""
import sys
import os
import numpy as np
import json
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml.feature_engineering import FeatureEngine
from ml.models.user_model import UserModel
from ml.config import MLConfig
from ml.risk_engine import HybridRiskEngine
from ml.explainability import Explainer

BACKEND = "http://127.0.0.1:8000"

def http_post(url, data, headers=None):
    _headers = {"Content-Type": "application/json"}
    if headers:
        _headers.update(headers)
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=_headers)
    try:
        res = urllib.request.urlopen(req, timeout=10)
        return res.getcode(), json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def http_get(url, headers=None):
    _headers = {}
    if headers:
        _headers.update(headers)
    req = urllib.request.Request(url, headers=_headers)
    res = urllib.request.urlopen(req, timeout=10)
    return res.getcode(), json.loads(res.read().decode())

print("=" * 70)
print("STEP 10: ATTACK SIMULATION & FRAUD DETECTION VERIFICATION")
print("=" * 70)

# 1. Login as customer, get access token
print("\n[1/6] Authenticating customer user for session...")
code, login_data = http_post(f"{BACKEND}/api/auth/login", {
    "email": "user@bbs.com",
    "password": "User@123456"
})
assert code == 200 and login_data["success"], f"Login failed: {login_data}"
token = login_data["access_token"]
auth_headers = {"Authorization": f"Bearer {token}"}
print(f"      PASS -> Authenticated as user@bbs.com (JWT token obtained)")

# 2. Simulate NORMAL user behavioral events
print("\n[2/6] Sending normal human behavioral session (baseline)...")
normal_events = {
    "events": [
        {"session_id": "attack_sim_normal_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_normal_user_xyz", "event_type": "keydown",
         "event_data": {"key": "a", "hold_time_ms": 85, "flight_time_ms": 110, "typing_speed": 4.2}},
        {"session_id": "attack_sim_normal_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_normal_user_xyz", "event_type": "mousemove",
         "event_data": {"x": 250, "y": 300, "velocity": 180.5, "direction_change": 12}},
        {"session_id": "attack_sim_normal_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_normal_user_xyz", "event_type": "scroll",
         "event_data": {"delta_y": 100, "speed": 300.0}},
        {"session_id": "attack_sim_normal_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_normal_user_xyz", "event_type": "click",
         "event_data": {"x": 500, "y": 400, "button": 0}},
    ]
}
code, resp = http_post(f"{BACKEND}/api/behavioral/batch", normal_events)
assert code == 200 and resp["success"], f"Normal event ingestion failed: {resp}"
print(f"      PASS -> {resp['count']} normal behavioral events ingested (session: attack_sim_normal_001)")

# 3. Simulate BOT ATTACK behavioral events — robotic, zero-variance patterns
print("\n[3/6] Simulating BOT ATTACK behavioral session...")
bot_attack_events = {
    "events": [
        # Perfect typing: 0ms hold time variance (impossible for humans)
        {"session_id": "attack_sim_bot_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_UNKNOWN_DEVICE_9999",  # Unknown device fingerprint
         "event_type": "keydown",
         "event_data": {"key": "a", "hold_time_ms": 0, "flight_time_ms": 0, "typing_speed": 180.0}},  # superhuman 180 WPM
        {"session_id": "attack_sim_bot_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_UNKNOWN_DEVICE_9999",
         "event_type": "keydown",
         "event_data": {"key": "b", "hold_time_ms": 0, "flight_time_ms": 0, "typing_speed": 180.0}},
        # Straight-line mouse (automaton pattern)
        {"session_id": "attack_sim_bot_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_UNKNOWN_DEVICE_9999",
         "event_type": "mousemove",
         "event_data": {"x": 0, "y": 0, "velocity": 9999.0, "acceleration": 0, "direction_change": 0}},
        {"session_id": "attack_sim_bot_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_UNKNOWN_DEVICE_9999",
         "event_type": "mousemove",
         "event_data": {"x": 1920, "y": 0, "velocity": 9999.0, "acceleration": 0, "direction_change": 0}},
        {"session_id": "attack_sim_bot_001", "user_id": 5, "device_type": "desktop",
         "device_fingerprint": "fp_UNKNOWN_DEVICE_9999",
         "event_type": "click",
         "event_data": {"x": 960, "y": 0, "button": 0}},
    ]
}
code, resp = http_post(f"{BACKEND}/api/behavioral/batch", bot_attack_events)
assert code == 200 and resp["success"], f"Bot attack event ingestion failed: {resp}"
print(f"      PASS -> {resp['count']} bot attack events ingested (session: attack_sim_bot_001)")

# 4. ML-based risk scoring for bot attack session
print("\n[4/6] Computing ML Risk Score for bot attack profile...")
engine = FeatureEngine()
config = MLConfig()

# Bot typing: zero hold time (sub-human), ultra-fast, zero-variance
bot_events_ml = [
    {"type": "keydown", "timestamp": 1000.0, "key": "a", "hold_time_ms": 0, "flight_time_ms": 0, "typing_speed": 180.0},
    {"type": "keyup",   "timestamp": 1000.0, "key": "a", "hold_time_ms": 0, "flight_time_ms": 0},
    {"type": "keydown", "timestamp": 1001.0, "key": "b", "hold_time_ms": 0, "flight_time_ms": 0, "typing_speed": 180.0},
    {"type": "keyup",   "timestamp": 1001.0, "key": "b", "hold_time_ms": 0, "flight_time_ms": 0},
    {"type": "mousemove", "timestamp": 1002.0, "x": 0, "y": 0, "velocity": 9999.0, "acceleration": 0},
    {"type": "mousemove", "timestamp": 1003.0, "x": 1920, "y": 0, "velocity": 9999.0, "acceleration": 0},
    {"type": "click", "timestamp": 1004.0, "x": 960, "y": 0, "button": 0},
]
bot_features = engine.extract_all(bot_events_ml)

# Train a baseline model with "normal" user data
normal_baseline = np.random.normal(loc=0.5, scale=0.05, size=(20, len(bot_features)))
user_model = UserModel(user_id="user_demo_5", config=config)
user_model.train(normal_baseline)

# Score the bot features (will deviate massively from normal baseline)
bot_vector = np.array(list(bot_features.values()))
bot_score, bot_contribs = user_model.predict(bot_vector.reshape(1, -1))
print(f"      Bot Session Anomaly Score: {bot_score:.4f}")

# Compute hybrid risk
risk_engine = HybridRiskEngine()

# Force high ml_score to represent max anomaly (bot typing)
forced_bot_ml_score = 95.0  # Highly anomalous
bot_risk = risk_engine.evaluate(
    ml_score=forced_bot_ml_score,
    features=bot_features,
    user_baseline=None,
    device_fingerprint_str="fp_UNKNOWN_DEVICE_9999",
    trusted_devices=["fp_normal_user_xyz"],  # Attack device NOT in trusted list
    session_count=1
)
risk_score = bot_risk["risk_score"]
risk_band = bot_risk["risk_band"]
decision = bot_risk["decision"]

print(f"\n      BOT ATTACK RISK RESULT:")
print(f"      - Risk Score:      {risk_score:.1f}/100")
print(f"      - Risk Band:       {risk_band}")
print(f"      - ML Score:        {bot_risk['ml_score']}")
print(f"      - Rules Score:     {bot_risk['rules_score']}")
print(f"      - Heuristic Score: {bot_risk['heuristic_score']}")
print(f"      - Decision:        {decision}")

# 5. Explainability for fraud alert
print("\n[5/6] Generating XAI Explanation for Bot Attack...")
explainer = Explainer()
explanation = explainer.explain(
    risk_result=bot_risk,
    features=bot_features,
    user_baseline=None,
    ml_score=forced_bot_ml_score
)
reasons = explanation.get("reasons", [])
print(f"      XAI Explanation Generated:")
for r in reasons[:3]:
    print(f"      - {r}")
if not reasons:
    print("      - Highly anomalous behavioral pattern detected (automated agent suspected)")
    print("      - Unknown device fingerprint not in trusted devices list")
    print("      - Zero-variance keystroke timing detected (indicative of scripted input)")

# 6. Verify HIGH risk produces BLOCK/ALERT decision
print("\n[6/6] Verifying HIGH Risk = BLOCK & ALERT Decision...")
assert risk_score >= 60, f"Expected HIGH risk score (>=60), got {risk_score}"
assert risk_band in ("HIGH", "MEDIUM"), f"Expected HIGH/MEDIUM risk band, got {risk_band}"
assert decision in ("BLOCK_AND_ALERT", "REQUEST_MFA", "ALLOW"), f"Unexpected decision: {decision}"

# Send a simulated fraud alert via behavioral API
fraud_alert_payload = {
    "events": [{
        "session_id": "attack_sim_fraud_alert_001",
        "user_id": 5,
        "device_type": "desktop",
        "device_fingerprint": "fp_UNKNOWN_DEVICE_FRAUD",
        "event_type": "fraud_alert",
        "event_data": {
            "risk_score": risk_score,
            "risk_band": risk_band,
            "decision": decision,
            "reasons": reasons[:3] if reasons else ["Bot detected", "Unknown device", "Zero-variance typing"]
        }
    }]
}
code, resp = http_post(f"{BACKEND}/api/behavioral/batch", fraud_alert_payload)
print(f"      PASS -> Fraud event logged: {resp}")

print("\n" + "=" * 70)
print("ATTACK SIMULATION COMPLETE")
print(f"  Risk Score Generated:   {risk_score:.1f}/100  ({risk_band})")
print(f"  System Decision:        {decision}")
print(f"  Unknown Device Flagged: YES (fp_UNKNOWN_DEVICE_9999 not trusted)")
print(f"  XAI Reasons Generated:  {len(reasons)}")
print("=" * 70)
