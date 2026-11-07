Read SPEC.md, AGENTS.md and config.yaml. The indicator logic in src/mr_scanner/indicators.py is already implemented and tested; do not alter its math.

Build the scanner around it:

1. `data/base.py`: a `DataProvider` protocol with `get_bars(symbol, timeframe, limit) -> DataFrame[open, high, low, close, volume]` and `get_option_chain(symbol) -> DataFrame` (columns: expiry, strike, type, bid, ask, delta, iv, open_interest, volume).
2. One concrete provider for <PICK ONE: Polygon / Tradier / Alpaca / Schwab>, reading the API key from an env var. Include a `FakeProvider` for tests that returns fixture data.
3. `scan.py`: load config.yaml and universe.txt, compute signals per ticker, honour `trigger_mode`, fetch chains only for tickers with a signal, apply the `options:` filters, and rank results (suggest: tightest spread, then highest open interest).
4. `notify.py`: send results via <Discord webhook / Telegram / email> and always append to `output/results.csv`.
5. `.github/workflows/scan.yml`: run the scan on weekdays shortly after market close, with secrets from GitHub Actions secrets.
6. Tests for the filtering logic and the scan flow using FakeProvider. All tests must pass.

Ask before making assumptions about anything marked TODO in config.yaml. Open a PR when done.
