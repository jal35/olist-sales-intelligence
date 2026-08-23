import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
import kagglehub

load_dotenv()

def download_and_organize_dataset():
    target_dir = Path("./olist_dataset")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading dataset from Kaggle...")
    download_path = Path(kagglehub.dataset_download("olistbr/brazilian-ecommerce"))
    
    print(f"Moving files to {target_dir.resolve()}...")
    for file in download_path.glob("*.csv"):
        shutil.copy(file, target_dir / file.name)
        
    print("Dataset setup complete.")
    
if __name__ == "__main__":
    download_and_organize_dataset()
