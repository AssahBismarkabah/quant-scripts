"""Opening-Range / Gap strategies pre-registered probe package.

Implements the frozen rule set from IA/opening-range-gap-strategies-research-spec.md
§8 for three independent, falsifiable strategies on NQ RTH 1-min bars:

- ORB      (Crabel-style opening range breakout): first 15-min range, 5-min close
           breakout, stop at range-other-side, 1:2 RR target.
- Gap Fill (fill the prev-close -> open gap): enter in fill direction after the
           open, target = full fill, plus a raw gap-fill-rate stat.
- Oops     (Larry Williams): gap >= 20 pts beyond prev-day high/low, trade the
           break back through the level, 1:1 RR.

Data is the combined owned NQ RTH 1-min caches (2013-11 .. 2026-08), deduped on
ts. All mechanics are look-ahead free by construction (gate 6): prev-day levels
and the opening range are complete before any trigger, and fills execute at the
open of the 5-min bar AFTER the confirming close.
"""

from .config import StudyParams
from .bars import load_combined
from .backtest import run_orb, run_gap_fill, run_oops

__all__ = ["StudyParams", "load_combined", "run_orb", "run_gap_fill", "run_oops"]
