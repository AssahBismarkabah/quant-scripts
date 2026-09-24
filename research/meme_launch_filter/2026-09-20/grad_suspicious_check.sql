-- Suspicious instant-graduation detail: creator==trader share, one trader share, trade count
WITH pairs AS (
  SELECT g.mint, g.user AS grad_user, g.evt_tx_id AS grad_tx,
         DATE_DIFF('second', l.call_block_time, g.evt_block_time) / 60.0 AS minutes,
         l.creator
  FROM pumpdotfun_solana.pump_evt_completeevent g
  JOIN pumpdotfun_solana.pump_call_create_v2 l ON g.mint = l.account_mint
  WHERE g.evt_block_date = DATE '2026-09-20'
    AND l.call_block_date = DATE '2026-09-20'
    AND DATE_DIFF('second', l.call_block_time, g.evt_block_time) < 60
)
SELECT
  COUNT(*) AS n_instant_grads,
  COUNT(DISTINCT p.grad_user) AS distinct_grad_users,
  SUM(CASE WHEN p.grad_user = p.creator THEN 1 ELSE 0 END) AS grad_user_is_creator,
  COUNT(DISTINCT p.creator) AS distinct_creators
FROM pairs p
