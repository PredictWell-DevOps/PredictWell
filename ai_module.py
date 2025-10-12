# backend/ai_module.py — Risk math utilities (pure functions)

from __future__ import annotations
from typing import List, Tuple
import numpy as np

# Model weights and risk bands
WEIGHTS = {
    "recent_fall":        0.25,
    "dizziness":          0.12,
    "orthostatic_drop":   0.12,
    "steps_delta":        0.16,  # down vs personal baseline
    "sleep_frag":         0.10,
    "gait_flag":          0.10,
    "med_change":         0.10,
    "hydration_low":      0.05,
}

BANDS: List[Tuple[float, float, str]] = [
    (0.00, 0.29, "Low"),
    (0.30, 0.59, "Moderate"),
    (0.60, 1.00, "High"),
]

def band_for(score: float) -> str:
    for lo, hi, name in BANDS:
        if lo <= score <= hi:
            return name
    return "Unknown"

def ema(series: List[float], alpha: float = 0.4):
    """Exponential moving average (None if empty)."""
    if not series:
        return None
    v = series[0]
    for x in series[1:]:
        v = alpha * x + (1 - alpha) * v
    return v

def ols_forecast(y: List[float], steps_ahead: int = 4):
    """
    Linear trend forecast with simple ~90% bands from residual RMSE.
    All values are clipped to [0,1] since score is normalized.
    """
    n = len(y)
    if n < 3:
        pred = [y[-1]] * steps_ahead
        low  = [max(0, y[-1] - 0.10)] * steps_ahead
        high = [min(1, y[-1] + 0.10)] * steps_ahead
        return pred, low, high

    x = np.arange(n)
    A = np.vstack([x, np.ones(n)]).T
    m, b = np.linalg.lstsq(A, y, rcond=None)[0]
    residuals = y - (m * x + b)
    rmse = float(np.sqrt(np.mean(residuals ** 2))) if n > 2 else 0.10

    preds, lows, highs = [], [], []
    for k in range(1, steps_ahead + 1):
        t = (n - 1) + k
        p = float(m * t + b)
        p = max(0.0, min(1.0, p))
        preds.append(p)
        lows.append(max(0.0, min(1.0, p - 1.64 * rmse)))
        highs.append(max(0.0, min(1.0, p + 1.64 * rmse)))
    return preds, lows, highs

def cusum(values: List[float], k: float = 0.03, h: float = 0.12) -> bool:
    """Detect small persistent upward drift; returns True if drift detected."""
    if len(values) < 4:
        return False
    s_pos = 0.0
    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        s_pos = max(0.0, s_pos + (diff - k))
        if s_pos > h:
            return True
    return False
