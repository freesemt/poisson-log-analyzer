<!-- AI Context Standard v0.10.3 - Adopted: 2026-11-23 -->
# AI Assistant Initialization Guide — poisson-log-analyzer

> **On every session start**: Read [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) to get the current task and recent context before responding.

## Repository Context

Detects traffic spikes in Apache/Nginx access logs: requests are counted per fixed time window, a baseline Poisson rate λ is fitted robustly, and windows with improbably high counts are flagged (Benjamini–Hochberg FDR). See [README.md](../README.md) for the method and roadmap.

Standard: https://github.com/freesemt/ai-context-standard (context lives in the repo, not in personal AI memory).

## Structure

- `src/poisson_log_analyzer/` — `parser.py` (log lines), `rates.py` (window counts), `detect.py` (spike detection), `cli.py`
- `tests/test_pipeline.py` — pytest suite
- `notebooks/` — experiments and explanations (`traffic_spike_demo.ipynb`, `how_it_works.ipynb`, `longest_run.ipynb`)

## Working Conventions

- Python ≥ 3.9, `src/` layout. Install with `pip install -e ".[dev]"` (add `.[notebook]` for notebooks); run `pytest`.
- Keep changes small and tested; the pipeline is `parse_lines` → `bin_counts` → `detect_spikes`.
- Notebooks: committed **with** outputs (they are small, and visible results help beginners); keep outputs small and re-run before committing. Explanations for non-experts are bilingual (English and Japanese); plot labels stay English. Experiment notebooks may be English only. Notebook conventions: https://github.com/freesemt/ai-context-standard/blob/main/NOTEBOOK_CONVENTIONS.md (the human selects the kernel).
- Windows PowerShell: terminal quirks for `git`/`gh` are in https://github.com/freesemt/ai-context-standard/blob/main/TERMINAL_CONVENTIONS.md — read before committing.
- If the same operation fails 3+ times, stop and explain to the user instead of retrying.
- Update `PROJECT_STATUS.md` at the end of each work session.
