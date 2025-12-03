import json
import pandas as pd
import os
import numpy as np

from storage_minio import download_from_minio
from sentence_transformers import SentenceTransformer

# --- GOOGLE PUBSUB ---
from google.cloud import pubsub_v1

PROJECT_ID = "focus-mechanic-474016-s2"
SUBSCRIPTION_NAME = "drift_jobs_sub"

# Correct way to build subscription path
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

print(f"[WORKER] Using subscription: {subscription_path}")
print("[WORKER] Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_drift(baseline_embeddings, drift_embeddings):
    baseline_mean = baseline_embeddings.mean(axis=0)
    drift_mean = drift_embeddings.mean(axis=0)

    cosine_similarity = np.dot(baseline_mean, drift_mean) / (
        np.linalg.norm(baseline_mean) * np.linalg.norm(drift_mean)
    )
    return 1 - cosine_similarity

def run_drift_detection(baseline_df, drift_df, job):
    print("\n[WORKER] Drift detection START")
    print("[WORKER] Job:", job)

    baseline_texts = baseline_df.iloc[:, 0].astype(str).tolist()
    drift_texts = drift_df.iloc[:, 0].astype(str).tolist()

    baseline_embeddings = model.encode(baseline_texts)
    drift_embeddings = model.encode(drift_texts)

    drift_score = compute_drift(baseline_embeddings, drift_embeddings)

    print(f"[WORKER] DRIFT SCORE = {drift_score:.4f}")
    if drift_score > 0.15:
        print("[WORKER] 🚨 HIGH DRIFT DETECTED!")
    else:
        print("[WORKER] Drift within normal range.")

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

    baseline_df = pd.read_csv(baseline_local)
    drift_df = pd.read_csv(drift_local)

    run_drift_detection(baseline_df, drift_df, job)

def callback(message):
    job = json.loads(message.data.decode("utf-8"))
    print("\n[WORKER] Received job:", job)
    process_job(job)
    message.ack()

def main():
    print("[WORKER] Listening for Pub/Sub messages...")
    subscriber.subscribe(subscription_path, callback=callback)

    # Keep alive
    import time
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
