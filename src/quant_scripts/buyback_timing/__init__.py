"""Buyback-timing research pipeline.

Modes (via python -m quant_scripts.buyback_timing):
  harvest   harvest + classify 8-K repurchase-program events from EDGAR
"""

from __future__ import annotations

from .cli import main

__all__ = ["main"]
