from sqlalchemy import Column, String, Integer, Float, UniqueConstraint, Boolean, BigInteger, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    txid = Column(String, nullable=False)
    block_height = Column(Integer, nullable=False)
    vin_count = Column(Integer, nullable=True)
    vout_count = Column(Integer, nullable=True)
    is_coinbase = Column(Boolean, nullable=True)
    total_input_value = Column(BigInteger, nullable=True)
    total_output_value = Column(BigInteger, nullable=True)
    fee = Column(BigInteger, nullable=True)
    sender_addresses = Column(ARRAY(String), nullable=True)
    recipient_addresses = Column(ARRAY(String), nullable=True)
    scriptpubkey_types = Column(ARRAY(String), nullable=True)
    is_whale = Column(Boolean, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint('txid', name='uix_txid'),
    )
