from .analyze import Analysis, analyze
from .detect import SpikeResult, detect_spikes
from .parser import LogEntry, parse_line, parse_lines
from .rates import bin_counts
from .runs import RunResult, longest_run_pvalue, run_test

__all__ = [
    "Analysis",
    "LogEntry",
    "RunResult",
    "SpikeResult",
    "analyze",
    "bin_counts",
    "detect_spikes",
    "longest_run_pvalue",
    "parse_line",
    "parse_lines",
    "run_test",
]
__version__ = "0.1.0"
