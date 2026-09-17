from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping


@dataclass(frozen=True)
class BasketValuation:
    """Conservative executable bounds for a holdings snapshot."""

    buy_value: float
    sell_value: float
    covered_notional: float
    missing_symbols: tuple[str, ...]


def conservative_basket_value(
    holdings: Iterable[Mapping[str, object]],
    quotes: Mapping[str, Mapping[str, float]],
) -> BasketValuation:
    """Value a basket using asks to buy and bids to sell.

    Holdings must contain ``symbol`` and ``quantity``.  A row is excluded
    from both bounds when either executable side is absent or invalid; this
    prevents incomplete coverage from being mistaken for a tradable gap.
    """
    buy = sell = covered = 0.0
    missing: list[str] = []
    for row in holdings:
        symbol = str(row["symbol"])
        quantity = float(row["quantity"])
        quote = quotes.get(symbol, {})
        bid, ask = quote.get("bid"), quote.get("ask")
        if (
            quantity < 0
            or bid is None
            or ask is None
            or not isfinite(float(bid))
            or not isfinite(float(ask))
            or float(bid) <= 0
            or float(ask) < float(bid)
        ):
            missing.append(symbol)
            continue
        buy += quantity * float(ask)
        sell += quantity * float(bid)
        covered += quantity * ((float(bid) + float(ask)) / 2)
    return BasketValuation(buy, sell, covered, tuple(missing))


def executable_gap(
    *, etf_bid: float, etf_ask: float, basket: BasketValuation, costs: float
) -> dict[str, float | None]:
    """Return conservative residual gaps after explicit costs.

    ``long_etf_gap`` is the amount left after buying ETF shares and selling
    the basket. ``long_basket_gap`` is the reverse direction. Values are
    null when the basket is incomplete or ETF quotes are invalid.
    """
    if basket.missing_symbols or etf_bid <= 0 or etf_ask < etf_bid:
        return {"long_etf_gap": None, "long_basket_gap": None}
    return {
        "long_etf_gap": basket.sell_value - etf_ask - costs,
        "long_basket_gap": etf_bid - basket.buy_value - costs,
    }
