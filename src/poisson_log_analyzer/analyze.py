"""Combined analysis: isolated spikes (count test) and sustained shifts (run test)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detect import SpikeResult, detect_spikes
from .runs import RunResult, run_test


@dataclass(frozen=True)
class Analysis:
    spikes: SpikeResult
    run: RunResult
    alpha: float  # overall false-alarm level, split equally between the two tests

    @property
    def sustained(self) -> bool:
        return self.run.p_value <= self.alpha / 2


def analyze(counts: np.ndarray, alpha: float = 0.01) -> Analysis:
    """Run both tests, each at ``alpha / 2`` so that the combined false-alarm rate stays near ``alpha``."""
    counts = np.asarray(counts, dtype=int)
    return Analysis(detect_spikes(counts, alpha=alpha / 2), run_test(counts), alpha)
