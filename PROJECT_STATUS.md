# Project Status

**Last Updated**: 2026-11-23

## 🎯 Current Task

Working on: Experiments in notebooks. Evaluating the longest-run distribution (Schilling 1990) as a complement to the count test
Next: Decide whether to add a `runs` module (exact distribution + run test) to the package, and use a detected run to trigger the baseline re-fit
See: `notebooks/longest_run.ipynb`, `src/poisson_log_analyzer/detect.py`

---

## 🎯 Recent Work

- 2026-11-23: Added `notebooks/longest_run.ipynb`. The exact longest-run distribution reproduces Table 2 of Schilling (1990). On 120-window Poisson(8) series, a run test (windows above the median) catches long modest bursts that the count test misses, and stays near its nominal level under over-dispersed traffic where the count test raises many false alarms. It is blind to short tall bursts, so the two tests complement each other. Reference PDF: `Dropbox\MOLASS\References\1990, M. F. Schilling.pdf` (scanned, no text layer).
- 2026-11-23: Adopted the AI Context Standard (this file and `.github/copilot-instructions.md`).
- 2026-11-23: Added `notebooks/how_it_works.ipynb` — bilingual (EN/JA), interactive explanation for non-statisticians.
- 2026-11-23: Added `notebooks/traffic_spike_demo.ipynb` — end-to-end demo with a synthetic log and a spike plot; added the `notebook` extra in `pyproject.toml`.

## ⏳ Next Steps

1. Decide on a `runs` module (exact longest-run distribution, run test) and a combined count + run detector.
2. Roadmap items in `README.md` (seasonality, negative binomial fallback, per-IP/path/status rates, dips; runs below the median also cover dips).

## ⚠️ Known Issues

- The baseline re-fit in `detect_spikes` only excludes windows flagged on the first pass. A long, modest burst that is never flagged keeps the baseline inflated, so it goes undetected. `notebooks/longest_run.ipynb` shows the run test catches these cases.

## 📊 Status Summary

Core pipeline (parser, window counts, spike detection, CLI) works; 6 tests pass.
