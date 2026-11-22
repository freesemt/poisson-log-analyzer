# Project Status

**Last Updated**: 2026-11-23

## 🎯 Current Task

Working on: Experiments in notebooks. The longest-run test (Schilling 1990) is now in the package and the CLI; next experiments build on it
Next: (1) use a detected run to seed the baseline re-fit, (2) dips / two-sided runs, (3) quantify how a daily cycle inflates run-test false alarms (seasonality)
See: `notebooks/longest_run.ipynb`, `src/poisson_log_analyzer/runs.py`, `src/poisson_log_analyzer/analyze.py`

---

## 🎯 Recent Work

- 2026-11-23: Longest-run test added to the package: `runs.py` (`longest_run_pvalue`, `run_test`), `analyze.py` (both tests, each at α/2), CLI prints `SUSTAINED` lines. The exact run-length DP is tested against brute-force enumeration for n ≤ 12 and against Schilling's Table 2. The null probability is the observed share of above-median windows: deriving it from Poisson(median) gave 7.3% false alarms at λ = 2.5 (nominal 1%), see Experiment C in `longest_run.ipynb`.
- 2026-11-23: Parser keeps request-less/malformed requests (HTTP 400/408 as method/path `-`), accepts lowercase methods and escaped quotes, and `parse_lines(on_skip=...)` lets the CLI report skipped lines on stderr.
- 2026-11-23: Housekeeping: `pythonpath = ["src"]` for pytest (works on a fresh checkout), GitHub Actions workflow running pytest on Python 3.9–3.13 (not yet seen running on GitHub).
- 2026-11-23: Added `notebooks/longest_run.ipynb`. The exact longest-run distribution reproduces Table 2 of Schilling (1990). On 120-window Poisson(8) series, a run test (windows above the median) catches long modest bursts that the count test misses, and stays near its nominal level under over-dispersed traffic where the count test raises many false alarms. It is blind to short tall bursts, so the two tests complement each other. Reference PDF: `Dropbox\MOLASS\References\1990, M. F. Schilling.pdf` (scanned, no text layer).
- 2026-11-23: Adopted the AI Context Standard (this file and `.github/copilot-instructions.md`).
- 2026-11-23: Added `notebooks/how_it_works.ipynb` — bilingual (EN/JA), interactive explanation for non-statisticians.
- 2026-11-23: Added `notebooks/traffic_spike_demo.ipynb` — end-to-end demo with a synthetic log and a spike plot; added the `notebook` extra in `pyproject.toml`.

## ⏳ Next Steps

1. Experiment: use a detected run to seed the baseline re-fit (so tall spikes inside a long burst are found too).
2. Experiment: dips / two-sided runs (CorMap-style same-sign runs).
3. Experiment: quantify how a daily cycle inflates run-test false alarms, then seasonality (roadmap in `README.md`; also negative binomial fallback, per-IP/path/status rates).

## ⚠️ Known Issues

- The baseline re-fit in `detect_spikes` only excludes windows flagged on the first pass. A long, modest burst that is never flagged keeps the baseline inflated; the count test misses it. The run test (`run_test`, reported as `SUSTAINED`) detects it but the baseline is not yet repaired from it.
- With very few windows the baseline can collapse onto one window (e.g. counts `[3, 40]` flag window 1); no minimum-window guard yet.
- The run test assumes independent windows: a daily cycle makes long above-median runs normal, so it needs seasonality handling on multi-day logs.

## 📊 Status Summary

Core pipeline (parser, window counts, spike test, run test, CLI) works; 35 tests pass; CI workflow added.
