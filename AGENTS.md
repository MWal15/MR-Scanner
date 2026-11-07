# AGENTS.md

## Project
Options scanner. Finds underlyings whose Mean Reversion Oscillator is stretched, then filters their option chains. See `SPEC.md` for the full behaviour.

## Rules
- `src/mr_scanner/indicators.py` is the source of truth for indicator math. Do not change formulas without updating `SPEC.md` and tests.
- All thresholds and filters come from `config.yaml`. Never hardcode them.
- Signals use CLOSED bars only. Never evaluate on a partial bar.
- Data providers sit behind an interface (`DataProvider` with `get_bars()` and `get_option_chain()`), so providers can be swapped.
- No scraping TradingView and no use of unofficial TradingView APIs.
- Secrets (API keys, webhooks) come from environment variables. Never commit them.
- Every new module needs tests. Run `pytest` before opening a PR.
- This tool surfaces candidates only. It does not place orders.

## Commands
- Install: `pip install -e ".[dev]"`
- Test: `pytest`
