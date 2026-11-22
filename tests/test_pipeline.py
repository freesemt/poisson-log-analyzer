from datetime import datetime, timedelta, timezone

import numpy as np

from poisson_log_analyzer import bin_counts, detect_spikes, parse_line, parse_lines
from poisson_log_analyzer.cli import main

LINE = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /a.gif HTTP/1.0" 200 2326 "-" "curl"'


def test_parse_line_combined_and_dash_size():
    e = parse_line(LINE)
    assert (e.ip, e.method, e.path, e.status, e.size) == ("127.0.0.1", "GET", "/a.gif", 200, 2326)
    assert parse_line(LINE.replace("2326", "-")).size == 0


def test_parse_line_keeps_requestless_and_malformed_requests():
    timeout = parse_line(LINE.replace('"GET /a.gif HTTP/1.0" 200 2326', '"-" 408 -'))
    assert (timeout.method, timeout.path, timeout.status, timeout.size) == ("-", "-", 408, 0)
    binary = parse_line(LINE.replace('"GET /a.gif HTTP/1.0" 200 2326', r'"\x16\x03\x01" 400 150'))
    assert (binary.method, binary.path, binary.status) == ("-", "-", 400)


def test_parse_line_accepts_lowercase_method_and_escaped_quotes():
    assert parse_line(LINE.replace("GET", "get")).method == "GET"
    assert parse_line(LINE.replace("/a.gif", r"/a\"b.gif")).path == r"/a\"b.gif"


def test_parse_lines_skips_malformed():
    assert len(list(parse_lines([LINE, "garbage", ""]))) == 1


def test_parse_lines_reports_skipped_lines():
    skipped = []
    assert len(list(parse_lines([LINE, "garbage", "", "  "], on_skip=skipped.append))) == 1
    assert skipped == ["garbage"]


def test_bin_counts_includes_empty_windows():
    es = [parse_line(LINE.replace("13:55:36", t)) for t in ("13:55:10", "13:55:20", "13:57:05")]
    _, counts = bin_counts([e.timestamp for e in es], 60)
    assert counts.tolist() == [2, 0, 1]


def test_detects_injected_spike_only():
    rng = np.random.default_rng(0)
    counts = rng.poisson(20, 500)
    counts[250] = 90
    r = detect_spikes(counts, alpha=0.01)
    assert r.flagged == [250]
    assert abs(r.rate - 20) < 1.5
    assert 0.8 < r.dispersion < 1.25


def test_pure_poisson_has_few_false_alarms():
    counts = np.random.default_rng(1).poisson(5, 2000)
    assert len(detect_spikes(counts, alpha=0.01).flagged) <= 2


def test_cli_reports_spike(tmp_path, capsys):
    lines = []
    for minute in range(30):
        n = 80 if minute == 15 else 5
        for s in range(n):
            lines.append(LINE.replace("13:55:36", f"14:{minute:02d}:{s % 60:02d}"))
    log = tmp_path / "access.log"
    log.write_text("\n".join(lines), encoding="utf-8")
    assert main([str(log), "--window", "60"]) == 0
    out = capsys.readouterr().out
    assert "SPIKE" in out and "14:15" in out


def test_cli_reports_sustained_shift_and_skipped_lines(tmp_path, capsys):
    counts = np.random.default_rng(3).poisson(8, 120)
    counts[40:70] += 6
    base = datetime(2025, 1, 1, tzinfo=timezone.utc)
    lines = []
    for minute, n in enumerate(counts):
        for s in range(n):
            stamp = (base + timedelta(minutes=minute, seconds=s)).strftime("%d/%b/%Y:%H:%M:%S +0000")
            lines.append(LINE.replace("10/Oct/2000:13:55:36 -0700", stamp))
    lines.insert(5, "not a log line")
    log = tmp_path / "access.log"
    log.write_text("\n".join(lines), encoding="utf-8")
    assert main([str(log), "--window", "60"]) == 0
    captured = capsys.readouterr()
    assert "SUSTAINED 2025-01-01T00:" in captured.out
    assert "1 line(s) could not be parsed" in captured.err
