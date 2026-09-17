"""Feasibility calculations for ETF NAV-dislocation research.

This package deliberately stops at observability and execution checks.  It
does not contain a signal, return series, or backtest.
"""

from .valuation import BasketValuation, conservative_basket_value, executable_gap

__all__ = ["BasketValuation", "conservative_basket_value", "executable_gap"]
