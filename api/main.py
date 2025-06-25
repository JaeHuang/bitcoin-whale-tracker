from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from scripts.whale_service import WhaleService

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# 可從 ENV 或固定寫死（測試用）
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://airflow:airflow@postgres:5432/whale_db")
engine = create_engine(POSTGRES_URL)

whale_service = WhaleService()

@app.get("/balance/{address}")
def get_balance(address: str):
    balance = whale_service.get_address_balance(address)
    return {"address": address, "balance": f"{balance:,}"}

@app.get("/activity/{address}")
def get_activity(address: str):
    activity = whale_service.get_address_activity_count(address)[0]
    return {"address": address, "receive_count": activity[1], "send_count": activity[2], "total_activity": activity[3]}