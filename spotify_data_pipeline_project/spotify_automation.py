import os
import pandas as pd
import boto3
from kaggle.api.kaggle_api_extended import KaggleApi

# ================================
# Part 1: Setup and Configurations
# ================================

# Define paths for data handling
DOWNLOAD_PATH = "./data"  # Path to download raw data
PROCESSED_PATH = "./processed"  # Path to store processed data

# AWS S3 Configuration
S3_BUCKET_NAME = "your-s3-bucket-name"  # Replace with your S3 bucket name
S3_FOLDER = "spotify-staging"  # Folder in S3 to store processed data

# Ensure necessary directories exist
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(PROCESSED_PATH, exist_ok=True)


# ================================
# Part 2: Download and Process Data
# ================================
"""
Downloads the dataset from Kaggle using the Kaggle API and unzips it into the DOWNLOAD_PATH directory.
"""
def download_kaggle_dataset(dataset_url):
    
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(dataset_url, path=DOWNLOAD_PATH, unzip=True)
    print("Dataset downloaded and unzipped.")

"""
Processes raw data files from the input folder and saves the cleaned files into the output folder.
Retains only relevant columns as specified for each dataset.
"""
def process_files(input_folder, output_folder):
    
    # Process spotify_features_data_2023.csv
    features_file = os.path.join(input_folder, "spotify_features_data_2023.csv")
    features_df = pd.read_csv(features_file, low_memory=False)
    features_df.to_csv(os.path.join(output_folder, "features.csv"), index=False)

    # Process spotify_tracks_data_2023.csv
    tracks_file = os.path.join(input_folder, "spotify_tracks_data_2023.csv")
    tracks_df = pd.read_csv(tracks_file, low_memory=False)
    tracks_df = tracks_df[["id", "track_popularity"]]  # Retain only required columns
    tracks_df.to_csv(os.path.join(output_folder, "tracks.csv"), index=False)

    # Process spotify_data_12_20_2023.csv
    spotify_data_file = os.path.join(input_folder, "spotify_data_12_20_2023.csv")
    spotify_data_df = pd.read_csv(spotify_data_file, low_memory=False)
    spotify_data_df.to_csv(os.path.join(output_folder, "data.csv"), index=False)

    # Process spotify_artist_data_2023.csv
    artist_file = os.path.join(input_folder, "spotify_artist_data_2023.csv")
    artist_df = pd.read_csv(artist_file, low_memory=False)
    artist_df = artist_df[["id", "name", "artist_popularity", "followers", "genre_0"]]
    artist_df.to_csv(os.path.join(output_folder, "artist.csv"), index=False)

    # Process spotify-albums_data_2023.csv
    albums_file = os.path.join(input_folder, "spotify-albums_data_2023.csv")
    albums_df = pd.read_csv(albums_file, low_memory=False)
    albums_df = albums_df[
        ["track_name", "track_id", "duration_ms", "album_name", "release_date", "label",
         "album_popularity", "album_id", "artist_id", "duration_sec"]
    ]
    albums_df.to_csv(os.path.join(output_folder, "albums.csv"), index=False)

    print("Files processed and saved to output folder.")


# ================================
# Part 3: Upload Processed Data to S3
# ================================
"""
Uploads all files from the folder_path to the specified S3 bucket and folder.
Each file is uploaded as a separate object under the S3 folder.
"""

def upload_files_to_s3(folder_path, bucket_name, s3_folder):
    s3 = boto3.client('s3')  # Use AWS credentials from AWS CLI configuration
    for root, _, files in os.walk(folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)  # Full path to the local file
            s3_key = f"{s3_folder}/{file}"  # Ensure the S3 key includes the folder name
            s3.upload_file(local_file_path, bucket_name, s3_key)
            print(f"Uploaded {file} to s3://{bucket_name}/{s3_key}")


# ================================
# Part 4: Main Function
# ================================
'''
Main function to orchestrate the data automation workflow:
1. Download the kaggle dataset
2. Processes the raw data
3. Uploads the processed data to the s3 bucket in the spotify-staging folder
'''

def main():
    dataset_url = "tonygordonjr/spotify-dataset-2023" # kaggle dataset url

    download_kaggle_dataset(dataset_url) # step 1 
    process_files(DOWNLOAD_PATH, PROCESSED_PATH) # step 2
    upload_files_to_s3(PROCESSED_PATH, S3_BUCKET_NAME, S3_FOLDER)

# Run the script
if __name__ == "__main__":
    main()

