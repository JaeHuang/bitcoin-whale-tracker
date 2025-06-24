from sqlalchemy import Column, String, Integer, Float, UniqueConstraint, Boolean, BigInteger, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Inputs(Base):
    __tablename__ = 'inputs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    txid = Column(String, nullable=False)
    input_index = Column(Integer, nullable=False)
    prev_txid = Column(String, nullable=False)
    prev_vout_index = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    value = Column(BigInteger, nullable=False)
    scriptpubkey_type = Column(String, nullable=False)
    is_coinbase = Column(Boolean, nullable=False)

    __table_args__ = (
        UniqueConstraint('txid', 'input_index', name='uix_txid_input_index'),
    )
