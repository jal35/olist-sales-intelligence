import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

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

def clean_table_name(filename: str) -> str:
    base_name = filename.replace(".csv", "")
    cleaned = base_name.replace("olist_", "").replace("_dataset", "")
    return cleaned
    
def load_csv_to_postgres():
    data_dir = Path("./olist_dataset")
    
    if not data_dir.exists():
        print("Dataset directory not found. Run setup_database.py first.")
        return
    
    for csv_file in data_dir.glob("*.csv"):
        table_name = clean_table_name(csv_file.name)
        print(f"Loading {csv_file} into table '{table_name}'...")
        
        df = pd.read_csv(csv_file)
        
        df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
        
        print(f"Sucessfully loaded {len(df)} rows into '{table_name}'.")
        
if __name__ == "__main__":
    load_csv_to_postgres()


    