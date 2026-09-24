-- First-hour trade aggregates per token created 2026-09-10, split creator vs non-creator
WITH launches AS (
  SELECT account_mint AS mint, call_block_time AS create_time, creator
  FROM pumpdotfun_solana.pump_call_create_v2
  WHERE call_block_date = DATE '2026-09-10'
  UNION ALL
  SELECT account_mint, call_block_time, creator
  FROM pumpdotfun_solana.pump_call_create
  WHERE call_block_date = DATE '2026-09-10'
),
trade_sides AS (
  SELECT
    t.token_bought_mint_address AS mint,
    TRUE AS is_buy,
    CAST(t.token_sold_amount_raw AS DOUBLE) / 1e9 AS sol_amount,
    t.trader_id,
    t.block_time,
    l.create_time,
    l.creator
  FROM pumpdotfun_solana.base_trades t
  JOIN launches l ON t.token_bought_mint_address = l.mint
  WHERE t.block_time >= TIMESTAMP '2026-09-10 00:00:00'
    AND t.block_time < DATE '2026-09-10' + INTERVAL '1' DAY
    AND t.block_time <= l.create_time + INTERVAL '60' MINUTE
  UNION ALL
  SELECT
    t.token_sold_mint_address AS mint,
    FALSE AS is_buy,
    CAST(t.token_bought_amount_raw AS DOUBLE) / 1e9 AS sol_amount,
    t.trader_id,
    t.block_time,
    l.create_time,
    l.creator
  FROM pumpdotfun_solana.base_trades t
  JOIN launches l ON t.token_sold_mint_address = l.mint
  WHERE t.block_time >= TIMESTAMP '2026-09-10 00:00:00'
    AND t.block_time < DATE '2026-09-10' + INTERVAL '1' DAY
    AND t.block_time <= l.create_time + INTERVAL '60' MINUTE
)
SELECT
  mint,
  creator,
  create_time,
  COUNT(*) AS fh_trades,
  COUNT(DISTINCT CASE WHEN trader_id != creator THEN trader_id END) AS fh_noncreator_traders,
  COUNT(DISTINCT trader_id) AS fh_traders,
  SUM(CASE WHEN is_buy AND trader_id = creator THEN 1 ELSE 0 END) AS fh_creator_buys,
  SUM(CASE WHEN is_buy AND trader_id = creator THEN sol_amount ELSE 0 END) AS fh_creator_buy_sol,
  SUM(CASE WHEN NOT is_buy AND trader_id = creator THEN 1 ELSE 0 END) AS fh_creator_sells,
  SUM(CASE WHEN NOT is_buy AND trader_id = creator THEN sol_amount ELSE 0 END) AS fh_creator_sell_sol,
  SUM(CASE WHEN is_buy AND trader_id != creator THEN 1 ELSE 0 END) AS fh_noncreator_buys,
  SUM(CASE WHEN is_buy AND trader_id != creator THEN sol_amount ELSE 0 END) AS fh_noncreator_buy_sol,
  SUM(CASE WHEN NOT is_buy AND trader_id != creator THEN sol_amount ELSE 0 END) AS fh_noncreator_sell_sol,
  MIN(CASE WHEN trader_id = creator AND NOT is_buy THEN DATE_DIFF('second', create_time, block_time) / 60.0 END) AS creator_first_sell_min
FROM trade_sides
GROUP BY mint, creator, create_time
