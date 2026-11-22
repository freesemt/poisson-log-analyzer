import itertools

import numpy as np
import pytest

from poisson_log_analyzer import analyze, longest_run_pvalue, run_test
from poisson_log_analyzer.runs import longest_run


def _brute_force_tail(n, p):
    """P(longest run >= r) for r = 0..n+1, by enumerating all 2**n sequences."""
    tail = np.zeros(n + 2)
    for seq in itertools.product((0, 1), repeat=n):
        k = sum(seq)
        length, _ = longest_run(seq)
        tail[: length + 1] += p**k * (1 - p) ** (n - k)
    return tail


@pytest.mark.parametrize("n", [1, 2, 5, 9, 12])
@pytest.mark.parametrize("p", [0.1, 0.5, 0.8])
def test_longest_run_pvalue_matches_brute_force(n, p):
    expected = _brute_force_tail(n, p)
    for r in range(n + 2):
        assert longest_run_pvalue(n, r, p) == pytest.approx(expected[r], abs=1e-12)


def test_longest_run_pvalue_matches_schilling_paper():
    # Fair coin, n = 3: the table on p. 197.
    assert [longest_run_pvalue(3, r, 0.5) for r in range(4)] == pytest.approx([1, 7 / 8, 3 / 8, 1 / 8])
    # Fair coin, n = 200: exact column of Table 2 (rounded to 3 decimals in the paper).
    pmf = lambda x: longest_run_pvalue(200, x, 0.5) - longest_run_pvalue(200, x + 1, 0.5)
    assert 1 - longest_run_pvalue(200, 4, 0.5) == pytest.approx(0.001, abs=6e-4)
    for x, paper in {4: 0.033, 5: 0.165, 6: 0.257, 7: 0.224, 8: 0.146, 12: 0.011}.items():
        assert pmf(x) == pytest.approx(paper, abs=6e-4)
    assert longest_run_pvalue(200, 13, 0.5) == pytest.approx(0.012, abs=6e-4)


def test_longest_run_pvalue_edge_cases():
    assert longest_run_pvalue(10, 0, 0.3) == 1.0
    assert longest_run_pvalue(10, 11, 0.3) == 0.0
    assert longest_run_pvalue(10, 1, 0.0) == 0.0
    assert longest_run_pvalue(10, 10, 1.0) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        longest_run_pvalue(10, 2, 1.5)


def test_longest_run_reports_first_longest_run():
    assert longest_run([0, 1, 1, 0, 1, 1, 0]) == (2, 1)
    assert longest_run([0, 0]) == (0, None)


def test_run_test_flags_long_modest_burst_that_count_test_misses():
    counts = np.random.default_rng(3).poisson(8, 120)
    counts[40:70] += 6
    result = run_test(counts)
    assert result.p_value < 1e-3
    assert result.length >= 15 and 35 <= result.start and result.stop <= 75
    assert not analyze(counts).spikes.flagged


@pytest.mark.parametrize("rate", [0.5, 2.5, 8])
def test_run_test_false_alarm_rate_stays_near_level(rate):
    rng = np.random.default_rng(0)
    hits = sum(run_test(rng.poisson(rate, 120)).p_value < 0.01 for _ in range(300))
    assert hits / 300 <= 0.03


def test_run_test_degenerate_inputs():
    flat = run_test([7] * 20)
    assert (flat.length, flat.start, flat.stop, flat.p_value) == (0, None, None, 1.0)
    sparse = run_test(np.array([0] * 50 + [1] * 3 + [0] * 50))  # median is 0
    assert 0.0 <= sparse.p_value <= 1.0
    with pytest.raises(ValueError):
        run_test([])


def test_run_test_p_high_override():
    counts = np.random.default_rng(3).poisson(8, 120)
    counts[40:70] += 6
    assert run_test(counts, p_high=0.9).p_value > run_test(counts).p_value


def test_analyze_separates_spike_from_sustained_shift():
    tall = np.random.default_rng(0).poisson(20, 300)
    tall[150] = 90
    a = analyze(tall)
    assert a.spikes.flagged == [150] and not a.sustained

    modest = np.random.default_rng(3).poisson(8, 120)
    modest[40:70] += 6
    assert analyze(modest).sustained
