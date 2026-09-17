from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .valuation import conservative_basket_value, executable_gap


REQUIRED_HOLDINGS = {"symbol", "quantity", "holdings_ts"}
REQUIRED_QUOTES = {"symbol", "bid", "ask", "quote_ts"}
REQUIRED_ETF_QUOTES = {"etf_bid", "etf_ask", "quote_ts"}


def build_observability_report(
    holdings: pd.DataFrame,
    underlying_quotes: pd.DataFrame,
    etf_quotes: pd.DataFrame,
    *,
    costs: float = 0.0,
) -> pd.DataFrame:
    """Create a coverage report without calculating returns or signals."""
    missing = {
        "holdings": REQUIRED_HOLDINGS - set(holdings.columns),
        "quotes": REQUIRED_QUOTES - set(underlying_quotes.columns),
        "etf_quotes": REQUIRED_ETF_QUOTES - set(etf_quotes.columns),
    }
    errors = [f"{name}: {sorted(fields)}" for name, fields in missing.items() if fields]
    if errors:
        raise ValueError("missing required columns: " + "; ".join(errors))

    quote_map = {
        str(row.symbol): {"bid": row.bid, "ask": row.ask}
        for row in underlying_quotes.itertuples(index=False)
    }
    basket = conservative_basket_value(holdings.to_dict("records"), quote_map)
    etf = etf_quotes.iloc[0]
    gaps = executable_gap(
        etf_bid=float(etf.etf_bid),
        etf_ask=float(etf.etf_ask),
        basket=basket,
        costs=costs,
    )
    holdings_ts = pd.to_datetime(holdings["holdings_ts"], utc=True)
    quote_ts = pd.to_datetime(underlying_quotes["quote_ts"], utc=True)
    etf_quote_ts = pd.to_datetime(etf_quotes["quote_ts"], utc=True)
    return pd.DataFrame(
        [
            {
                "holdings_ts_min": holdings_ts.min().isoformat(),
                "holdings_ts_max": holdings_ts.max().isoformat(),
                "underlying_quote_ts_min": quote_ts.min().isoformat(),
                "underlying_quote_ts_max": quote_ts.max().isoformat(),
                "etf_quote_ts": etf_quote_ts.iloc[0].isoformat(),
                "holding_rows": len(holdings),
                "covered_rows": len(holdings) - len(basket.missing_symbols),
                "missing_symbols": ",".join(basket.missing_symbols),
                "buy_value": basket.buy_value if not basket.missing_symbols else None,
                "sell_value": basket.sell_value if not basket.missing_symbols else None,
                "long_etf_gap_after_costs": gaps["long_etf_gap"],
                "long_basket_gap_after_costs": gaps["long_basket_gap"],
                "executable": not basket.missing_symbols,
            }
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit ETF basket observability; no returns analysis.")
    parser.add_argument("--holdings", type=Path, required=True)
    parser.add_argument("--quotes", type=Path, required=True)
    parser.add_argument("--etf-quotes", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--costs", type=float, default=0.0)
    args = parser.parse_args()
    report = build_observability_report(
        pd.read_csv(args.holdings), pd.read_csv(args.quotes), pd.read_csv(args.etf_quotes), costs=args.costs
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
