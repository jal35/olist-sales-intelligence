import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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

def optimize_schema():
    ddl_statements = [
        # 1. Cast string dates to native PostgreSQL Timestamps
        "ALTER TABLE orders ALTER COLUMN order_purchase_timestamp TYPE TIMESTAMP USING order_purchase_timestamp::TIMESTAMP;",
        "ALTER TABLE orders ALTER COLUMN order_approved_at TYPE TIMESTAMP USING order_approved_at::TIMESTAMP;",
        "ALTER TABLE orders ALTER COLUMN order_delivered_carrier_date TYPE TIMESTAMP USING order_delivered_carrier_date::TIMESTAMP;",
        "ALTER TABLE orders ALTER COLUMN order_delivered_customer_date TYPE TIMESTAMP USING order_delivered_customer_date::TIMESTAMP;",
        "ALTER TABLE orders ALTER COLUMN order_estimated_delivery_date TYPE TIMESTAMP USING order_estimated_delivery_date::TIMESTAMP;",
        "ALTER TABLE order_items ALTER COLUMN shipping_limit_date TYPE TIMESTAMP USING shipping_limit_date::TIMESTAMP;",
        "ALTER TABLE order_reviews ALTER COLUMN review_creation_date TYPE TIMESTAMP USING review_creation_date::TIMESTAMP;",
        "ALTER TABLE order_reviews ALTER COLUMN review_answer_timestamp TYPE TIMESTAMP USING review_answer_timestamp::TIMESTAMP;",

        # 2. Define Primary Keys
        "ALTER TABLE orders ADD PRIMARY KEY (order_id);",
        "ALTER TABLE customers ADD PRIMARY KEY (customer_id);",
        "ALTER TABLE products ADD PRIMARY KEY (product_id);",
        "ALTER TABLE sellers ADD PRIMARY KEY (seller_id);",

        # 3. Define Foreign Keys
        "ALTER TABLE orders ADD CONSTRAINT fk_orders_customers FOREIGN KEY (customer_id) REFERENCES customers(customer_id);",
        "ALTER TABLE order_items ADD CONSTRAINT fk_items_orders FOREIGN KEY (order_id) REFERENCES orders(order_id);",
        "ALTER TABLE order_items ADD CONSTRAINT fk_items_products FOREIGN KEY (product_id) REFERENCES products(product_id);",
        "ALTER TABLE order_items ADD CONSTRAINT fk_items_sellers FOREIGN KEY (seller_id) REFERENCES sellers(seller_id);",
        "ALTER TABLE order_payments ADD CONSTRAINT fk_payments_orders FOREIGN KEY (order_id) REFERENCES orders(order_id);",
        "ALTER TABLE order_reviews ADD CONSTRAINT fk_reviews_orders FOREIGN KEY (order_id) REFERENCES orders(order_id);"
    ]

    print("Applying schema optimizations (timestamps, primary keys, foreign keys)...")
    
    # Execute all DDL changes in a single atomic transaction
    with engine.begin() as connection:
        for statement in ddl_statements:
            connection.execute(text(statement))
            
    print("Schema optimization complete.")

if __name__ == "__main__":
    optimize_schema()