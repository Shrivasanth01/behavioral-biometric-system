# Data Flow Diagrams

## 1. Authentication Flow (Login with MFA)

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web/Mobile Client
    participant BE as Backend API
    participant DB as PostgreSQL
    participant ML as ML Engine
    participant RD as Redis

    U->>W: Enter email & password
    W->>BE: POST /api/auth/login
    BE->>DB: Verify credentials
    DB-->>BE: User record

    alt Invalid credentials
        BE-->>W: 401 Unauthorized
        W-->>U: Show error
    else Valid credentials
        BE->>BE: Generate temp JWT (5min)
        BE-->>W: 200 { mfa_required: true, temp_token }
        W-->>U: Prompt for MFA code

        U->>W: Enter TOTP/SMS code
        W->>BE: POST /api/auth/verify-mfa { temp_token, otp_code }
        BE->>BE: Verify OTP against user secret

        alt MFA valid
            BE->>BE: Generate access_token + refresh_token
            BE->>RD: Cache session data
            BE->>DB: Log login session
            BE-->>W: 200 { access_token, refresh_token }
            W->>W: Store tokens securely
            W-->>U: Redirect to dashboard
        else MFA invalid
            BE-->>W: 401 Invalid OTP
            W-->>U: Show error
        end
    end
```

## 2. Transaction Flow with Behavioral Risk Assessment

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web/Mobile Client
    participant JS as Behavioral Tracker
    participant BE as Backend API
    participant ML as ML Engine
    participant DB as PostgreSQL
    participant RD as Redis

    Note over U,W: User fills transfer form
    U->>W: Enter transfer details
    W->>JS: Auto-capture keystroke events
    JS->>JS: Buffer events (throttled at 5s intervals)
    JS->>BE: POST /api/events/batch (async)

    U->>W: Click "Send" button
    JS->>BE: Final event batch flush (mouse click)
    W->>BE: POST /api/transactions/transfer

    BE->>BE: Validate request (balance, limits)
    BE->>ML: assess_risk(session_id, amount, device)

    ML->>ML: FeatureEngine.extract_all(events)
    ML->>ML: InferencePipeline.score(user_id, events)
    ML->>ML: HybridRiskEngine.evaluate(ml_score, features)

    alt LOW risk (0-30)
        ML-->>BE: { score: 15, band: "LOW", decision: "ALLOW" }
        BE->>DB: Create transaction (status: completed)
        BE-->>W: 200 { reference, status: "completed" }
        W-->>U: "Transfer successful"
    else MEDIUM risk (31-70)
        ML-->>BE: { score: 55, band: "MEDIUM", decision: "REQUEST_MFA" }
        BE-->>W: 200 { requires_mfa: true, temp_token }
        W-->>U: Prompt for MFA verification
        U->>W: Enter MFA code
        W->>BE: POST /api/auth/verify-mfa { temp_token, otp }
        alt MFA verified
            BE->>DB: Create transaction (status: completed)
            BE-->>W: 200 { reference, status: "completed" }
            W-->>U: "Transfer successful"
        else MFA failed
            BE-->>W: 401 "MFA verification failed"
            W-->>U: Show error
        end
    else HIGH risk (71-100)
        ML-->>BE: { score: 85, band: "HIGH", decision: "BLOCK" }
        BE->>DB: Create transaction (status: blocked)
        BE->>DB: Create fraud alert (severity: HIGH)
        BE-->>W: 200 { status: "blocked", reason: "High risk" }
        W-->>U: "Transaction blocked for security"
    end
```

## 3. Behavioral Event Capture & Training Pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant JS as Web SDK (tracker.js)
    participant BE as Backend API
    participant CL as Celery Worker
    participant ML as Training Pipeline
    participant DB as PostgreSQL
    participant FS as File System (model_store/)

    loop Every session
        U->>JS: Type, move mouse, click, scroll
        JS->>JS: Buffer events (max 50 or 5s interval)
        JS->>BE: POST /api/events/batch { events, session_id, fingerprint }

        BE->>BE: BehavioralService.ingest_event()
        BE->>DB: INSERT INTO behavioral_events
        BE-->>JS: 200 { event_ids }
    end

    Note over BE: After N sessions per user

    BE->>CL: trigger_train_for_user.delay(user_id)
    CL->>CL: TrainingPipeline.train_for_user()
    CL->>ML: FeatureEngine.extract_batch(session_batches)
    ML->>ML: Compute 36 behavioral features
    CL->>CL: UserModel.train(features)
    CL->>CL: IsolationForest.fit(scaled_features)
    CL->>CL: Compute adaptive threshold
    CL->>FS: Save model to model_store/{user_id}/model_v{p}.pkl
    CL->>FS: Save model metadata JSON
    CL->>FS: Update behavioral profile JSON
    CL->>DB: Update behavioral_profiles table
```

## 4. Fraud Alert Resolution Flow

```mermaid
sequenceDiagram
    participant ML as ML Engine
    participant BE as Backend API
    participant DB as PostgreSQL
    participant RD as Redis
    participant DS as Security Dashboard
    participant SA as Security Analyst
    participant NT as Notification Service

    ML->>ML: HybridRiskEngine.evaluate(ml_score, features)
    alt Score > 70
        ML->>BE: Risk assessment result (HIGH)
        BE->>BE: evaluate_with_details()
        BE->>ML: Explainer.explain(features, baseline)
        ML-->>BE: { reasons, feature_contributions }
        BE->>DB: INSERT INTO risk_scores
        BE->>DB: INSERT INTO fraud_alerts (status: open)
        BE->>DB: INSERT INTO explainability_results
        BE->>RD: PUBLISH alert:user:{user_id}
        RD->>DS: Push notification (WebSocket)
        DS-->>SA: Alert card appears in dashboard
        NT->>U: Email/SMS notification of suspicious activity

        SA->>DS: Open alert detail
        DS->>BE: GET /api/risk/alerts/{alert_id}
        BE-->>DS: Alert data + explainability
        DS->>BE: GET /api/risk/explain/{session_id}
        BE->>ML: Explainer.explain()
        ML-->>BE: { reasons, feature_contributions }
        BE-->>DS: { risk_score, reasons, features }

        SA->>DS: Investigate - review session timeline
        DS->>BE: GET /api/events/session/{session_id}
        DS->>BE: GET /api/admin/users/{user_id}
        BE-->>DS: User details, devices, history

        alt False positive
            SA->>DS: Mark as false_positive
            DS->>BE: PUT /api/risk/alerts/{id}/status
            BE->>DB: UPDATE fraud_alerts SET status = 'false_positive'
        else Legitimate fraud
            SA->>DS: Mark as resolved, add notes
            DS->>BE: PUT /api/risk/alerts/{id}/status
            BE->>DB: UPDATE fraud_alerts SET status = 'resolved'
            BE->>DB: UPDATE users SET is_locked = true (if needed)
            NT->>U: Account temporarily locked notification
        end
    end
```

## 5. ML Model Drift Detection Flow

```mermaid
sequenceDiagram
    participant CP as Celery Periodic Task
    participant ML as DriftDetector
    participant FS as Profile Store
    participant DB as PostgreSQL
    participant RG as ModelRegistry
    participant AD as Admin Dashboard

    CP->>ML: check_all_features() (every 24h)
    ML->>ML: Compute PSI on reference vs monitoring windows
    ML->>ML: Count drifted features

    alt Drift detected
        ML-->>DB: INSERT INTO model_drift_logs
        ML-->>DB: INSERT INTO retraining_queue

        DB->>AD: Show drift alert in dashboard
        AD-->>SA: "Feature drift detected - {n} features drifted"

        SA->>AD: Review drift report
        AD->>ML: get_drift_trend(feature_name)
        ML-->>AD: { trend: "increasing", psi_history }

        SA->>AD: Trigger retraining
        AD->>DB: UPDATE retraining_queue SET priority = 100
        CP->>CP: TrainingPipeline.retrain_if_needed()
        alt Retrain success
            CP->>RG: register_model(new_version)
            CP->>FS: Update user profiles
            CP->>ML: set_reference_batch(new_features)
            ML-->>DB: UPDATE model_drift_logs SET action_taken = 'retrained'
        end
    else No drift
        ML-->>CP: { has_drifted: false, severity: "STABLE" }
    end
```

## Data Flow Summary

| Flow | Trigger | Key Components | Average Latency |
|------|---------|----------------|-----------------|
| Authentication | User login attempt | AuthService, JWT, MFA | ~200ms (without MFA) |
| Transaction + Risk | Transfer submission | BankingService, RiskService, HybridRiskEngine | ~350ms |
| Event Ingestion | User interaction | BehavioralTracker, BehavioralService, FeatureEngine | ~50ms (batch) |
| Fraud Alert | Risk score > 70 | RiskService, Explainer, NotificationService | ~100ms |
| Model Training | Session threshold met | TrainingPipeline, UserModel, ModelRegistry | ~30s-2min |
| Drift Detection | Periodic (24h) | DriftDetector, PSI computation, ModelRegistry | ~5min |
