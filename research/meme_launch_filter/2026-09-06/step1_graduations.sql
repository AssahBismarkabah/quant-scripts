-- Graduation events for 2026-09-06: first graduation per mint
SELECT mint, MIN(evt_block_time) AS first_graduation_time
FROM pumpdotfun_solana.pump_evt_completeevent
WHERE evt_block_date = DATE '2026-09-06'
GROUP BY mint
