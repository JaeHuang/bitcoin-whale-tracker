import requests
import json
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
import sys


sys.path.append('/opt/airflow/scripts')

from SQL.transactions import Transactions
from SQL.inputs import Inputs
from SQL.outputs import Outputs

url = 'https://blockstream.info/api/blocks/tip/hash'


def get_latest_block_hash():
    result = requests.get(url)
    return result.text

def get_block_by_hash(hash):
    url = f'https://blockstream.info/api/blocks/{hash}'
    result = requests.get(url)
    return result.json()

def get_block_transactions(hash):
    url = f'https://blockstream.info/api/block/{hash}/txs'
    result = requests.get(url)
    return result.json()

def get_all_transactions_by_block_hash(hash, tx_count=None):
    # If tx_count is not provided, it will fetch all transactions in the block
    start_index = 0
    url = f'https://blockstream.info/api/block/{hash}/txs'
    txs = []
    page = 1
    while True:
        result = requests.get(url)
        page_txs = result.json()
        page_result_count = len(page_txs)
        start_index += page_result_count
        txs.extend(page_txs)
        print(f'page {page} done, {len(txs)} txs in total. First tx id: {page_txs[0]["txid"]}')
        page += 1
        if page_result_count < 25 or (tx_count is not None and len(txs) >= tx_count):
            print(f'No more page to request')
            break
        url = f'https://blockstream.info/api/block/{hash}/txs/{start_index}'

    return txs

def clean_txs(txs, block_height):
    cleaned_txs = []
    ignore_type = ['op_return', 'unknown']
    for tx in txs:
        print(tx['txid'])
        tx_id = tx['txid']
        vin_count = len(tx['vin'])
        vout_count = len(tx['vout'])
        is_coinbase = tx['vin'][0]['is_coinbase']
        total_input_value = sum(vin['prevout']['value'] for vin in tx['vin'] if not is_coinbase)
        total_output_value = sum(vout['value'] for vout in tx['vout'])
        fee = tx['fee']
        sender_addresses = [vin['prevout']['scriptpubkey_address'] for vin in tx['vin'] if not is_coinbase]
        recipient_addresses = [vout['scriptpubkey_address'] for vout in tx['vout'] if vout['scriptpubkey_type'] not in ignore_type]
        cleaned_txs.append({
            'block_height': block_height,
            'txid': tx_id,
            'vin_count': vin_count,
            'vout_count': vout_count,
            'total_input_value': total_input_value,
            'total_output_value': total_output_value,
            'fee': fee,
            'sender_addresses': sender_addresses,
            'recipient_addresses': recipient_addresses,
            'is_coinbase': is_coinbase
        })
    return cleaned_txs

def fetch_block_transactions(**context):
    latest_block_hash = get_latest_block_hash()
    block_data = get_block_by_hash(latest_block_hash)
    latest_block_height = block_data[0]["height"]
    block_transactions = get_all_transactions_by_block_hash(latest_block_hash)
    save_txs_to_json(block_transactions, f'data/raw_blocks/block_{latest_block_height}.json')
    return latest_block_height

def extract_transactions_data(raw_block_transactions_df, block_height):
    ignore_type = ['op_return', 'unknown']
    transactions_df = raw_block_transactions_df.copy()
    transactions_df['block_height'] = block_height
    transactions_df['timestamp'] = transactions_df['status'].apply(lambda x: x.get('block_time', None))
    transactions_df['vin_count'] = transactions_df['vin'].apply(len)
    transactions_df['vout_count'] = transactions_df['vout'].apply(len)
    transactions_df['is_coinbase'] = transactions_df['vin'].apply(lambda x: x[0]['is_coinbase'])
    transactions_df['total_input_value'] = transactions_df['vin'].apply(lambda x: sum(v['prevout']['value'] for v in x if not v['is_coinbase']))
    transactions_df['total_output_value'] = transactions_df['vout'].apply(lambda x: sum(v['value'] for v in x))
    transactions_df['sender_addresses'] = transactions_df['vin'].apply(lambda x: [v['prevout']['scriptpubkey_address'] for v in x if not v['is_coinbase']])
    transactions_df['recipient_addresses'] = transactions_df['vout'].apply(lambda x: [v['scriptpubkey_address'] for v in x if v['scriptpubkey_type'] not in ignore_type])
    transactions_df['scriptpubkey_types'] = transactions_df['vout'].apply(lambda x: list(set(v['scriptpubkey_type'] for v in x)))
    transactions_df['is_whale'] = transactions_df['total_output_value'].apply(lambda v: v >= 100 * 100_000_000)  # 100 BTC
    cols = ['txid', 'block_height', 'timestamp', 'vin_count', 'vout_count', 'is_coinbase', 'total_input_value', 'total_output_value',
            'fee', 'sender_addresses', 'recipient_addresses', 'scriptpubkey_types', 'is_whale']
    transactions_df = transactions_df[cols]
    return transactions_df

def extract_inputs_data(raw_block_transactions_df):
    inputs_data = []
    for tx in raw_block_transactions_df.to_dict('records'):
        for i, vin in enumerate(tx['vin']):
            if vin['is_coinbase']:
                inputs_data.append({
                    'txid': tx['txid'],
                    'input_index': i,
                    'prev_txid': None,
                    'prev_vout_index': None,
                    'address': None,
                    'value': None,
                    'scriptpubkey_type': None,
                    'is_coinbase': True
                })
            else:
                inputs_data.append({
                    'txid': tx['txid'],
                    'input_index': i,
                    'prev_txid': vin['txid'],
                    'prev_vout_index': vin['vout'],
                    'address': vin['prevout'].get('scriptpubkey_address'),
                    'value': vin['prevout'].get('value'),
                    'scriptpubkey_type': vin['prevout'].get('scriptpubkey_type'),
                    'is_coinbase': False
                })
    inputs_df = pd.DataFrame(inputs_data)
    return inputs_df

def extract_outputs_data(raw_block_transactions_df):
    outputs_data = []
    for tx in raw_block_transactions_df.to_dict('records'):
        for i, vout in enumerate(tx['vout']):
            outputs_data.append({
            'txid': tx['txid'],
            'output_index': i,
            'address': vout.get('scriptpubkey_address'),
            'value': vout['value'],
                'scriptpubkey_type': vout.get('scriptpubkey_type')
            })
    outputs_df = pd.DataFrame(outputs_data)
    return outputs_df

def save_df_to_db(df, table_name, engine, index_columns):
    rows_to_insert = df.to_dict(orient='records')
    stmt = insert(table_name).values(rows_to_insert)
    stmt = stmt.on_conflict_do_nothing(index_elements=index_columns)

    with engine.begin() as conn:
        conn.execute(stmt)


def clean_and_store_transactions(**context):
    latest_block_height = context['task_instance'].xcom_pull(task_ids='fetch_block_transactions')
    raw_block_transactions_df = pd.read_json(f'data/raw_blocks/block_{latest_block_height}.json')
    db_user = 'airflow'
    db_pass = 'airflow'
    db_host = 'postgres'  # docker-compose service name
    db_port = '5432'
    db_name = 'whale_db'
    engine = create_engine(f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')

    # extract transactions data
    transactions_df = extract_transactions_data(raw_block_transactions_df, latest_block_height)
    print(f'Cleaned {latest_block_height} block with {transactions_df.shape[0]} transactions')
    save_df_to_db(transactions_df, Transactions.__table__, engine, ['txid'])

    # extract inputs data
    inputs_df = extract_inputs_data(raw_block_transactions_df)
    print(f'Cleaned {latest_block_height} block with {inputs_df.shape[0]} inputs')
    save_df_to_db(inputs_df, Inputs.__table__, engine, ['txid', 'input_index'])

    # extract outputs data
    outputs_df = extract_outputs_data(raw_block_transactions_df)
    print(f'Cleaned {latest_block_height} block with {outputs_df.shape[0]} outputs')
    save_df_to_db(outputs_df, Outputs.__table__, engine, ['txid', 'output_index'])
    return latest_block_height


def save_txs_to_json(txs, file_name):
    with open(file_name, 'w') as f:
        json.dump(txs, f)




if __name__ == "__main__":
    # latest_block_hash = get_latest_block_hash()
    # print(latest_block_hash)

    # block_data = get_block_by_hash(latest_block_hash)
    # print(f'block {latest_block_hash} has {block_data[0]["tx_count"]} transactions')
    # latest_block_height = block_data[0]["height"]

    # block_transactions = get_all_transactions_by_block_hash(latest_block_hash)
    # print(f'block {latest_block_hash} has {len(block_transactions)} transactions')

    # # save raw txs to json
    # save_txs_to_json(block_transactions, f'data/raw_blocks/block_{latest_block_height}.json')

    # # clean txs
    # cleaned_txs = clean_txs(block_transactions, latest_block_height)
    # save_txs_to_json(cleaned_txs, f'data/cleaned_blocks/block_{latest_block_height}.json')

    latest_block_height = fetch_block_transactions(tx_count=100)
    context = {}
    context['task_instance'] = latest_block_height
    clean_and_store_transactions(latest_block_height)