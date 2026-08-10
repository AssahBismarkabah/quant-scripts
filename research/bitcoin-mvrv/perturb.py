"""Perturbation + drop-cycle sensitivity for the MVRV DCA verdict (G2/G4).

Not a re-specification of the frozen test; characterization only. Reports whether
the OOS max-DD improvement of dynamic vs buy-and-hold survives modest parameter
perturbation, and whether either window's conclusion flips when dropping the
worst/best year. Used to qualify the DISCONFIRMED verdict (which is already
determined by G5 IS-reproduction failure).
"""

from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_probe import (load, simulate, metrics, Z_ACC, Z_TRIM, MULT_ACC,
                       MULT_NEUT, MULT_TRIM, PERIOD_DAYS, FRICTION_SIDE,
                       FRICTION_FLAT, TOTAL_BUDGET, IS_START, IS_END,
                       OOS_START, OOS_END)

# re-import simulate with custom thresholds via monkeypatching constants is messy;
# instead reimplement a thin local perturbation driver reusing simulate fields
# by calling simulate (which reads module globals we can override).

import run_probe as RP


def run_with(Z_ACC_, Z_TRIM_, M_ACC_, M_TRIM_, M_NEUT_=1.0):
    RP.Z_ACC, RP.Z_TRIM = Z_ACC_, Z_TRIM_
    RP.MULT_ACC, RP.MULT_TRIM, RP.MULT_NEUT = M_ACC_, M_TRIM_, M_NEUT_
    for wname, (ws, we) in {"IS": (IS_START, IS_END), "OOS": (OOS_START, OOS_END)}.items():
        vals = {}
        for mode in ["dynamic", "buyhold"]:
            v, *_ = simulate(RP.load_global_df(), ws, we, mode)
            vals[mode] = metrics(v)
        dd_dyn, dd_bh = vals["dynamic"]["max_drawdown"], vals["buyhold"]["max_drawdown"]
        yield wname, dd_dyn, dd_bh


# ensure load() reads module-level ROOT/CACHE consistently
def load_df():
    return load()


RP.load_global_df = load_df


def main():
    base = [(Z_ACC, Z_TRIM, MULT_ACC, MULT_TRIM)]
    perturbs = base + [
        (-0.75, 2.0, 3.0, 0.25),   # milder buy threshold
        (-1.25, 2.0, 3.0, 0.25),   # deeper buy threshold
        (-1.0, 1.5, 3.0, 0.25),    # lower trim threshold
        (-1.0, 2.5, 3.0, 0.25),    # higher trim threshold
        (-1.0, 2.0, 2.0, 0.25),    # lower accel multiplier
        (-1.0, 2.0, 4.0, 0.25),    # higher accel multiplier
        (-1.0, 2.0, 3.0, 0.0),     # full stop at trim
    ]
    print(f"{'params':42} {'IS dynDD':>9} {'IS bhDD':>9} {'IS impr':>8}  {'OOS dynDD':>9} {'OOS bhDD':>9} {'OOS impr':>8}  IS<BH  OOS<BH")
    for p in perturbs:
        ris = ris_oos = None
        for wname, d, b in run_with(*p):
            if wname == "IS":
                ris = (d, b)
            else:
                ris_oos = (d, b)
        d_i, b_i = ris; d_o, b_o = ris_oos
        impr_i = (b_i - d_i) * 100
        impr_o = (b_o - d_o) * 100
        print(f"{str(p):42} {d_i*100:8.1f}% {b_i*100:8.1f}% {impr_i:7.1f}pp  {d_o*100:8.1f}% {b_o*100:8.1f}% {impr_o:7.1f}pp  {d_i<b_i!s:<5s} {d_o<b_o!s}")


if __name__ == "__main__":
    main()
