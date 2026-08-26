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
    print("Starting schema optimization and constraint enforcement...")
    
    # This function opens an "all-or-nothing" transaction. 
    # If something breaks mid-script. Postgres rolls back every change, so we don't end up with a half-broken data base
    
    with engine.begin() as conn:
        # ----------------------------------------------------------
        # Convert text dates into actual TIMESTAMP columns, Pandas load everything as string by defualt.
        # Convert them so we can use them for calculation and filter by date
        # ----------------------------------------------------------

        print("Converting string columns to proper Postgres TIMESTAMPs...")
        conn.execute(
            text(""" 
             ALTER TABLE orders
                ALTER COLUMN order_purchase_timestamp TYPE TIMESTAMP using order_purchase_timestamp::TIMESTAMP, 
                ALTER COLUMN order_approved_at TYPE TIMESTAMP using order_approved_at::TIMESTAMP, 
                ALTER COLUMN order_delivered_carrier_date TYPE TIMESTAMP using order_delivered_carrier_date::TIMESTAMP,  
                ALTER COLUMN order_delivered_customer_date TYPE TIMESTAMP using order_delivered_customer_date::TIMESTAMP, 
                ALTER COLUMN order_estimated_delivery_date TYPE TIMESTAMP using order_estimated_delivery_date::TIMESTAMP;
                 
            ALTER TABLE order_items
                ALTER COLUMN shipping_limit_date TYPE TIMESTAMP using shipping_limit_date::TIMESTAMP;
            
            ALTER TABLE order_reviews
                ALTER COLUMN review_creation_date TYPE TIMESTAMP using review_creation_date::TIMESTAMP, 
                ALTER COLUMN review_answer_timestamp TYPE TIMESTAMP using review_answer_timestamp::TIMESTAMP;
                """)
        )
        
        # --------------------------------------------
        # Add Primary Keys (PKs)
        # PKs guarantee every row is unique and auto-build B-Tree indexes
        # behind the scens for fast $0(/log N)$ lookups.
        # --------------------------------------------
        print("Setting Primary Keys on core tables...")

        # Single-column primary keys
        conn.execute(text("ALTER TABLE orders ADD PRIMARY KEY (order_id);"))
        conn.execute(
            text("ALTER TABLE customers ADD PRIMARY KEY (customer_id);")
        )
        conn.execute(
            text("ALTER TABLE products ADD PRIMARY KEY (product_id);")
        )
        conn.execute(text("ALTER TABLE sellers ADD PRIMARY KEY (seller_id);"))

        # Multi-item orders require order_id + order_item_id
        conn.execute(
            text(
                "ALTER TABLE order_items ADD PRIMARY KEY (order_id,"
                " order_item_id);"
            )
        )

        # Split payments require order_id + payment_sequential
        conn.execute(
            text(
                "ALTER TABLE order_payments ADD PRIMARY KEY (order_id,"
                " payment_sequential);"
            )
        )

        # Shared reviews require review_id + order_id
        conn.execute(
            text(
                "ALTER TABLE order_reviews ADD PRIMARY KEY (review_id,"
                " order_id);"
            )
        )
        # ---------------------------------------------------
        # Add Foreign Keys 
        # Links child tables back to parent tables. Stops "ghost" records, like items that reference an order that doesn't exist.
        # ---------------------------------------------------
        print("Hooking up Foreign Key relationships...")
        conn.execute(
            text("""
            ALTER TABLE orders
                ADD CONSTRAINT fk_orders_customers
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
                
            ALTER TABLE order_items
                ADD CONSTRAINT fkn_order_items_order
                FOREIGN KEY (order_id) REFERENCES orders(order_id),     
                ADD CONSTRAINT fkn_order_items_products
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                ADD CONSTRAINT fk_order_items_sellers
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id);
                 
            ALTER TABLE order_payments
                ADD CONSTRAINT fk_order_payments_orders
                FOREIGN KEY (order_id) REFERENCES orders(order_id);
            
            ALTER TABLE order_reviews
                ADD CONSTRAINT fk_order_reviews_orders
                FOREIGN KEY (order_id) REFERENCES orders(order_id);
                 
                 """)
        )
        
    print(" Done! Schema optimized and referential integrity enforced.")
    
if __name__ == "__main__":
    optimize_schema()
        

    