# Bitcoin Whale Tracker

An end-to-end data pipeline for tracking Bitcoin whale activity using public blockchain data.

This project fetches data from the Blockstream API, processes it via Python & Airflow, transforms it with DBT, stores it in PostgreSQL, and exposes a query API through FastAPI.

---

## Project Structure

```
bitcoin-whale-tracker/
├── dags/               # Airflow DAGs
├── scripts/            # Python scripts for ETL & services
├── whale_dbt/          # DBT project (sources, staging models)
├── api/                # FastAPI app (whale API)
├── docker/             # Dockerfile, docker-compose, init SQL
```

---

## Prerequisites

- Docker & Docker Compose
- Python 3.9+ (only if running scripts locally)

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/JaeHuang/bitcoin-whale-tracker.git
cd bitcoin-whale-tracker

# 2. Start all services
docker compose -f docker/docker-compose.yaml up --build -d

# 3. Verify services are running:
# - Airflow:       http://localhost:8080
# - FastAPI:       http://localhost:8000/docs
# - PostgreSQL:    localhost:5432 (user: airflow, db: whale_db)
```

---

## Features

- Sync latest Bitcoin blocks and transactions
- Normalize inputs, outputs, and UTXO state
- Classify and aggregate whale transactions (e.g. > 100 BTC)
- API endpoints to query address balance, activity count, etc.
- Data transformations via DBT with test coverage

---

## Sample API Usage

### Get Address Balance

```http
GET /address/balance/{address}
```

Example:

```
GET http://localhost:8000/address/balance/bc1qexample123
```

### Get Address Activity Count

```http
GET /address/activity/{address}
```

---

## DBT Models

- `stg_outputs`: Normalized outputs with BTC values
- `stg_transactions`: Transaction metadata with derived fields
- Additional models: `daily_whale_tx`, `balance_change_stats` (coming soon)

Run DBT manually:

```bash
# Inside the container or with proper profile
cd whale_dbt
dbt run
```

---

## Airflow Tasks

- `fetch_latest_block`: fetch latest block data
- `parse_transactions`: extract & clean raw tx info
- `sync_to_db`: load into PostgreSQL
- (Optional) trigger DBT transforms

---

## License

MIT © Jae Huang

