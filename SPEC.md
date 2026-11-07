# Mean Reversion Oscillator: Spec

Ported from Pine v5 `indicator("Mean Reversion Oscillator")`.

## Inputs (defaults)
| Name | Default | Meaning |
|---|---|---|
| ema_length | 21 | EMA of close (the "mean") |
| atr_length | 14 | Wilder ATR period |
| atr_mult | 2.0 | Band width in ATRs |

## Formulas
- `ema = EMA(close, 21)`: alpha = 2/(n+1), seeded with the first close
- `atr = RMA(TR, 14)`: Wilder smoothing, seeded with SMA of first 14 TRs. TR on bar 0 = high - low
- `upper = ema + 2.0 * atr`, `lower = ema - 2.0 * atr`
- **`deviation = (close - ema) / (2.0 * atr)`**

`deviation` is measured in band-widths, so +/-1.0 = price exactly on the ATR band. It is not a statistical standard deviation, despite the "SD" labels in the original.

## Reference levels
+1.4, +1.0, 0, -1.0, -1.4 (display only in Pine).

## Signals
| Name | Pine origin | Rule | Meaning |
|---|---|---|---|
| alert_oversold | `ta.crossunder(deviation, -1.4)` | deviation < -1.4 now and >= -1.4 on prior bar | Price just fell into extreme-low zone: candidate LONG |
| alert_overbought | `ta.crossover(deviation, 1.4)` | deviation > 1.4 now and <= 1.4 on prior bar | Price just rose into extreme-high zone: candidate SHORT |
| stretched_high | bgcolor | deviation > 1.4 | State flag |
| stretched_low | bgcolor | deviation < -1.5 | State flag (threshold is -1.5, asymmetric in the original; preserved) |

## Behavioural notes and gotchas
1. **Fires on entry, not recovery.** Alerts trigger when price first becomes extreme, not when it turns back toward the mean. Confirm this is what you want; a "recovery cross" (deviation crossing back above -1.4) is a different, later signal. Config option `trigger_mode` covers cross vs state.
2. **Repainting.** The indicator uses only `close`, so it only changes on the live bar. Always evaluate on the last CLOSED bar.
3. **Warm-up.** First ~14 bars have NaN ATR. Fetch at least ~200 bars so EMA/RMA converge to TradingView's values (they depend on history length; small differences are normal if the data window differs).
4. **Data adjustments.** TradingView uses split-adjusted data by default. Match that in the data provider or values will drift.
5. **Visual-only parts** (plot colors, fills, bgcolor, hlines) are not ported.

## Not in the Pine script (must be defined by the user before building)
- Universe of tickers
- Timeframe (assumed daily)
- How an oversold/overbought underlying maps to an option trade (calls vs puts, spreads, etc.)
- Option filters: see `config.yaml`, values are placeholders

## Scanner flow (to be built)
1. Load universe and config.
2. For each ticker, fetch ~250 daily bars, drop any unfinished bar.
3. Compute oscillator and signals via `mr_scanner.indicators`.
4. If signal per `trigger_mode` is true, fetch the options chain for that ticker.
5. Filter contracts by `options:` config (DTE, delta, OI, volume, spread, optional IV rank).
6. Rank and send a notification; also write a CSV log.
