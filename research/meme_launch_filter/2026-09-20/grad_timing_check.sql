SELECT
  CASE WHEN t.minutes < 1 THEN 'under_1min'
       WHEN t.minutes < 60 THEN '1_60min'
       WHEN t.minutes < 360 THEN '1_6h'
       ELSE 'over_6h' END AS bucket,
  COUNT(*) AS n
FROM (
  SELECT DATE_DIFF('second', l.call_block_time, g.evt_block_time) / 60.0 AS minutes
  FROM pumpdotfun_solana.pump_evt_completeevent g
  JOIN pumpdotfun_solana.pump_call_create_v2 l ON g.mint = l.account_mint
  WHERE g.evt_block_date = DATE '2026-09-20'
    AND l.call_block_date = DATE '2026-09-20'
) t
GROUP BY 1
ORDER BY n DESC
