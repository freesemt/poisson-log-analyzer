"""Turn timestamps into request counts per fixed-width time window."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Tuple

import numpy as np


def bin_counts(
    timestamps: Iterable[datetime], window_seconds: int = 60
) -> Tuple[datetime, np.ndarray]:
    """Count events per window, including empty windows.

    Returns ``(start, counts)`` where window ``i`` covers
    ``[start + i*w, start + (i+1)*w)``. ``start`` is the first timestamp
    floored to a multiple of the window width (epoch-aligned).
    """
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    ts = sorted(timestamps)
    if not ts:
        raise ValueError("no timestamps given")
    epoch = [t.timestamp() for t in ts]
    first = int(epoch[0] // window_seconds) * window_seconds
    idx = ((np.asarray(epoch) - first) // window_seconds).astype(int)
    counts = np.bincount(idx, minlength=int(idx[-1]) + 1)
    start = datetime.fromtimestamp(first, tz=ts[0].tzinfo)
    return start, counts


def window_start(start: datetime, index: int, window_seconds: int) -> datetime:
    return start + timedelta(seconds=index * window_seconds)
