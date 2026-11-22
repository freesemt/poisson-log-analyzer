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

## Usage

```powershell
pip install -e .[dev]
poisson-log-analyzer access.log --window 60 --alpha 0.01
pytest
```

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

```python
from poisson_log_analyzer import parse_lines, bin_counts, detect_spikes

entries = parse_lines(open("access.log"))
start, counts = bin_counts(e.timestamp for e in entries)
result = detect_spikes(counts, alpha=0.01)
result.flagged, result.rate, result.dispersion
```

Supported input: Apache/Nginx common and combined log formats.

## Roadmap

- Time-of-day / weekly seasonality (non-homogeneous Poisson rate)
- Negative binomial fallback for over-dispersed traffic
- Per-IP, per-path and per-status (e.g. 4xx/5xx) rates
- Dips (unusually low traffic) as well as spikes
