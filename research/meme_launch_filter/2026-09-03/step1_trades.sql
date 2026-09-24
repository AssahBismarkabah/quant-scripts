-- Per-token trade aggregates for tokens created 2026-09-03: buys and sells stacked.
WITH launches AS (
  SELECT account_mint AS mint, call_block_time AS create_time, creator
  FROM pumpdotfun_solana.pump_call_create_v2
  WHERE call_block_date = DATE '2026-09-03'
  UNION ALL
  SELECT account_mint, call_block_time, creator
  FROM pumpdotfun_solana.pump_call_create
  WHERE call_block_date = DATE '2026-09-03'
),
trade_sides AS (
  SELECT
    t.token_bought_mint_address AS mint,
    TRUE AS is_buy,
    CAST(t.token_sold_amount_raw AS DOUBLE) / 1e9 AS sol_amount,
    t.trader_id,
    t.block_time,
    t.sol_reserves,
    t.token_reserves
  FROM pumpdotfun_solana.base_trades t
  JOIN launches l ON t.token_bought_mint_address = l.mint
  WHERE t.block_time >= TIMESTAMP '2026-09-03 00:00:00'
    AND t.block_time < DATE '2026-09-03' + INTERVAL '1' DAY
  UNION ALL
  SELECT
    t.token_sold_mint_address AS mint,
    FALSE AS is_buy,
    CAST(t.token_bought_amount_raw AS DOUBLE) / 1e9 AS sol_amount,
    t.trader_id,
    t.block_time,
    t.sol_reserves,
    t.token_reserves
  FROM pumpdotfun_solana.base_trades t
  JOIN launches l ON t.token_sold_mint_address = l.mint
  WHERE t.block_time >= TIMESTAMP '2026-09-03 00:00:00'
    AND t.block_time < DATE '2026-09-03' + INTERVAL '1' DAY
),
side_agg AS (
  SELECT
    mint,
    COUNT(*) AS n_trades,
    COUNT(DISTINCT trader_id) AS n_traders,
    SUM(CASE WHEN is_buy THEN 1 ELSE 0 END) AS n_buys,
    SUM(CASE WHEN NOT is_buy THEN 1 ELSE 0 END) AS n_sells,
    SUM(CASE WHEN is_buy THEN sol_amount ELSE 0 END) AS total_buy_sol,
    SUM(CASE WHEN NOT is_buy THEN sol_amount ELSE 0 END) AS total_sell_sol,
    MAX(sol_reserves) AS max_sol_reserves,
    MIN(CASE WHEN sol_reserves > 0.001 THEN sol_reserves ELSE NULL END) AS min_sol_reserves,
    MIN(block_time) AS first_trade_time,
    MAX(block_time) AS last_trade_time
  FROM trade_sides
  GROUP BY mint
)
SELECT
  s.*,
  l.creator,
  l.create_time
FROM side_agg s
JOIN launches l ON s.mint = l.mint
