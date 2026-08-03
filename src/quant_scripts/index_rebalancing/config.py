from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .models import Venue


@dataclass(frozen=True)
class DatabentoCredentials:
    api_key: str

    @classmethod
    def from_env(cls, dotenv_path: Path | None = None) -> "DatabentoCredentials":
        if dotenv_path is not None and dotenv_path.exists():
            for line in dotenv_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if key.strip() == "DATABENTO_API_KEY":
                    return cls(api_key=value.strip())
        import os

        return cls(api_key=os.environ.get("DATABENTO_API_KEY", ""))


@dataclass(frozen=True)
class FrictionSettings:
    slippage_base_bps: float = 1.5  # frozen by spec
    slippage_stress_bps: float = 10.0  # frozen by spec (small-cap names)
    commission_per_share: float = 0.005  # pre-registered
    sec_fee_rate: float = 0.0000278  # Section 31, per $ of sell notional
    borrow_fee_annual_bps: float = 200.0  # modeled stress assumption (no borrow data at L1)
    borrow_fee_cap_bps: float = 300.0  # hard-to-borrow filter cap, pre-registered

    def slippage_bps(self, *, stress: bool = False) -> float:
        return self.slippage_stress_bps if stress else self.slippage_base_bps


@dataclass(frozen=True)
class StudySettings:
    study_start: date = date(2023, 3, 28)  # EQUS.MINI start
    data_end: date = date(2026, 8, 1)  # EQUS.MINI ohlcv-1d end
    windows_td: tuple[int, ...] = (10, 20, 40, 60)  # frozen by spec
    min_price_history_td: int = 252  # 1 year of trading before event
    min_addv20_usd: float = 5_000_000.0  # pre-registered liquidity threshold
    vol_window_td: int = 60  # vol estimation window, ends at effective-date close
    depth_fraction: float = 0.05  # of ADDV20 executable per event
    stop_loss_bps: float | None = None  # base case: no stop; robustness variant: 1000.0
    benchmark_by_venue: dict = field(
        default_factory=lambda: {
            Venue.SP600: "IJR",
            Venue.SP400: "IJH",
            Venue.R2000: "IWM",
        }
    )


__all__ = ["DatabentoCredentials", "FrictionSettings", "StudySettings"]
