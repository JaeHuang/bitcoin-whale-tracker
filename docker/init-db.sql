CREATE DATABASE whale_db;

CREATE TABLE transactions (
    txid TEXT PRIMARY KEY,
    block_height INTEGER NOT NULL,
    vin_count INTEGER,
    vout_count INTEGER,
    is_coinbase BOOLEAN,
    total_input_value BIGINT,
    total_output_value BIGINT,
    fee BIGINT,
    sender_addresses TEXT[],        -- 陣列欄位：支援多個 address
    recipient_addresses TEXT[],     -- 同上
    scriptpubkey_types TEXT[],      -- 如：['p2pkh', 'p2wpkh']
    is_whale BOOLEAN,               -- 100 BTC 以上
    timestamp TIMESTAMP             -- 若你能從 API 抓 block_time
);

CREATE TABLE inputs (
    id SERIAL PRIMARY KEY,
    txid TEXT REFERENCES transactions(txid) ON DELETE CASCADE,
    input_index INTEGER,                 -- 第幾個 input
    prev_txid TEXT,                      -- 來源交易
    prev_vout_index INTEGER,
    address TEXT,
    value BIGINT,
    scriptpubkey_type TEXT,
    is_coinbase BOOLEAN
);

CREATE TABLE outputs (
    id SERIAL PRIMARY KEY,
    txid TEXT REFERENCES transactions(txid) ON DELETE CASCADE,
    output_index INTEGER,               -- 第幾個 output
    address TEXT,
    value BIGINT,
    scriptpubkey_type TEXT
);
