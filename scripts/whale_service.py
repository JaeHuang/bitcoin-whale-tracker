from sqlalchemy import create_engine, text

class WhaleService:
    def __init__(self) -> None:
        db_user = 'airflow'
        db_pass = 'airflow'
        db_host = 'postgres'  # docker-compose service name
        db_port = '5432'
        db_name = 'whale_db'
        self.engine = create_engine(f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')
    
    def get_address_balance(self, address: str):
        query = text("""
            SELECT COALESCE(SUM(o.value), 0) AS balance
            FROM outputs o
            LEFT JOIN inputs i
            ON o.txid = i.prev_txid AND o.output_index = i.prev_vout_index
            WHERE o.address = :address AND i.txid IS NULL;
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query, {"address": address})
            return result.scalar()

        
    

if __name__ == '__main__':
    whale_service = WhaleService()
    test_address = 'bc1ppxt9j958t422zyl0vvjw777a6u8m0ljwmkk3vuh0uknnx8gru3xqhxms85'
    result = whale_service.get_address_balance(test_address)
    print(result)