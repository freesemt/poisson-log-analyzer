# poisson-log-analyzer

Detect traffic spikes in web server access logs using a Poisson model of request rates.

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
