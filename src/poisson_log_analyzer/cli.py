from __future__ import annotations

import argparse
import sys

from .detect import detect_spikes
from .parser import parse_lines
from .rates import bin_counts, window_start


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="poisson-log-analyzer",
        description="Detect request-rate spikes in a web server access log.",
    )
    ap.add_argument("logfile", help="access log (common/combined format)")
    ap.add_argument("--window", type=int, default=60, help="window width in seconds")
    ap.add_argument("--alpha", type=float, default=0.01, help="FDR level")
    args = ap.parse_args(argv)

    with open(args.logfile, encoding="utf-8", errors="replace") as f:
        entries = list(parse_lines(f))
    if not entries:
        print("No valid log lines found.", file=sys.stderr)
        return 1

    start, counts = bin_counts((e.timestamp for e in entries), args.window)
    result = detect_spikes(counts, alpha=args.alpha)
    print(f"{len(entries)} requests, {len(counts)} windows of {args.window}s")
    print(f"baseline rate: {result.rate:.2f} req/window, dispersion: {result.dispersion:.2f}")
    if not result.flagged:
        print("no spikes detected")
    for i in result.flagged:
        t = window_start(start, i, args.window).isoformat()
        print(f"SPIKE {t}  count={counts[i]}  q={result.q_values[i]:.3g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
