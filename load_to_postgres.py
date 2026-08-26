import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load variables from .env into system memory
load_dotenv()

# Temporary debug check
print("DEBUG - Loaded DB_USER:", os.getenv("DB_USER"))
print("DEBUG - Loaded DB_NAME:", os.getenv("DB_NAME"))

# Retrive database credentials securely
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "olist_db")

# Create the SQLAlchemy connection engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Prefixes & suffixes to convert CSV filenames into clean SQL table names
def clean_table_name(filename: str) -> str:
    base_name = filename.replace(".csv", "")
    return base_name.replace("olist_", "").replace("_dataset", "")


def load_csv_to_postgres():
    data_dir = Path("./olist_dataset")

    if not data_dir.exists():
        print("Dataset directory not found.")
        return

    # Reset schema completely to clear existing tables and foreign key locks
    print("Wiping schema for clean re-ingestion...")
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))

    # Dynamically find and load all CSV files into Postgres
    for csv_file in data_dir.glob("*.csv"):
        if "product_category_name_translation" in csv_file.name:
            continue

        table_name = clean_table_name(csv_file.name)
        print(f"Loading {csv_file.name} into '{table_name}'...")

        df = pd.read_csv(csv_file)
        df.to_sql(
            name=table_name, con=engine, if_exists="replace", index=False
        )
        print(f"Loaded {len(df)} rows into '{table_name}'.")

    print("\nRaw CSV ingestion complete.")

if __name__ == "__main__":
    load_csv_to_postgres()