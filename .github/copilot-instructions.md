<!-- AI Context Standard v0.10.3 - Adopted: 2026-11-23 -->
# AI Assistant Initialization Guide — poisson-log-analyzer

> **On every session start**: Read [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) to get the current task and recent context before responding.

## Repository Context

Detects traffic spikes in Apache/Nginx access logs: requests are counted per fixed time window, a baseline Poisson rate λ is fitted robustly, and windows with improbably high counts are flagged (Benjamini–Hochberg FDR). See [README.md](../README.md) for the method and roadmap.

Standard: https://github.com/freesemt/ai-context-standard (context lives in the repo, not in personal AI memory).

## Structure

- `src/poisson_log_analyzer/` — `parser.py` (log lines), `rates.py` (window counts), `detect.py` (spike count test), `runs.py` (longest-run test, Schilling 1990), `analyze.py` (both tests), `cli.py`
- `tests/` — pytest suite (`test_pipeline.py`, `test_runs.py`; the run-length DP is checked against brute-force enumeration and the paper's tables)
- `.github/workflows/tests.yml` — CI: pytest on Python 3.9–3.13
- `notebooks/` — experiments and explanations (`traffic_spike_demo.ipynb`, `how_it_works.ipynb`, `longest_run.ipynb`, `change_points.ipynb`); notebooks import the package instead of redefining its code, except experiments that are not packaged yet (`change_points.ipynb`)

## Working Conventions

- Python ≥ 3.9, `src/` layout. Install with `pip install -e ".[dev]"` (add `.[notebook]` for notebooks); run `pytest` (it finds `src/` itself).
- Keep changes small and tested; the pipeline is `parse_lines` → `bin_counts` → `analyze` (`detect_spikes` + `run_test`). Keep the code compatible with Python 3.9 (CI runs 3.9–3.13).
- Statistical code is tested against an independent reference (brute-force enumeration, a published table) before it is trusted; do not leave the only copy of such code in a notebook.
- Notebooks: committed **with** outputs (they are small, and visible results help beginners); keep outputs small and re-run before committing. Explanations for non-experts are bilingual (English and Japanese); plot labels stay English. Experiment notebooks may be English only. Notebook conventions: https://github.com/freesemt/ai-context-standard/blob/main/NOTEBOOK_CONVENTIONS.md (the human selects the kernel).
- Windows PowerShell: terminal quirks for `git`/`gh` are in https://github.com/freesemt/ai-context-standard/blob/main/TERMINAL_CONVENTIONS.md — read before committing.
- If the same operation fails 3+ times, stop and explain to the user instead of retrying.
- Update `PROJECT_STATUS.md` at the end of each work session.
