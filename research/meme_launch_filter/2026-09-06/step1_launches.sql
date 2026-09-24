-- Step 1: all pump.fun token creations for 2026-09-06 (v1 legacy + v2 live path)
SELECT
  'v1' AS schema_ver,
  call_block_time,
  call_block_slot,
  call_tx_id,
  account_mint AS mint,
  account_bonding_curve AS bonding_curve,
  call_tx_signer AS fee_payer,
  creator,
  name,
  symbol,
  uri,
  CAST(NULL AS boolean) AS is_mayhem_mode
FROM pumpdotfun_solana.pump_call_create
WHERE call_block_date = DATE '2026-09-06'
UNION ALL
SELECT
  'v2',
  call_block_time,
  call_block_slot,
  call_tx_id,
  account_mint,
  account_bonding_curve,
  call_tx_signer,
  creator,
  name,
  symbol,
  uri,
  is_mayhem_mode
FROM pumpdotfun_solana.pump_call_create_v2
WHERE call_block_date = DATE '2026-09-06'
ORDER BY call_block_time, call_tx_id
