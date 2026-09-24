-- Step 2 feature pull: per-graduate features at the entry bar (graduation).
-- Entry archetype = the graduate's first PumpSwap AMM trade. No-lookahead:
-- all feature aggregates use ONLY curve trades strictly before grad_time.
-- Instant self-grads have empty pre-grad history and drop out naturally.
WITH grads AS (
  SELECT mint, MIN(evt_block_time) AS grad_time
  FROM pumpdotfun_solana.pump_evt_completeevent
  WHERE evt_block_date = DATE '2026-09-04'
  GROUP BY mint
),
launches AS (
  SELECT account_mint AS mint, call_block_time AS create_time, creator
  FROM pumpdotfun_solana.pump_call_create_v2
  WHERE call_block_date = DATE '2026-09-04'
  UNION ALL
  SELECT account_mint, call_block_time, creator
  FROM pumpdotfun_solana.pump_call_create
  WHERE call_block_date = DATE '2026-09-04'
),
curve_pre AS (
  SELECT
    t.token_bought_mint_address AS mint,
    TRUE AS is_buy,
    CAST(t.token_sold_amount_raw AS DOUBLE) / 1e9 AS sol_amount,
    t.trader_id,
    t.block_time,
    t.sol_reserves
  FROM pumpdotfun_solana.base_trades t
  JOIN grads g ON t.token_bought_mint_address = g.mint
  WHERE t.block_time < g.grad_time
  UNION ALL
  SELECT
    t.token_sold_mint_address,
    FALSE,
    CAST(t.token_bought_amount_raw AS DOUBLE) / 1e9,
    t.trader_id,
    t.block_time,
    t.sol_reserves
  FROM pumpdotfun_solana.base_trades t
  JOIN grads g ON t.token_sold_mint_address = g.mint
  WHERE t.block_time < g.grad_time
),
f AS (
  SELECT
    l.mint,
    COUNT(*) AS fb_trades,
    COUNT(DISTINCT c2.trader_id) AS fb_traders,
    SUM(CASE WHEN c2.is_buy THEN 1 ELSE 0 END) AS fb_buys,
    SUM(CASE WHEN NOT c2.is_buy THEN 1 ELSE 0 END) AS fb_sells,
    SUM(CASE WHEN c2.is_buy THEN c2.sol_amount ELSE 0 END) AS fb_buy_sol,
    SUM(CASE WHEN NOT c2.is_buy THEN c2.sol_amount ELSE 0 END) AS fb_sell_sol,
    SUM(CASE WHEN c2.is_buy AND c2.trader_id != l.creator THEN c2.sol_amount ELSE 0 END) AS fb_noncreator_buy_sol,
    SUM(CASE WHEN NOT c2.is_buy AND c2.trader_id != l.creator THEN c2.sol_amount ELSE 0 END) AS fb_noncreator_sell_sol,
    MAX(c2.sol_reserves) AS fb_max_reserves,
    MIN(c2.block_time) AS fb_first_trade_time,
    MAX(c2.block_time) AS fb_last_trade_time,
    -- token-side HHI proxy: top-10 holder concentration needs transfer graph;
    -- use per-trader volume share as a cheap upper-bound proxy for now.
    MAX(c2.pair_share) AS fb_max_trader_share
  FROM (
    SELECT
      c.*,
      c.sol_amount / SUM(c.sol_amount) OVER (PARTITION BY c.mint) AS pair_share
    FROM curve_pre c
  ) c2
  JOIN launches l ON l.mint = c2.mint
  GROUP BY l.mint, l.creator
)
SELECT
  g.mint,
  l.create_time,
  g.grad_time,
  l.creator,
  DATE_DIFF('second', l.create_time, g.grad_time) AS age_at_grad_s,
  f.fb_trades,
  f.fb_traders,
  f.fb_buys,
  f.fb_sells,
  f.fb_buy_sol,
  f.fb_sell_sol,
  f.fb_noncreator_buy_sol,
  f.fb_noncreator_sell_sol,
  f.fb_max_reserves,
  f.fb_first_trade_time,
  f.fb_last_trade_time,
  f.fb_max_trader_share
FROM grads g
JOIN launches l ON l.mint = g.mint
LEFT JOIN f ON f.mint = g.mint
