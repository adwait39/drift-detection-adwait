import os
from pathlib import Path
from minio import Minio


MINIO_ENDPOINT = "localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
DRIFT_BUCKET_NAME = "drift-datasets"  
LOCAL_DIR = Path("../data/drift_sets")   


client = Minio(
    MINIO_ENDPOINT,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False
)

if not client.bucket_exists(DRIFT_BUCKET_NAME):
    client.make_bucket(DRIFT_BUCKET_NAME)
    print(f"✔ Bucket created: {DRIFT_BUCKET_NAME}")
else:
    print(f"✔ Bucket already exists: {DRIFT_BUCKET_NAME}")



files_uploaded = 0
print("hello")
print(f"{LOCAL_DIR}")
for file in LOCAL_DIR.glob("*.csv"):
    object_name = file.name  
    print(f"⏫ Uploading: {object_name}... ", end="")
    
    client.fput_object(
        DRIFT_BUCKET_NAME,
        object_name,
        str(file)
    )

    print(f"📤 Uploaded: {object_name}")
    files_uploaded += 1

print("\n------------------------------------")
print(f"🎉 Upload Complete — {files_uploaded} files uploaded to bucket '{DRIFT_BUCKET_NAME}'")
print("------------------------------------")
