# poisson-log-analyzer

Detect traffic spikes in web server access logs using a Poisson model of request rates.

> **For AI assistants (GitHub Copilot)**: Context is loaded automatically from `.github/copilot-instructions.md`; current state is in `PROJECT_STATUS.md`.

## Idea

Under normal traffic, the number of requests in a fixed time window is approximately
Poisson(λ). For each window with count *k* we compute the upper-tail probability
P(X ≥ k | λ). Windows with very small probability are anomalies.

- **Baseline λ** is fitted robustly: windows flagged as spikes are excluded and λ is re-fitted until stable.
- **Multiple testing** across windows is controlled with Benjamini–Hochberg FDR.
- **Dispersion index** (variance/mean of baseline windows) checks the Poisson assumption; values well above 1 mean the traffic is over-dispersed and p-values are too optimistic.
- **Sustained shifts.** The count test judges each window alone, so a long but modest elevation can slip through. A second test marks each window as above or below the median and asks whether the longest run of "above" windows is too long for independent windows, using the exact distribution of Schilling (1990). It is robust to over-dispersion. The CLI runs both tests, each at α/2.

## Usage

```powershell
pip install -e .[dev]
poisson-log-analyzer access.log --window 60 --alpha 0.01
pytest
```

Example output (`SPIKE` = single windows with improbably high counts, `SUSTAINED` = longest run of above-median windows):

```text
warning: 1 line(s) could not be parsed and were skipped
1110 requests, 120 windows of 60s
baseline rate: 9.25 req/window, dispersion: 1.40
no spikes detected
SUSTAINED 2025-01-01T00:54:00+00:00 .. 2025-01-01T01:09:00+00:00  windows=16  p=0.000165
```

Lines that cannot be parsed are counted and reported on stderr. Requests with an empty or malformed request line (HTTP 400/408) are kept as requests with method and path `-`.

```python
from poisson_log_analyzer import parse_lines, bin_counts, analyze

entries = parse_lines(open("access.log"))
start, counts = bin_counts(e.timestamp for e in entries)
result = analyze(counts, alpha=0.01)
result.spikes.flagged, result.spikes.rate, result.spikes.dispersion
result.sustained, result.run.start, result.run.length, result.run.p_value
```

Supported input: Apache/Nginx common and combined log formats.

## Notebook experiments

Install the notebook dependencies and open the starter visualization in Jupyter
or VS Code:

```powershell
pip install -e ".[notebook]"
jupyter notebook notebooks/traffic_spike_demo.ipynb
```

The notebook generates a reproducible sample access log, parses and analyzes it,
and plots request counts with detected spikes highlighted. Replace its sample
log-generation cell with your own log lines to explore real data.

[`notebooks/how_it_works.ipynb`](notebooks/how_it_works.ipynb) explains the method
for readers without a statistics background, in English and Japanese, with
interactive sliders (λ, p-values, multiple-testing false alarms, baseline re-fitting,
dispersion, and the real pipeline).

[`notebooks/longest_run.ipynb`](notebooks/longest_run.ipynb) is the experiment behind the
sustained-shift test: the exact longest-run distribution checked against Schilling's
Table 2, detection power and false alarms compared with the count test.

[`notebooks/change_points.ipynb`](notebooks/change_points.ipynb) explores change-point detection
(exact Poisson segmentation with a dispersion-scaled penalty): where a shift starts and ends,
repairing the baseline, and why a daily cycle breaks it. Not yet part of the package.

## Roadmap

- Time-of-day / weekly seasonality (non-homogeneous Poisson rate); the run test also needs it, since a daily cycle produces long runs
- Negative binomial fallback for over-dispersed traffic
- Per-IP, per-path and per-status (e.g. 4xx/5xx) rates
- Dips (unusually low traffic) as well as spikes, e.g. runs below the median
- Seed the baseline re-fit with the run test's window set
