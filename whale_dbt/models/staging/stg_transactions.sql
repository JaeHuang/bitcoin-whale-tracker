with source as (
  select * from {{ source('public', 'transactions') }}
)
select
  txid,
  vin_count,
  vout_count,
  is_coinbase,
  fee / 100000000.0 as fee_btc,
  total_input_value / 100000000.0 as input_btc,
  total_output_value / 100000000.0 as output_btc
from source
