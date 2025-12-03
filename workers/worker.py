import json
import pandas as pd
import os

from storage_minio import download_from_minio

# --- IMPORT DRIFT FUNCTIONS ---
from workers.compute import compute_all
from drift_detection import *

# --- IMPORT DB FUNCTIONS ---
import db   # since db.py contains functions, NOT a class

# --- GOOGLE PUBSUB ---
from google.cloud import pubsub_v1

PROJECT_ID = "focus-mechanic-474016-s2"
SUBSCRIPTION_NAME = "drift_jobs_sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

print(f"[WORKER] Using subscription: {subscription_path}")
print("[WORKER] Worker ready.")

def process_job(job):
    bucket = job["bucket"]
    baseline_key = job["baseline_key"]
    drift_key = job["drift_key"]

    os.makedirs("worker_tmp", exist_ok=True)

    baseline_local = os.path.join("worker_tmp", os.path.basename(baseline_key))
    drift_local = os.path.join("worker_tmp", os.path.basename(drift_key))

    print(f"[WORKER] Downloading baseline: {baseline_key}")
    download_from_minio(bucket, baseline_key, baseline_local)

    print(f"[WORKER] Downloading drift: {drift_key}")
    download_from_minio(bucket, drift_key, drift_local)

    baseline_df = pd.read_csv(baseline_local, header=None)
    drift_df = pd.read_csv(drift_local, header=None)

    baseline_texts = baseline_df[baseline_df.columns[0]].astype(str).tolist()
    drift_texts = drift_df[drift_df.columns[0]].astype(str).tolist()

    # ----------------------------------------------------
    # CALL YOUR UNIFIED compute_all()
    # ----------------------------------------------------
    dataset_name = drift_key.split("/")[-1]

    metrics = compute_all(baseline_texts, drift_texts, dataset_name)

    print("\n[WORKER] DRIFT METRICS:")
    print(metrics)

    # ----------------------------------------------------
    # SAVE METRICS TO POSTGRES
    # ----------------------------------------------------
    db.create_table_if_not_exists()      # correct function name
    db.insert_metrics(metrics)

    print("[WORKER] Metrics saved to database.")

def callback(message):
    print("\n[WORKER] Received message")
    job = json.loads(message.data.decode("utf-8"))

    process_job(job)
    message.ack()
    print("[WORKER] Message processed & acknowledged.")

def main():
    print("[WORKER] Listening for messages...")
    subscriber.subscribe(subscription_path, callback=callback)

    # Keep alive
    while True:
        import time
        time.sleep(60)

if __name__ == "__main__":
    main()
