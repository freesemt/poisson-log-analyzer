# Project Status

**Last Updated**: 2026-11-23

## 🎯 Current Task

Working on: Experiments in notebooks (starting from the two notebooks in `notebooks/`)
Next: Decide the first experiment, e.g. making the baseline re-fit robust to a long, modest burst (see Known Issues)
See: `notebooks/how_it_works.ipynb`, `src/poisson_log_analyzer/detect.py`

---

## 🎯 Recent Work

- 2026-11-23: Adopted the AI Context Standard (this file and `.github/copilot-instructions.md`).
- 2026-11-23: Added `notebooks/how_it_works.ipynb` — bilingual (EN/JA), interactive explanation for non-statisticians.
- 2026-11-23: Added `notebooks/traffic_spike_demo.ipynb` — end-to-end demo with a synthetic log and a spike plot; added the `notebook` extra in `pyproject.toml`.

## ⏳ Next Steps

1. Pick the first notebook experiment.
2. Roadmap items in `README.md` (seasonality, negative binomial fallback, per-IP/path/status rates, dips).

## ⚠️ Known Issues

- The baseline re-fit in `detect_spikes` only excludes windows flagged on the first pass. A long, modest burst that is never flagged keeps the baseline inflated, so it goes undetected.

## 📊 Status Summary

Core pipeline (parser, window counts, spike detection, CLI) works; 6 tests pass.
