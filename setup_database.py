import os
import kagglehub

# Copy the exact string from your Kaggle screen here:
os.environ['KAGGLE_USERNAME'] = "justinalde" 
os.environ['KAGGLE_KEY'] = "KGAT_b86a99ec27e313e87734ac7cccd1fd3cd"

# Now run the download
path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
print("Data is located at:", path)