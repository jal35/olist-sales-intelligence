import os 
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

# Load database credentials from .env
load_dotenv()

# Retrive database credentials securely
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "olist_db")

# Create the SQLAlchemy connection engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Expected database structure used for testing
EXPECTED_PKS = {
    "orders": ["order_id"],
    "customers": ["customer_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "order_items": ["order_id", "order_item_id"],
    "order_payments": ["order_id", "payment_sequential"],
    "order_reviews": ["review_id", "order_id"],  
}

EXPECTED_FKS = {
    "orders": ["customer_id"],
    "order_items": ["order_id", "product_id", "seller_id"],
    "order_payments": ["order_id"],
    "order_reviews": ["order_id"],  
}

EXPECTED_TIMESTAMPS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}

def verify_schema():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("---- Running Schema Verification ----")
    
    # Verify required tables exist
    for table in EXPECTED_PKS.keys():
        assert table in tables, f"Missing table: {table}"
    print("[PASS] All core tables exist.")
    
    # Verify primary key constraints
    for table, expected_pk in EXPECTED_PKS.items():
        pk_info = inspector.get_pk_constraint(table)
        actual_pk = pk_info["constrained_columns"]
        assert sorted(actual_pk) == sorted(expected_pk), (f"PK mismatch on {table}: expected {expected_pk}, got {actual_pk}")
    print("[PASS] Primary keys verified")
    
    # Verify foreign key constraints
    for table, expected_fk_cols in EXPECTED_FKS.items():
        fks = inspector.get_foreign_keys(table)
        actual_fk_cols = [
            col for fk in fks for col in fk["constrained_columns"]
        ] 
        for col in expected_fk_cols:
            assert col in actual_fk_cols, f"Missing FK on table{table}.{col}"
        ("[PASS] Foreign keys verified.")
        
    # Veirfy timestamp column data types
    for table, ts_cols in EXPECTED_TIMESTAMPS.items():
        columns = inspector.get_columns(table)
        col_types = {col["name"]: str(col["type"]) for col in columns}
        for col in ts_cols:
            assert "TIMESTAMP" in col_types[col], (
                f"Column {table}.{col} is not TIMESTAMP: {col_types[col]}"
            )
            ("[PASS] Timestamp data types verified.")
            
            ("\nSchema verification complete.")
            
if __name__ == "__main__":
    verify_schema()
        