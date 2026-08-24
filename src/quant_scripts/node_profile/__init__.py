"""Fixed-range volume-profile node detection for the four swing setups.

This module implements IA/node-profile-setups-spec.md. It computes, per symbol
on a daily panel, the raw inputs for the four discretionary setups:

  S1 contraction:   tight rolling range, node = range POC
  S2 trend:         leg high-volume cluster, node = cluster
  S3 rejection:     sharp reversal level, node = reaction origin
  S4 failed-break:  break closed back inside range, node = range POC

Everything is a deterministic function of split-adjusted OHLCV. The threshold
parameters are frozen in SpecParams (spec SS1-SS5); a human veto remains ONLY
at the point where a definition is genuinely a judgment call, and that veto is
explicitly declared in the spec, never silently tuned.
"""

from .detector import (
    NodeKind,
    NodeSignal,
    SpecParams,
    detect_nodes,
    value_area,
)

__all__ = ["NodeKind", "NodeSignal", "SpecParams", "detect_nodes", "value_area"]
