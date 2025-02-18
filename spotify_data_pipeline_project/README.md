# 🚀 **End-to-End ETL Data Pipeline with API, Python & AWS**

## 🛠️ **Project Overview**

I developed a fully automated **ETL (Extract, Transform, Load) data pipeline** using **Python, Kaggle API and AWS services**. This project demonstrates the process of gathering, transforming and analyzing Spotify data, illustrating how cloud-based infrastructure can streamline data workflows. The pipeline follows industry best practices to manage datasets, perform transformations and provide data for business intelligence to generate insights.

---

## ⚙️ **Pipeline Architecture**

The architecture consists of seven key stages:

1. **Data Collection:** Python script utilizing Kaggle API to download datasets.
2. **Data Processing:** Python code to clean and transform data.
3. **Cloud Storage:** Processed data uploaded to AWS S3.
4. **ETL Operations:** AWS Glue job written in PySpark to join and refine tables.
5. **Metadata Generation:** AWS Glue Crawler for schema discovery.
6. **SQL Queries:** Amazon Athena to execute analytical queries.
7. **Data Visualization:** Amazon QuickSight to prepare the data for dashboards.

---

## 🧩 **AWS Services Used**

- 🚀 **Amazon S3**: Centralized object storage for raw, processed, and final datasets.
- 🔍 **AWS Glue**: ETL engine for data transformation using PySpark.
- ⚙️ **AWS Glue Crawler**: Automated metadata extraction for query readiness.
- 🛠️ **Amazon Athena**: Serverless SQL query execution on S3-based datasets.
- 📊 **Amazon QuickSight**: Business intelligence tool for dashboard creation.

---

## 🔍 **Step-by-Step Breakdown**

### 🌐 **1️⃣ Data Collection via Kaggle API**

**Objective:** Automate the data ingestion process by programmatically retrieving datasets from Kaggle.

**Explanation:**
- Used **Kaggle API** to download datasets without manual intervention.
- Defined reusable functions for scalability.
- Ensured extraction into a predefined directory structure.

**Code Implementation:**
```python
from kaggle.api.kaggle_api_extended import KaggleApi
import os

# Configure download path
DATA_PATH = "./data"
os.makedirs(DATA_PATH, exist_ok=True)

# Download dataset
def download_kaggle_dataset(dataset):
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(dataset, path=DATA_PATH, unzip=True)
    print("✅ Dataset downloaded and extracted.")

download_kaggle_dataset("tonygordonjr/spotify-dataset-2023")
```

📖 **Why:** Automated data ingestion eliminates manual downloads, ensuring real-time updates when required.

---

### 🧼 **2️⃣ Data Preprocessing with Python**

**Objective:** Clean and prepare raw data for cloud storage.

**Explanation:**
- Utilized **Pandas** to handle CSV files.
- Filtered relevant columns to reduce unnecessary storage.
- Standardized data formatting for consistency.

**Code Implementation:**
```python
import pandas as pd

def process_spotify_data():
    tracks = pd.read_csv("./data/tracks.csv")[["id", "name", "popularity"]]
    albums = pd.read_csv("./data/albums.csv")[["id", "album_name", "release_date"]]
    artists = pd.read_csv("./data/artists.csv")[["id", "name"]]

    tracks.to_csv("./data/processed_tracks.csv", index=False)
    albums.to_csv("./data/processed_albums.csv", index=False)
    artists.to_csv("./data/processed_artists.csv", index=False)

process_spotify_data()
```

📖 **Why:** Pre-processing reduces unnecessary data load, improving performance during downstream ETL steps.

---

### ☁️ **3️⃣ Upload Processed Data to Amazon S3**

**Objective:** Transfer cleaned data to AWS S3.

**Explanation:**
- Established connection using **boto3**.
- Organized files into distinct directories for clarity.
- Ensured idempotent uploads for consistent storage state.

**Code Implementation:**
```python
import boto3
import os

bucket_name = "spotify-automation-project-bucket"
s3 = boto3.client('s3')

for file in os.listdir("./data"):
    s3.upload_file(f"./data/{file}", bucket_name, f"spotify-staging/{file}")
```

📖 **Why:** Centralized cloud storage ensures data availability for distributed services.

---

### 🔄 **4️⃣ ETL with AWS Glue**

**Objective:** Transform raw data into queryable datasets.

**Explanation:**
- Implemented ETL jobs using **AWS Glue** with **PySpark**.
- Joined tables based on shared keys.
- Removed extraneous fields to optimize queries.
- Stored final datasets in **Parquet** for efficient I/O.

**Code Implementation:**
```python
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

artist = glueContext.create_dynamic_frame.from_options(
    connection_type="s3", format="csv",
    connection_options={"paths": ["s3://spotify-automation-project-bucket/spotify-staging/processed_artists.csv"]},
    format_options={"withHeader": True, "separator": ","}
)

album = glueContext.create_dynamic_frame.from_options(
    connection_type="s3", format="csv",
    connection_options={"paths": ["s3://spotify-automation-project-bucket/spotify-staging/processed_albums.csv"]},
    format_options={"withHeader": True, "separator": ","}
)

track = glueContext.create_dynamic_frame.from_options(
    connection_type="s3", format="csv",
    connection_options={"paths": ["s3://spotify-automation-project-bucket/spotify-staging/processed_tracks.csv"]},
    format_options={"withHeader": True, "separator": ","}
)

joined = Join.apply(album, artist, keys1=["id"], keys2=["id"])
final_data = Join.apply(joined, track, keys1=["id"], keys2=["id"])

# Write to S3 in Parquet format
glueContext.write_dynamic_frame.from_options(
    frame=final_data,
    connection_type="s3", format="glueparquet",
    connection_options={"path": "s3://spotify-datawarehouse/"},
    format_options={"compression": "snappy"}
)
```

📖 **Why:** PySpark's distributed processing accelerates large-scale transformations.

---

### 🧠 **5️⃣ Metadata Generation with AWS Glue Crawler**

**Objective:** Automatically generate schema information.

**Explanation:**
- Configured **AWS Glue Crawler** to scan Parquet files.
- Created metadata for querying in **Amazon Athena**.
- Enabled regular crawler runs for schema consistency.

📖 **Why:** Glue Crawlers streamline schema discovery, reducing manual effort.

---

### 📖 **6️⃣ Querying with Amazon Athena**

**Objective:** Run analytical SQL queries.

**Explanation:**
- Connected Athena to the Glue Data Catalog.
- Used SQL to analyze music trends.

**Sample Query:**
```sql
SELECT album_name, AVG(track_popularity) AS avg_popularity
FROM spotify_database.spotify_datawarehouse
GROUP BY album_name
ORDER BY avg_popularity DESC
LIMIT 10;
```

📖 **Why:** Athena's serverless design eliminates infrastructure overhead.

---

### 📊 **7️⃣ Data Visualization with Amazon QuickSight**

**Objective:** Generate interactive dashboards.

**Explanation:**
- Established connections to **Athena** and **S3**.
- Built dashboards to showcase artist popularity and album trends.

📖 **Why:** QuickSight provides dynamic visuals for non-technical audiences.

---

## 🎯 **Project Outcomes**

- 🔹 **Seamless Automation:** From data collection to visualization.
- 🔹 **Efficient Data Transformation:** ETL jobs executed using PySpark.
- 🔹 **Optimized Performance:** Queries accelerated with Parquet storage.
- 🔹 **Cloud Integration:** All components deployed using AWS services.

---
