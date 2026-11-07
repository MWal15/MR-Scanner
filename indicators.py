"""Python port of the Pine v5 "Mean Reversion Oscillator".

Matches TradingView semantics:
- ta.ema: alpha = 2/(n+1), seeded with the first source value (ewm adjust=False).
- ta.atr: RMA (Wilder) of true range, seeded with SMA of the first n TRs.
- ta.tr: first bar = high - low (handle_na=true behaviour).
All signals are computed on CLOSED bars only. Drop the in-progress bar before calling.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    parts = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    # max(axis=1) skips NaN, so bar 0 falls back to high - low, as in Pine.
    return parts.max(axis=1)


def rma(series: pd.Series, length: int) -> pd.Series:
    """Wilder's RMA, seeded with SMA(length) like ta.rma."""
    values = series.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    if len(values) < length:
        return pd.Series(out, index=series.index)
    out[length - 1] = values[:length].mean()
    alpha = 1.0 / length
    for i in range(length, len(values)):
        out[i] = alpha * values[i] + (1 - alpha) * out[i - 1]
    return pd.Series(out, index=series.index)


def atr(df: pd.DataFrame, length: int) -> pd.Series:
    return rma(true_range(df), length)


def mean_reversion_oscillator(
    df: pd.DataFrame,
    ema_length: int = 21,
    atr_length: int = 14,
    atr_mult: float = 2.0,
) -> pd.DataFrame:
    """Input: DataFrame with columns open, high, low, close (sorted ascending).
    Output: copy with ema, atr, upper, lower, deviation columns.

    deviation = (close - ema) / (atr_mult * atr)
    So +/-1.0 sits exactly on the ATR bands. It is NOT a standard deviation,
    despite the "SD" labels in the Pine script.
    """
    out = df.copy()
    out["ema"] = ema(out["close"], ema_length)
    out["atr"] = atr(out, atr_length)
    out["upper"] = out["ema"] + atr_mult * out["atr"]
    out["lower"] = out["ema"] - atr_mult * out["atr"]
    out["deviation"] = (out["close"] - out["ema"]) / (atr_mult * out["atr"])
    return out


def crossover(s: pd.Series, level: float) -> pd.Series:
    """Pine ta.crossover(s, level): s > level now and s <= level on the prior bar."""
    return (s > level) & (s.shift(1) <= level)


def crossunder(s: pd.Series, level: float) -> pd.Series:
    """Pine ta.crossunder(s, level): s < level now and s >= level on the prior bar."""
    return (s < level) & (s.shift(1) >= level)


def add_signals(
    df: pd.DataFrame,
    overbought: float = 1.4,
    oversold: float = -1.4,
    stretch_high: float = 1.4,
    stretch_low: float = -1.5,
) -> pd.DataFrame:
    """Adds boolean columns.

    alert_oversold   : crossunder(deviation, oversold)   -> price just ENTERED extreme-low zone
    alert_overbought : crossover(deviation, overbought)  -> price just ENTERED extreme-high zone
    stretched_high/low : state flags matching the Pine bgcolor (note the asymmetric 1.4 / -1.5).
    """
    out = df.copy()
    dev = out["deviation"]
    out["alert_oversold"] = crossunder(dev, oversold)
    out["alert_overbought"] = crossover(dev, overbought)
    out["stretched_high"] = dev > stretch_high
    out["stretched_low"] = dev < stretch_low
    return out
