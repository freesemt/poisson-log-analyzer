# Project Status

**Last Updated**: 2026-11-23

## 🎯 Current Task

Working on: Experiments in notebooks. Change-point detection (`notebooks/change_points.ipynb`) looks worth packaging; the run test is already in the package and the CLI
Next: (1) settle the open points in the change-point notebook (normal-level rule, dispersion estimator, penalty multiplier, PELT for long logs) and package it with tests, (2) estimate the seasonal profile from multi-day data and re-run Experiment C without the true profile, (3) report segments in the CLI
See: `notebooks/change_points.ipynb`, `notebooks/longest_run.ipynb`, `src/poisson_log_analyzer/runs.py`, `src/poisson_log_analyzer/analyze.py`

---

## 🎯 Recent Work

- 2026-11-23: Added `notebooks/change_points.ipynb` (not packaged yet). Exact Poisson optimal partitioning (checked against brute force on 135 series), penalty 1.5 × 2·ln(n) scaled by a robust dispersion estimate. Finds both edges of 10-window +6 bursts in 72% of series (`analyze()` detects 36%) and of 5-window +10 bursts in 93% (28%), start error 0.17 windows, burst-free false alarms 0.3%. Dispersion scaling is essential (70% false alarms at dispersion 3 without it). A baseline from the window-weighted median of segment rates repairs the Known Issue up to bursts of about 40% of the series (isolated +14 spikes found 47% vs 10%); the "longest segment" rule fails earlier, and "normal" is ambiguous at 50% or more. A daily cycle breaks it (about 6 false change points per 3 days) unless the profile is known (0 false, burst edges found 86%).
- 2026-11-23: Longest-run test added to the package: `runs.py` (`longest_run_pvalue`, `run_test`), `analyze.py` (both tests, each at α/2), CLI prints `SUSTAINED` lines. The exact run-length DP is tested against brute-force enumeration for n ≤ 12 and against Schilling's Table 2. The null probability is the observed share of above-median windows: deriving it from Poisson(median) gave 7.3% false alarms at λ = 2.5 (nominal 1%), see Experiment C in `longest_run.ipynb`.
- 2026-11-23: Parser keeps request-less/malformed requests (HTTP 400/408 as method/path `-`), accepts lowercase methods and escaped quotes, and `parse_lines(on_skip=...)` lets the CLI report skipped lines on stderr.
- 2026-11-23: Housekeeping: `pythonpath = ["src"]` for pytest (works on a fresh checkout), GitHub Actions workflow running pytest on Python 3.9–3.13 (runner pinned to `ubuntu-24.04`: `ubuntu-latest` is 26.04, which has no Python 3.9 build).
- 2026-11-23: Added `notebooks/longest_run.ipynb`. The exact longest-run distribution reproduces Table 2 of Schilling (1990). On 120-window Poisson(8) series, a run test (windows above the median) catches long modest bursts that the count test misses, and stays near its nominal level under over-dispersed traffic where the count test raises many false alarms. It is blind to short tall bursts, so the two tests complement each other. Reference PDF: `Dropbox\MOLASS\References\1990, M. F. Schilling.pdf` (scanned, no text layer).
- 2026-11-23: Adopted the AI Context Standard (this file and `.github/copilot-instructions.md`).
- 2026-11-23: Added `notebooks/how_it_works.ipynb` — bilingual (EN/JA), interactive explanation for non-statisticians.
- 2026-11-23: Added `notebooks/traffic_spike_demo.ipynb` — end-to-end demo with a synthetic log and a spike plot; added the `notebook` extra in `pyproject.toml`.

## ⏳ Next Steps

1. Package the change-point detector once its open points are settled (see the notebook's takeaways), with tests; report segments in the CLI.
2. Experiment: estimate the seasonal profile from multi-day data and re-run the daily-cycle experiment without the true profile (this also unblocks the run test on multi-day logs).
3. Experiment: dips / two-sided runs (CorMap-style same-sign runs); also roadmap items in `README.md` (negative binomial fallback, per-IP/path/status rates).

## ⚠️ Known Issues

- The baseline re-fit in `detect_spikes` only excludes windows flagged on the first pass. A long, modest burst that is never flagged keeps the baseline inflated; the count test misses it. The run test (`run_test`, reported as `SUSTAINED`) detects it; a baseline read off the change-point fit repairs it in the notebook experiment (`change_points.ipynb`) but is not in the package yet.
- With very few windows the baseline can collapse onto one window (e.g. counts `[3, 40]` flag window 1); no minimum-window guard yet.
- The run test assumes independent windows: a daily cycle makes long above-median runs normal, so it needs seasonality handling on multi-day logs.

## 📊 Status Summary

Core pipeline (parser, window counts, spike test, run test, CLI) works; 35 tests pass; CI passes on Python 3.9–3.13. Four notebooks (`traffic_spike_demo`, `how_it_works`, `longest_run`, `change_points`); the change-point detector exists only in its notebook and is not packaged or tested outside it.
