-- Per-graduate 1-minute OHLC bars for the first 24h post-graduation (PumpSwap AMM).
-- Purpose: honest exit-rule simulation (trailing stop / take-profit / 24h time stop)
-- needs price paths, not aggregates. All frozen exits live inside the first 24h.
-- Price = pool_quote_token_reserves / pool_base_token_reserves at each AMM event
-- (post-trade marginal price). Bars: minute-truncated OHLC + last reserves.
-- Day-split pulls: evt_block_date window covers grad day + 1 for cross-midnight grads.
WITH grads AS (
  SELECT mint, MIN(evt_block_time) AS grad_time
  FROM pumpdotfun_solana.pump_evt_completeevent
  WHERE evt_block_date = DATE '2026-09-14'
  GROUP BY mint
),
pools AS (
  SELECT base_mint AS mint, pool, MIN(evt_block_time) AS pool_create_time
  FROM pumpdotfun_solana.pump_amm_evt_createpoolevent
  WHERE evt_block_date BETWEEN DATE '2026-09-14' AND DATE '2026-09-14' + INTERVAL '1' DAY
  GROUP BY base_mint, pool
),
one_pool AS (
  SELECT mint, pool
  FROM (
    SELECT mint, pool, ROW_NUMBER() OVER (PARTITION BY mint ORDER BY pool_create_time) AS rn
    FROM pools
  ) t
  WHERE rn = 1
),
grad_pools AS (
  SELECT g.mint, g.grad_time, p.pool
  FROM grads g
  JOIN one_pool p ON p.mint = g.mint
),
buys AS (
  SELECT
    gp.mint,
    gp.grad_time,
    b.evt_block_time,
    TRUE AS is_buy,
    CAST(b.quote_amount_in AS DOUBLE) / 1e9 AS sol_amount,
    CAST(b.pool_quote_token_reserves AS DOUBLE) / 1e9 AS quote_reserves,
    CAST(b.pool_base_token_reserves AS DOUBLE) AS base_reserves
  FROM grad_pools gp
  JOIN pumpdotfun_solana.pump_amm_evt_buyevent b ON b.pool = gp.pool
  WHERE b.evt_block_date BETWEEN DATE '2026-09-14' AND DATE '2026-09-14' + INTERVAL '1' DAY
    AND b.evt_block_time > gp.grad_time
    AND b.evt_block_time <= gp.grad_time + INTERVAL '24' HOUR
),
sells AS (
  SELECT
    gp.mint,
    gp.grad_time,
    s.evt_block_time,
    FALSE AS is_buy,
    CAST(s.quote_amount_out AS DOUBLE) / 1e9 AS sol_amount,
    CAST(s.pool_quote_token_reserves AS DOUBLE) / 1e9 AS quote_reserves,
    CAST(s.pool_base_token_reserves AS DOUBLE) AS base_reserves
  FROM grad_pools gp
  JOIN pumpdotfun_solana.pump_amm_evt_sellevent s ON s.pool = gp.pool
  WHERE s.evt_block_date BETWEEN DATE '2026-09-14' AND DATE '2026-09-14' + INTERVAL '1' DAY
    AND s.evt_block_time > gp.grad_time
    AND s.evt_block_time <= gp.grad_time + INTERVAL '24' HOUR
),
sides AS (
  SELECT * FROM buys
  UNION ALL
  SELECT * FROM sells
),
priced AS (
  SELECT
    *,
    quote_reserves / NULLIF(base_reserves, 0) AS price
  FROM sides
)
SELECT
  mint,
  grad_time,
  DATE_TRUNC('minute', evt_block_time) AS minute_ts,
  MIN_BY(price, evt_block_time) AS open,
  MAX(price) AS high,
  MIN(price) AS low,
  MAX_BY(price, evt_block_time) AS close,
  SUM(CASE WHEN is_buy THEN sol_amount ELSE 0 END) AS buy_sol,
  SUM(CASE WHEN NOT is_buy THEN sol_amount ELSE 0 END) AS sell_sol,
  COUNT(*) AS n_trades,
  MAX_BY(quote_reserves, evt_block_time) AS last_quote_reserves,
  MAX_BY(base_reserves, evt_block_time) AS last_base_reserves
FROM priced
GROUP BY mint, grad_time, DATE_TRUNC('minute', evt_block_time)
