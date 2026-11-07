import numpy as np
import pandas as pd
import pytest

from mr_scanner.indicators import (
    add_signals, crossover, crossunder, ema, mean_reversion_oscillator, rma, true_range,
)


def make_df(n=120, seed=1):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    high = close + rng.uniform(0.2, 1.5, n)
    low = close - rng.uniform(0.2, 1.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close})


def test_first_bar_true_range_is_high_minus_low():
    df = make_df()
    assert true_range(df).iloc[0] == pytest.approx(df["high"].iloc[0] - df["low"].iloc[0])


def test_rma_seed_is_sma_and_warmup_is_nan():
    s = pd.Series(np.arange(1.0, 31.0))
    r = rma(s, 14)
    assert r.iloc[:13].isna().all()
    assert r.iloc[13] == pytest.approx(s.iloc[:14].mean())
    assert r.iloc[14] == pytest.approx((s.iloc[14] + 13 * r.iloc[13]) / 14)


def test_ema_seeded_with_first_value():
    s = pd.Series([10.0, 12.0, 11.0])
    e = ema(s, 21)
    alpha = 2 / 22
    assert e.iloc[0] == 10.0
    assert e.iloc[1] == pytest.approx(alpha * 12 + (1 - alpha) * 10)


def test_deviation_formula_and_band_identity():
    out = mean_reversion_oscillator(make_df())
    row = out.dropna().iloc[-1]
    assert row["deviation"] == pytest.approx((row["close"] - row["ema"]) / (2.0 * row["atr"]))
    assert (row["upper"] - row["ema"]) == pytest.approx(2.0 * row["atr"])


def test_crossunder_crossover_semantics():
    s = pd.Series([0.0, -1.0, -1.4, -1.5, -1.3, -1.5])
    assert crossunder(s, -1.4).tolist() == [False, False, False, True, False, True]
    assert crossover(pd.Series([1.0, 1.4, 1.5]), 1.4).tolist() == [False, False, True]


def test_no_lookahead_appending_bars_does_not_change_history():
    df = make_df(150)
    a = mean_reversion_oscillator(df.iloc[:100])["deviation"]
    b = mean_reversion_oscillator(df)["deviation"].iloc[:100]
    pd.testing.assert_series_equal(a, b)


def test_signals_columns_present():
    out = add_signals(mean_reversion_oscillator(make_df()))
    for c in ["alert_oversold", "alert_overbought", "stretched_high", "stretched_low"]:
        assert c in out.columns
