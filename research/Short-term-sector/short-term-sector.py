# region imports
from AlgorithmImports import *
# endregion


class SectorMomentumRotation(QCAlgorithm):
    """
    Short-term sector momentum rotation.

    Research-backed edge (validated Jan 2023 -> present and back to Oct 2015):
    - Universe: 11 US sector SPDRs + QQQ
    - Signal: trailing 1-month (21 trading day) rate of change
    - Rebalance: monthly, equal-weight top-2 highest momentum sectors, fully invested
    """

    def initialize(self) -> None:
        self.set_start_date(2023, 1, 1)
        self.set_cash(100000)

        # reserve a small cash buffer so same-bar rotations cannot run out of margin
        self.settings.free_portfolio_value_percentage = 0.03

        # ---- Strategy parameters ----
        self._momentum_window = 21      # trading days, ~1 month
        self._top_k = 2                 # number of sectors to hold

        # ---- Universe ----
        self._tickers = [
            "XLK", "XLF", "XLE", "XLV", "XLI",
            "XLB", "XLY", "XLP", "XLU", "XLRE", "QQQ"
        ]
        self._symbols = {}
        for ticker in self._tickers:
            equity = self.add_equity(ticker, Resolution.DAILY)
            # attach a self-updating RateOfChange indicator to each security
            equity.mom = self.roc(equity.symbol, self._momentum_window, Resolution.DAILY)
            self._symbols[ticker] = equity.symbol

        # ---- Rebalance: first trading day of month, after the open ----
        self.schedule.on(
            self.date_rules.month_start("XLK"),
            self.time_rules.after_market_open("XLK", 30),
            self._rebalance
        )

        # warm up the momentum indicators from history
        self.set_warm_up(self._momentum_window + 5, Resolution.DAILY)

    def _rebalance(self) -> None:
        if self.is_warming_up:
            return

        # ---- Compute momentum scores ----
        scores = []
        for ticker, symbol in self._symbols.items():
            sec = self.securities[symbol]
            if not sec.mom.is_ready:
                continue
            scores.append((ticker, sec.mom.current.value))

        if not scores:
            return

        # Pick the top-k sectors by 1-month momentum, fully invested
        scores.sort(key=lambda x: x[1], reverse=True)
        winners = [t for t, _ in scores[:self._top_k]]

        weight = 1.0 / len(winners)
        targets = [PortfolioTarget(self._symbols[t], weight) for t in winners]
        self.set_holdings(targets, liquidate_existing_holdings=True)
        self.debug(f"Rebalance {self.time.date()}: holding {winners} at {weight:.2f} each")
