from __future__ import annotations

import argparse
import sys

from .analyze import analyze
from .parser import parse_lines
from .rates import bin_counts, window_start


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="poisson-log-analyzer",
        description="Detect request-rate spikes and sustained shifts in a web server access log.",
    )
    ap.add_argument("logfile", help="access log (common/combined format)")
    ap.add_argument("--window", type=int, default=60, help="window width in seconds")
    ap.add_argument(
        "--alpha",
        type=float,
        default=0.01,
        help="overall false-alarm level, split equally between the spike and sustained-shift tests",
    )
    args = ap.parse_args(argv)

    skipped = 0

    def count_skip(_line: str) -> None:
        nonlocal skipped
        skipped += 1

    with open(args.logfile, encoding="utf-8", errors="replace") as f:
        entries = list(parse_lines(f, on_skip=count_skip))
    if skipped:
        print(f"warning: {skipped} line(s) could not be parsed and were skipped", file=sys.stderr)
    if not entries:
        print("No valid log lines found.", file=sys.stderr)
        return 1

    start, counts = bin_counts((e.timestamp for e in entries), args.window)
    analysis = analyze(counts, alpha=args.alpha)
    result = analysis.spikes
    print(f"{len(entries)} requests, {len(counts)} windows of {args.window}s")
    print(f"baseline rate: {result.rate:.2f} req/window, dispersion: {result.dispersion:.2f}")
    if not result.flagged:
        print("no spikes detected")
    for i in result.flagged:
        t = window_start(start, i, args.window).isoformat()
        print(f"SPIKE {t}  count={counts[i]}  q={result.q_values[i]:.3g}")
    if analysis.sustained:
        run = analysis.run
        first = window_start(start, run.start, args.window).isoformat()
        last = window_start(start, run.stop - 1, args.window).isoformat()
        print(f"SUSTAINED {first} .. {last}  windows={run.length}  p={run.p_value:.3g}")
    else:
        print("no sustained shift detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
