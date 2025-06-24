from sqlalchemy import Column, String, Integer, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Outputs(Base):
    __tablename__ = 'outputs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    txid = Column(String, nullable=False)
    output_index = Column(Integer, nullable=False)
    address = Column(String)
    value = Column(Float, nullable=False)
    scriptpubkey_type = Column(String)

    __table_args__ = (
        UniqueConstraint('txid', 'output_index', name='uix_txid_output_index'),
    )
