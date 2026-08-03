from __future__ import annotations

from .config import FrictionSettings
from .models import EventAction


def commission_cost_bps(price: float, *, settings: FrictionSettings) -> float:
    """Per-share commission expressed in bps of notional."""
    if price <= 0:
        return 0.0
    return settings.commission_per_share / price * 10_000


def sec_fee_bps(*, settings: FrictionSettings) -> float:
    """SEC Section 31 fee (sell side only), in bps of notional."""
    return settings.sec_fee_rate * 10_000


def borrow_cost_bps(hold_days: int, *, settings: FrictionSettings) -> float:
    """Annualized borrow fee pro-rated over the holding window."""
    return settings.borrow_fee_annual_bps * hold_days / 365


def is_hard_to_borrow(fee_annual_bps: float, *, settings: FrictionSettings) -> bool:
    return fee_annual_bps > settings.borrow_fee_cap_bps


def total_cost_bps(
    action: EventAction,
    entry_price: float,
    exit_price: float,
    hold_days: int,
    *,
    stress: bool,
    settings: FrictionSettings,
) -> float:
    """Total friction in bps of notional for one round trip.

    Long:  entry slippage + exit slippage + 2 x commission + SEC fee (sell).
    Short: same plus borrow (short pays SEC fee at entry; borrow over window).
    """
    sl = settings.slippage_bps(stress=stress)
    c_entry = commission_cost_bps(entry_price, settings=settings)
    c_exit = commission_cost_bps(exit_price, settings=settings)
    sec = sec_fee_bps(settings=settings)
    cost = sl + sl + c_entry + c_exit + sec
    if action is EventAction.ADDITION:  # short leg
        cost += sec  # SEC fee on the opening sell
        cost += borrow_cost_bps(hold_days, settings=settings)
    return cost


__all__ = [
    "commission_cost_bps",
    "sec_fee_bps",
    "borrow_cost_bps",
    "is_hard_to_borrow",
    "total_cost_bps",
]
