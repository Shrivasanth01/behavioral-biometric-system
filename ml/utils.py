import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Tuple
from scipy import stats
import hashlib
import json


def normalize_feature(
    value: float,
    mean: float,
    std: float,
    eps: float = 1e-8,
    method: str = "zscore",
) -> float:
    if std < eps:
        return 0.0
    if method == "zscore":
        return (value - mean) / std
    elif method == "minmax":
        return value
    return (value - mean) / std


def robust_normalize(
    values: np.ndarray,
    method: str = "robust",
) -> np.ndarray:
    if len(values) == 0:
        return np.array([])
    arr = np.asarray(values, dtype=np.float64)
    if method == "zscore":
        mean = np.nanmean(arr)
        std = np.nanstd(arr)
        return np.where(std > 1e-8, (arr - mean) / std, np.zeros_like(arr))
    elif method == "minmax":
        mn, mx = np.nanmin(arr), np.nanmax(arr)
        return np.where((mx - mn) > 1e-8, (arr - mn) / (mx - mn), np.zeros_like(arr))
    elif method == "robust":
        median = np.nanmedian(arr)
        iqr = np.nanpercentile(arr, 75) - np.nanpercentile(arr, 25)
        return np.where(iqr > 1e-8, (arr - median) / iqr, np.zeros_like(arr))
    return arr


def validate_events(events: List[Dict]) -> bool:
    if not isinstance(events, list) or len(events) == 0:
        return False
    required_keys = {"type", "timestamp"}
    for ev in events:
        if not isinstance(ev, dict):
            return False
        if not required_keys.issubset(ev.keys()):
            return False
    return True


def preprocess_events(events: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(events)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp").reset_index(drop=True)
    if df.empty:
        return df
    df = df.replace([np.inf, -np.inf], np.nan)
    return df


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator is None or abs(denominator) < 1e-12:
        return default
    return numerator / denominator


def compute_entropy(counts: np.ndarray, base: Optional[float] = None) -> float:
    counts = np.asarray(counts, dtype=np.float64)
    if counts.sum() == 0:
        return 0.0
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    if base is None:
        base = np.e
    return -np.sum(probs * np.log(probs) / np.log(base))


def compute_kl_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-10) -> float:
    p = np.asarray(p, dtype=np.float64) + eps
    q = np.asarray(q, dtype=np.float64) + eps
    p = p / p.sum()
    q = q / q.sum()
    return np.sum(p * np.log(p / q))


def compute_psi(expected: np.ndarray, actual: np.ndarray, n_bins: int = 10) -> float:
    expected = np.asarray(expected, dtype=np.float64)
    actual = np.asarray(actual, dtype=np.float64)
    if len(expected) == 0 or len(actual) == 0:
        return 0.0
    bins = np.linspace(0, 100, n_bins + 1)
    expected_pct = np.histogram(expected, bins=bins)[0].astype(np.float64)
    actual_pct = np.histogram(actual, bins=bins)[0].astype(np.float64)
    expected_pct = (expected_pct / expected_pct.sum()).clip(1e-5, None)
    actual_pct = (actual_pct / actual_pct.sum()).clip(1e-5, None)
    return np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))


def compute_mad(values: np.ndarray) -> float:
    arr = np.asarray(values, dtype=np.float64)
    if len(arr) == 0:
        return 0.0
    median = np.nanmedian(arr)
    return float(np.nanmedian(np.abs(arr - median)))


def compute_weighted_percentile(
    data: np.ndarray,
    weights: Optional[np.ndarray] = None,
    percentile: float = 50.0,
) -> float:
    data = np.asarray(data, dtype=np.float64)
    if len(data) == 0:
        return 0.0
    if weights is None:
        return float(np.nanpercentile(data, percentile))
    weights = np.asarray(weights, dtype=np.float64)
    order = np.argsort(data)
    data_sorted = data[order]
    weights_sorted = weights[order]
    cumsum = np.cumsum(weights_sorted)
    cumsum_pct = cumsum / cumsum[-1]
    idx = np.searchsorted(cumsum_pct, percentile / 100.0)
    return float(data_sorted[min(idx, len(data_sorted) - 1)])


def device_fingerprint(device_info: Dict) -> str:
    raw = json.dumps(device_info, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def exponential_moving_average(
    series: np.ndarray,
    alpha: float = 0.3,
) -> np.ndarray:
    arr = np.asarray(series, dtype=np.float64)
    result = np.zeros_like(arr)
    if len(arr) == 0:
        return result
    result[0] = arr[0]
    for i in range(1, len(arr)):
        result[i] = alpha * arr[i] + (1 - alpha) * result[i - 1]
    return result


def time_since_last_event(timestamps: List[float]) -> float:
    if len(timestamps) < 2:
        return 0.0
    return timestamps[-1] - timestamps[-2]


def event_rate(timestamps: List[float]) -> float:
    if len(timestamps) < 2:
        return 0.0
    duration = timestamps[-1] - timestamps[0]
    if duration <= 0:
        return 0.0
    return len(timestamps) / duration


def percentile_bucket(value: float, buckets: List[float]) -> int:
    for i, b in enumerate(buckets):
        if value <= b:
            return i
    return len(buckets)


def safe_log(x: float, eps: float = 1e-10) -> float:
    return np.log(max(x, eps))


def discretize_angle(angle_deg: float, n_bins: int = 8) -> int:
    angle_deg = angle_deg % 360.0
    bin_size = 360.0 / n_bins
    return int(angle_deg // bin_size) % n_bins


def compute_cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64).flatten()
    b = np.asarray(b, dtype=np.float64).flatten()
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
