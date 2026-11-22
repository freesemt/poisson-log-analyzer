"""Poisson-based spike detection on per-window request counts.

Model: under normal traffic the count in each window is Poisson(lambda).
A window with count k is anomalous when P(X >= k | lambda) is small. The
baseline lambda is estimated robustly by re-fitting after excluding flagged
windows, and p-values are corrected for multiple testing (Benjamini-Hochberg).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from scipy.stats import poisson


@dataclass(frozen=True)
class SpikeResult:
    rate: float  # baseline events per window
    p_values: np.ndarray  # P(X >= count) per window
    q_values: np.ndarray  # BH-adjusted p-values
    flagged: List[int]  # window indices with q <= alpha
    dispersion: float  # variance/mean of baseline windows; ~1 if Poisson fits


def _upper_tail(counts: np.ndarray, rate: float) -> np.ndarray:
    if rate <= 0:
        return np.where(counts > 0, 0.0, 1.0)
    return poisson.sf(counts - 1, rate)


def _benjamini_hochberg(p: np.ndarray) -> np.ndarray:
    n = len(p)
    order = np.argsort(p)
    scaled = p[order] * n / np.arange(1, n + 1)
    q_sorted = np.minimum.accumulate(scaled[::-1])[::-1]
    q = np.empty(n)
    q[order] = np.minimum(q_sorted, 1.0)
    return q


def detect_spikes(
    counts: np.ndarray, alpha: float = 0.01, max_iter: int = 10
) -> SpikeResult:
    """Flag windows whose counts are improbably high under a Poisson baseline."""
    counts = np.asarray(counts, dtype=int)
    if counts.size == 0:
        raise ValueError("counts is empty")
    mask = np.ones(counts.size, dtype=bool)  # windows used for the baseline
    for _ in range(max_iter):
        rate = float(counts[mask].mean())
        q = _benjamini_hochberg(_upper_tail(counts, rate))
        new_mask = q > alpha
        if new_mask.sum() == 0 or np.array_equal(new_mask, mask):
            break
        mask = new_mask
    rate = float(counts[mask].mean())
    p = _upper_tail(counts, rate)
    q = _benjamini_hochberg(p)
    base = counts[mask]
    dispersion = float(base.var(ddof=1) / base.mean()) if base.size > 1 and base.mean() > 0 else float("nan")
    return SpikeResult(rate, p, q, [int(i) for i in np.flatnonzero(q <= alpha)], dispersion)
