# B5 Primary-Source Evidence

- [SEC ETF website-posting requirements](https://www.sec.gov/about/divisions-offices/division-investment-management/accounting-disclosure-information/adi-2025-15) establishes that qualifying ETFs post holdings used for NAV calculation before regular trading.
- [SEC ETF prospectus example](https://www.sec.gov/Archives/edgar/data/1633061/000121390026010237/ea0273008-32_497.htm) establishes creation units, baskets, AP agreements, cutoffs, and the route for non-AP investors.
- [SEC creation/redemption disclosure](https://www.sec.gov/Archives/edgar/data/1884021/000121390025102126/ea0262228-04_485apos.htm) describes the AP arbitrage relationship between ETF price and NAV.
- [Cboe historical iNAV](https://datashop.cboe.com/inav-channel-tick-data), [S&P Global iNAV](https://www.marketplace.spglobal.com/en/datasets/inav-%281692912037%29), and [ICE iNAV](https://developer.ice.com/fixed-income-data-services/catalog/ice-data-indices-inav-calculation-services) establish that commercial indicative-value products exist.

These sources do not establish historical intraday executable basket value, AP intent, profitable convergence, retail access to the primary process, or free historical coverage. No commercial source was purchased.

## Frozen universe

The initial universe is [`frozen_universe.csv`](frozen_universe.csv), fixed before any outcome inspection. EMB, EMLC, HYEM, and FM were selected from pre-specified asset-class and market-hours characteristics, not from observed premiums, spreads, or returns. The universe is a research input, not evidence that any candidate is executable.
