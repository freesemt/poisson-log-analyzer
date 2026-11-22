"""Longest-run test for sustained shifts in request counts.

Mark each window "high" when its count is above the median. If windows are
independent, the marks behave like biased coin flips, so a long run of "high"
windows is unlikely (Schilling, 1990). This catches long, modest elevations that
the per-window Poisson count test cannot see.

Reference: M. F. Schilling, "The Longest Run of Heads", The College Mathematics
Journal 21(3), 196-207 (1990).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

import numpy as np


def longest_run_pvalue(n: int, length: int, p: float) -> float:
    """Exact P(longest run of successes >= length) in n independent Bernoulli(p) trials.

    The state is the current run length, so the cost is O(n * length) and any
    0 <= p <= 1 is valid.
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be between 0 and 1")
    if length <= 0:
        return 1.0
    if length > n:
        return 0.0
    state = np.zeros(length)  # state[j]: current run is j long and no run of `length` yet
    state[0] = 1.0
    hit = 0.0
    for _ in range(n):
        hit += state[-1] * p
        new = np.empty(length)
        new[0] = state.sum() * (1 - p)
        new[1:] = state[:-1] * p
        state = new
    return min(hit, 1.0)


def longest_run(flags: Iterable[bool]) -> Tuple[int, Optional[int]]:
    """Return ``(length, start)`` of the first longest run of True values (start is None if none)."""
    best = best_end = current = 0
    for i, flag in enumerate(flags):
        current = current + 1 if flag else 0
        if current > best:
            best, best_end = current, i
    return best, (best_end - best + 1 if best else None)


@dataclass(frozen=True)
class RunResult:
    length: int  # longest run of windows above the median
    start: Optional[int]  # first window index of that run (None if length is 0)
    p_value: float  # P(longest run >= length) if windows were independent
    p_high: float  # probability that a window is above the median under the null

    @property
    def stop(self) -> Optional[int]:
        """Window index just after the run (None if there is no run)."""
        return None if self.start is None else self.start + self.length


def run_test(counts: np.ndarray, p_high: Optional[float] = None) -> RunResult:
    """Test for a sustained shift: is the longest run of above-median windows too long?

    ``p_high`` is the null probability that a window is above the median. By
    default it is the observed share of such windows, which needs no Poisson
    assumption and stays valid for over-dispersed traffic. Deriving it from a
    Poisson rate at the median instead is liberal when the rate is small.
    """
    counts = np.asarray(counts)
    if counts.size == 0:
        raise ValueError("counts is empty")
    above = counts > np.median(counts)
    if p_high is None:
        p_high = float(above.mean())
    length, start = longest_run(above)
    if not 0.0 < p_high < 1.0:
        return RunResult(length, start, 1.0, float(p_high))
    return RunResult(length, start, longest_run_pvalue(counts.size, length, p_high), float(p_high))
