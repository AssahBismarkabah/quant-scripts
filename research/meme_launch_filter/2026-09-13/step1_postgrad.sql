-- Post-graduation (PumpSwap AMM) trade aggregates for tokens that graduated 2026-09-13.
-- base_trades is bonding-curve-only; PumpSwap activity lives in pump_amm_evt_*.
-- AMM events carry pool (not mint); pool -> base_mint comes from pump_amm_evt_createpoolevent.
-- All 2026-09-13 graduates' pools were created in the Sep block month partition.
-- Pool quote reserves are lamports/1e9 -> SOL. Amounts: quote raw/1e9.
WITH grads AS (
  SELECT mint, MIN(evt_block_time) AS grad_time
  FROM pumpdotfun_solana.pump_evt_completeevent
  WHERE evt_block_date = DATE '2026-09-13'
  GROUP BY mint
),
pools AS (
  SELECT base_mint AS mint, pool, MIN(evt_block_time) AS pool_create_time
  FROM pumpdotfun_solana.pump_amm_evt_createpoolevent
  WHERE evt_block_date BETWEEN DATE '2026-09-13' AND DATE '2026-09-13' + INTERVAL '7' DAY
  GROUP BY base_mint, pool
),
grad_pools AS (
  SELECT g.mint, g.grad_time, p.pool, p.pool_create_time
  FROM grads g
  JOIN pools p ON p.mint = g.mint
),
buy_sides AS (
  SELECT
    gp.mint,
    gp.grad_time,
    b.user AS trader,
    CAST(b.quote_amount_in AS DOUBLE) / 1e9 AS sol_amount,
    b.evt_block_time,
    CAST(b.pool_quote_token_reserves AS DOUBLE) / 1e9 AS quote_reserves
  FROM grad_pools gp
  JOIN pumpdotfun_solana.pump_amm_evt_buyevent b ON b.pool = gp.pool
  WHERE b.evt_block_date >= DATE '2026-09-13'
    AND b.evt_block_time > gp.grad_time
),
sell_sides AS (
  SELECT
    gp.mint,
    gp.grad_time,
    s.user AS trader,
    CAST(s.quote_amount_out AS DOUBLE) / 1e9 AS sol_amount,
    s.evt_block_time,
    CAST(s.pool_quote_token_reserves AS DOUBLE) / 1e9 AS quote_reserves
  FROM grad_pools gp
  JOIN pumpdotfun_solana.pump_amm_evt_sellevent s ON s.pool = gp.pool
  WHERE s.evt_block_date >= DATE '2026-09-13'
    AND s.evt_block_time > gp.grad_time
),
sides AS (
  SELECT *, TRUE AS is_buy FROM buy_sides
  UNION ALL
  SELECT *, FALSE FROM sell_sides
)
SELECT
  mint,
  grad_time,
  COUNT(*) AS pg_trades,
  COUNT(DISTINCT trader) AS pg_traders,
  SUM(CASE WHEN is_buy THEN 1 ELSE 0 END) AS pg_buys,
  SUM(CASE WHEN NOT is_buy THEN 1 ELSE 0 END) AS pg_sells,
  SUM(CASE WHEN is_buy THEN sol_amount ELSE 0 END) AS pg_buy_sol,
  SUM(CASE WHEN NOT is_buy THEN sol_amount ELSE 0 END) AS pg_sell_sol,
  MAX(quote_reserves) AS pg_max_pool_sol,
  MIN(CASE WHEN quote_reserves > 0.001 THEN quote_reserves ELSE NULL END) AS pg_min_pool_sol,
  MIN(evt_block_time) AS pg_first_trade_time,
  MAX(evt_block_time) AS pg_last_trade_time
FROM sides
GROUP BY mint, grad_time
