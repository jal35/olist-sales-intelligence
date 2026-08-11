import os
import pandas as pd
from sqlalchemy import create_engine

"""
CONNECTION DETAILS
# Use my PostgresSQL password for installation
"""
DB_PASS = 'Crafted6on$'
DB_NAME = 'olist_db'
engine = create_engine(f'postgresql://postgres:{DB_PASS}@localhost:5432/{DB_NAME}')

"""
THE DATA PATH
Point to the data set folders
"""

csv_folder =r'C:\Users\Justin\Projects\Olist\olist_dataset'

def ingest_data():
    print("Beginning to move to PostgresSQL")
    
    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_folder, filename)
            
            # Make table names
            table_name = filename.replace('.csv', '')
            
            print(f"Reading{filename}...")
            df = pd.read_csv(file_path)
            
            print(f"Pushing {len(df)} rows to table '{table_name}")
            # Using repalce, we check if it is ran twice, then refresh
            df.to_sql(table_name, engine, if_exists='replace', index=False)     
    print("\n Succesful download. All data is now in PostgreSQL")
    
    
if __name__ == "__main__":
    ingest_data()
    
    