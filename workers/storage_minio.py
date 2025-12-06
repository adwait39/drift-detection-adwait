# storage_minio.py
from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv
load_dotenv()
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_SECURE = False                       # http, not https

def get_minio_client():
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )
    return client

def upload_to_minio(bucket_name: str, local_path: str, object_name: str) -> str:
    """
    Uploads local_path → bucket/object_name on MinIO.
    Returns a pseudo-uri like minio://bucket/object_name
    """
    client = get_minio_client()

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    client.fput_object(bucket_name, object_name, local_path)
    uri = f"minio://{bucket_name}/{object_name}"
    print(f"[MINIO] Uploaded {local_path} -> {uri}")
    return uri

def download_from_minio(bucket_name: str, object_name: str, local_path: str) -> None:
    """
    Downloads bucket/object_name → local_path from MinIO.
    """
    client = get_minio_client()
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    client.fget_object(bucket_name, object_name, local_path)
    print(f"[MINIO] Downloaded minio://{bucket_name}/{object_name} -> {local_path}")
