with source as (
  select * from {{ source('public', 'outputs') }}
)
select
  txid,
  output_index,
  address,
  scriptpubkey_type,
  value / 100000000.0 as value_btc
from source
