# ML Architecture

## Overview

The ML subsystem uses unsupervised anomaly detection to model user behavior and detect deviations indicative of account takeover or fraud. It employs a **hybrid ensemble approach** combining Isolation Forest, One-Class SVM, and an optional autoencoder (Keras/TensorFlow). All models train on per-user behavioral profiles with a global fallback model for cold-start users.

## Feature Engineering

### Feature Categories

**36 features total** across 4 categories, defined in `ml/config.py:8-53`:

#### Keystroke Features (10)

| Feature | Description | Source (`ml/feature_engineering.py`) |
|---------|-------------|--------------------------------------|
| `typing_speed_mean` | Mean inter-key interval inverted (keys/sec) | `_extract_keystroke_features:70` |
| `typing_speed_std` | Std dev of inter-key intervals | `:72` |
| `key_hold_mean` | Mean key press duration (ms) | `:76` |
| `key_hold_std` | Std dev of key hold durations | `:77` |
| `backspace_rate` | Ratio of Backspace/Delete to total keys | `:84` |
| `error_correction_rate` | Ratio of correction keys (Backspace, Delete, arrows) to total keys | `:89` |
| `trigram_latency_mean` | Mean time between 1st and 4th key in sliding trigram window | `:92` |
| `key_press_freq_entropy` | Shannon entropy of key press frequency distribution | `:96` |
| `special_key_ratio` | Ratio of modifier keys (Shift, Ctrl, Alt, etc.) to total keys | `:100` |
| `number_row_freq` | Ratio of digit keys pressed to total keys | `:104` |

#### Mouse Features (12)

| Feature | Description | Source |
|---------|-------------|--------|
| `cursor_velocity_mean` | Mean cursor movement speed (px/ms) | `_extract_mouse_features:151` |
| `cursor_velocity_std` | Std dev of cursor velocity | `:152` |
| `cursor_accel_mean` | Mean cursor acceleration (px/ms²) | `:153` |
| `cursor_accel_std` | Std dev of cursor acceleration | `:154` |
| `path_length` | Total Euclidean distance traveled by cursor | `:155` |
| `direction_entropy` | Shannon entropy of cursor direction binned into 8 octants | `:160` |
| `click_frequency` | Clicks per second | `:165` |
| `double_click_rate` | Ratio of clicks with <500ms interval to total clicks | `:169` |
| `right_click_ratio` | Ratio of right-clicks (button=2) to total clicks | `:172` |
| `scroll_speed_mean` | Mean scroll delta per unit time | `:186` |
| `scroll_direction_changes` | Count of direction changes in scroll delta sign | `:188` |
| `idle_time_ratio` | Ratio of idle time (gaps > 2× P90 inter-event interval) to total session time | `:200` |

#### Session Features (8)

| Feature | Description | Source |
|---------|-------------|--------|
| `session_duration` | Total elapsed time (ms) | `_extract_session_features:213` |
| `total_interactions` | Count of all events in session | `:214` |
| `interaction_density` | Interactions per second | `:217` |
| `navigation_depth` | Number of pageview-type events | `:222` |
| `navigation_entropy` | Shannon entropy of page transition frequencies | `:228` |
| `form_focus_consistency` | Ratio of forward-to-backward field transitions | `:239` |
| `time_of_day` | Starting hour normalized to [0, 1] | `:247` |
| `day_of_week` | Starting day normalized to [0, 1] | `:250` |

#### Mobile Features (8)

| Feature | Description | Source |
|---------|-------------|--------|
| `swipe_velocity_mean` | Mean swipe speed (px/ms) | `_extract_mobile_features:272` |
| `swipe_velocity_std` | Std dev of swipe velocity | `:273` |
| `swipe_accel_mean` | Mean swipe acceleration | `:276` |
| `touch_pressure_mean` | Mean touch force | `:291` |
| `touch_pressure_std` | Std dev of touch force | `:292` |
| `touch_duration_mean` | Mean touch hold time (ms) | `:295` |
| `gesture_complexity` | Count of velocity direction changes exceeding 10% of mean | `:300` |
| `multi_touch_ratio` | Ratio of multi-touch to single-touch events | `:312` |

### Feature Computation Pipeline

```
Raw Events (JSON) → preprocess_events() → pd.DataFrame → FeatureEngine.extract_all()
```

Processing steps in `ml/utils.py`:
1. `validate_events()`: checks required keys (`type`, `timestamp`)
2. `preprocess_events()`: converts to DataFrame, sorts by timestamp, replaces inf/nan
3. Categorical features dispatched to `_extract_keystroke/mouse/session/mobile_features()`
4. Missing features set to `0.0` via `features.setdefault(k, 0.0)`

## Model Architecture

### User Model (`ml/models/user_model.py`)

Primary model: **Isolation Forest** (scikit-learn)

```python
IsolationForest(
    n_estimators=200,
    max_samples=256,
    contamination=0.05,
    n_jobs=-1,
    random_state=42,
)
```

**Training flow:**
1. `scaler.fit(features)` → StandardScaler
2. `IsolationForest.fit(scaled)` → train model
3. `score_samples(scaled)` → compute raw anomaly scores
4. `_compute_adaptive_threshold(scores)` → dynamic threshold

**Adaptive threshold computation:**
```
threshold = mean(scores) - k * std(scores)
clamped to [min: -0.3, max: 0.5]
k = 2.5 (configurable via adaptive_k_multiplier)
```

**Score normalization:**
```python
normalized = (threshold - raw_score) / |threshold|
clamped to [-1.0, 1.0]
final_score = (normalized + 1.0) * 50.0   # Maps to [0, 100]
```

**Optional secondary models:**
- **One-Class SVM**: `nu=0.05, gamma='scale'` — zero-shot classification boundary
- **Autoencoder** (Keras): encoding_dim=16, ReLU activations, MSE loss, Adam optimizer — reconstruction-based anomaly detection

### Global Model (`ml/models/global_model.py`)

Ensemble of 10 bagged Isolation Forest models:

```python
for i in range(10):
    indices = rng.choice(n_samples, size=0.8*n_samples, replace=True)
    model = IsolationForest(
        n_estimators=40,          # 200 / (10/5)
        max_samples=256,
        contamination=0.05,
        n_jobs=1,
    )
    model.fit(scaled[indices])
```

**Ensemble prediction:**
```python
mean_score = mean([model.score_samples(features) for model in ensemble])
```

**Global model threshold:** P5 percentile of all training scores.

### Cold Start Strategy

- Users with <5 low-risk sessions use global model exclusively
- Global model trained on aggregate population data (requires 10+ batches)
- Fallback score: 50.0 if global model unavailable
- Cold start status tracked in `BehavioralProfile.cold_start`

## Inference Pipeline

```
events → FeatureEngine.extract_all(events) → feature_vec [1×36]
    ↓
InferencePipeline.score(user_id, events)
    ↓
    ├── User model exists & not cold start?
    │   ├── Yes: UserModel.predict(feature_vec) → (anomaly_score, feature_contributions)
    │   └── No:  GlobalModel.predict(feature_vec) → (anomaly_score, fallback)
    ↓
    ↓   Model cache checked first (TTL: 3600s, max 100 models)
    ↓   Profile cache checked first (TTL: 1800s, max 1000 profiles)
    ↓
Return: { ml_score, feature_contributions, model_source, features, timestamp }
```

## Risk Engine

### Hybrid Risk Score Formula (`ml/risk_engine.py`)

```
final_score = 0.65 * ml_score + 0.25 * rules_score + 0.10 * heuristic_score
clamped to [0, 100]
```

### Rules Score Components

| Rule | Condition | Points |
|------|-----------|--------|
| Typing speed anomaly | `|z_typing| > 2.0` | 30 |
| Mouse speed anomaly | `|z_mouse| > 2.0` | 25 |
| Session duration anomaly | `z_duration < -3.0` (short session) | 20 |
| Untrusted device | device not in trusted list | 15 |
| Suspicious time | hour in [22,23,0,1,2,3,4,5] | 10 |
| Navigation entropy anomaly | `|z_nav| > 2.0` | 20 |

### Heuristic Score Components

| Heuristic | Condition | Points |
|-----------|-----------|--------|
| Too few interactions | `total_interactions < 5` | 50 |
| Perfect typing | `backspace_rate == 0 && interactions > 10` | 10 |
| Automated mouse pattern | `direction_entropy < 0.5 && interactions > 20` | 30 |
| Automated keyboard pattern | `key_press_freq_entropy < 0.3 && interactions > 15` | 30 |
| No idle time | `idle_time_ratio < 0.01 && interactions > 20` | 10 |

### Risk Bands & Decisions

```python
LOW:    score <= 30  → "ALLOW"
MEDIUM: score <= 70  → "REQUEST_MFA"
HIGH:   score > 70   → "BLOCK_AND_ALERT"
```

## Explainability

### Feature Impact Computation (`ml/explainability.py`)

```python
impact(feature) = -tanh(z_score / 3.0)
# Positive z-score → negative impact (anomalous) → risk increases
```

- Top 6 features by absolute impact are selected
- Feature names mapped to human-readable reason templates
- 15 reason templates defined (e.g., `"Typing speed {direction} {pct}% than personal baseline"`)
- Device fingerprint and interaction count included as additional reasons
- Cold start explanations automatically generated with confidence note
- Results limited to 8 reasons maximum

### Explanation Output Structure

```json
{
  "risk_score": 72.3,
  "risk_band": "HIGH",
  "reasons": [
    "Typing speed higher 45% than personal baseline of 4.2ms",
    "New device fingerprint detected (not in trusted devices)",
    "Mouse movement entropy lower than historical pattern (0.31 vs 0.78)"
  ],
  "feature_contributions": {
    "typing_speed_mean": -0.35,
    "device_match": -0.15,
    "direction_entropy": -0.25
  },
  "ml_score": 65.0,
  "timestamp": "2026-06-14T10:30:00"
}
```

## Model Training Pipeline

### User Model Training (`ml/training_pipeline.py`)

```
Trigger: session_count % retrain_interval (10) == 0
         OR cold_start == True

TrainingPipeline.train_for_user(user_id, event_batches, risk_scores):
  1. Filter: only low-risk sessions (risk <= 70)
  2. Feature extraction: FeatureEngine.extract_batch(low_risk_batches) → DataFrame
  3. Cold start check: session_count < 5?
     - Yes: Skip training, return cold_start message
     - No: Proceed
  4. Load previous features if model exists → vstack with new features
  5. Truncate to max 10,000 samples
  6. UserModel.train(features)
  7. Save model to model_store/{user_id}/model_v{n}.pkl
  8. Compute feature statistics (mean, std, min, max, quartiles)
  9. Update BehavioralProfile (version, model_version, session_count, feature_stats)
  10. Register model in ModelRegistry
```

### Global Model Training

```
TrainingPipeline.retrain_global_model(all_user_batches):
  1. Aggregate features from non-cold-start users
  2. Minimum 10 samples required
  3. GlobalModel.train(combined_features)
  4. Save to model_store/_global_/global_model_v{n}.pkl
```

### Training Configuration (`ml/config.py`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `min_sessions_for_personal_model` | 5 | Minimum sessions before personal model created |
| `min_samples_for_training` | 20 | Minimum feature vectors for training |
| `retrain_interval_sessions` | 10 | Sessions between retraining cycles |
| `max_training_samples` | 10000 | Max historical samples retained |
| `anomaly_score_percentile_threshold` | 95.0 | P95 threshold for anomaly classification |

## Model Registry

Version management via `ml/model_registry.py`:

| Operation | Description |
|-----------|-------------|
| `register_model(user_id, version, path, metrics)` | Add new model version, archive previous |
| `get_active_model(user_id)` | Latest active model |
| `rollback(user_id, version)` | Revert to specific version |
| `get_all_active_models()` | All current models (for dashboard) |
| `get_summary_stats()` | Total/active/archived counts |

Models stored as pickle files in:
```
model_store/
├── _global_/
│   ├── global_model_v1.pkl
│   └── global_model_v1_meta.json
└── {user_id}/
    ├── model_v1.pkl
    ├── model_v1_meta.json
    ├── model_v2.pkl
    └── model_v2_meta.json
```

Profile store:
```
profile_store/
├── {user_id}_profile.json
```

Registry:
```
model_registry/model_registry.json
```

## Drift Detection

### Population Stability Index (PSI) (`ml/drift_detection.py`)

```python
def compute_psi(expected, actual, n_bins=10):
    # Bins: 10 equal-width percentiles
    # expected_pct = histogram(expected, 10 bins) → normalized
    # actual_pct = histogram(actual, 10 bins) → normalized
    # PSI = Σ((actual - expected) * ln(actual / expected))
```

### Drift Thresholds

| Threshold | Value | Meaning |
|-----------|-------|---------|
| `psi_warning_threshold` | 0.10 | Per-feature warning |
| `psi_drift_threshold` | 0.25 | Severe drift threshold |
| `feature_drift_warning_pct` | 0.20 | % of drifted features triggering warning |
| `reference_window_size` | 100 | Baseline distribution samples |
| `monitoring_window_size` | 50 | Current window samples |
| `accuracy_degradation_threshold` | 0.10 | 10% accuracy drop = significant |

### Drift Severity Levels

```python
CRITICAL: avg_psi > 0.25 OR >50% features drifted → "Immediate retraining required"
WARNING:  avg_psi > 0.10 OR >20% features drifted → "Monitor closely"
STABLE:   otherwise → "No action required"
```

User-level drift detection compares current feature Z-scores against baseline statistics. Z-score > 3.0 flags a feature as drifted.

## Caching Strategy

| Cache | TTL | Max Size | Key |
|-------|-----|----------|-----|
| User models | 3600s (1h) | 100 | `user_id` |
| Behavioral profiles | 1800s (30min) | 1000 | `user_id` |

Both caches use LRU-style eviction: oldest entry removed when capacity reached.

## Model Evaluation (`ml/evaluation.py`)

The `Evaluator` class provides comprehensive model assessment:

- `evaluate_binary(...)`: accuracy, F1, precision, recall, MCC, ROC-AUC, avg precision, confusion matrix
- `cross_validate(...)`: stratified K-fold cross-validation
- `compare_models(...)`: statistical significance testing (t-test, Wilcoxon, Mann-Whitney)
- `permutation_feature_importance(...)`: permutation-based feature importance
- `find_optimal_threshold(...)`: Youden's J, closest-to-(0,1), F1-maximizing threshold

## Performance Characteristics

| Component | Average Latency | Memory | Notes |
|-----------|----------------|--------|-------|
| Feature extraction (36 features) | ~15ms | ~1MB | Per session of ~200 events |
| User model inference | ~3ms | Model: ~500KB | Isolation Forest single sample |
| Global model inference (10 estimators) | ~20ms | Model: ~5MB | Ensemble prediction |
| Risk engine evaluation | ~1ms | ~100KB | Pure arithmetic |
| User model training (100 samples) | ~2s | ~10MB | IForest fit |
| Global model training (1000 samples) | ~30s | ~100MB | 10× subsampled IForest |
| Full explainability | ~5ms | ~500KB | Feature impact + template generation |
