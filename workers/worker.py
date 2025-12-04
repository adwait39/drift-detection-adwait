import json
import pandas as pd
import os

# --- MINIO ---
from storage_minio import download_from_minio

# --- DRIFT COMPUTATION ---
from workers.compute import compute_all

# --- DATABASE ---
import db

# --- GMAIL NOTIFIER ---
from notifier import send_email_alert

# --- GOOGLE PUBSUB ---
from google.cloud import pubsub_v1

PROJECT_ID = "focus-mechanic-474016-s2"
SUBSCRIPTION_NAME = "drift_jobs_sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

print(f"[WORKER] Using subscription: {subscription_path}")
print("[WORKER] Worker ready.")

# Email address to receive drift alerts
ALERT_EMAIL = "yourgmail@gmail.com"   # <-- CHANGE THIS


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
    # Compute drift metrics
    # ----------------------------------------------------
    dataset_name = drift_key.split("/")[-1]
    metrics = compute_all(baseline_texts, drift_texts, dataset_name)

    print("\n[WORKER] DRIFT METRICS:")
    print(metrics)

    # ----------------------------------------------------
    # NEW: Save latest result for UI (Streamlit)
    # ----------------------------------------------------
    try:
        os.makedirs("data", exist_ok=True)
        latest_path = os.path.join("data", "latest_result.json")

        with open(latest_path, "w") as f:
            json.dump(metrics, f, indent=2)

        print(f"[WORKER] Saved latest result → {latest_path}")
    except Exception as e:
        print(f"[WORKER] Failed to save latest result: {e}")

    # ----------------------------------------------------
    # Save to PostgreSQL
    # ----------------------------------------------------
    db.create_table_if_not_exists()
    db.insert_metrics(metrics)
    print("[WORKER] Metrics saved to database.")

    # ----------------------------------------------------
    # Gmail Alerts (Conditions)
    # ----------------------------------------------------
    try:
        ood_rate = float(metrics.get("ood_rate", 0.0))
        topic_kl = float(metrics.get("topic_kl", 0.0))
        semantic_mean = float(metrics.get("semantic_mean", 0.0))

        high_drift = (
            ood_rate > 0.5
            or topic_kl > 1.0
            or semantic_mean < 0.30
        )

        if high_drift:
            print("[WORKER] High drift detected → sending Gmail alert...")

            subject = f"[DRIFT ALERT] High Drift in {dataset_name}"
            body = (
                f"A drift was detected in dataset: {dataset_name}\n\n"
                f"Drift Metrics:\n"
                f"  • OOD Rate: {ood_rate}\n"
                f"  • Topic KL Divergence: {topic_kl}\n"
                f"  • Semantic Mean Similarity: {semantic_mean}\n\n"
                f"Recommended Action: Review drift immediately.\n"
            )

            send_email_alert(subject, body, ALERT_EMAIL)

        else:
            print("[WORKER] Drift within normal range → no email alert.")

    except Exception as e:
        print(f"[WORKER] Gmail notifier failed → {e}")


def callback(message):
    print("\n[WORKER] Received message")
    job = json.loads(message.data.decode("utf-8"))
    process_job(job)
    message.ack()
    print("[WORKER] Message processed & acknowledged.")


def main():
    print("[WORKER] Listening for messages...")
    subscriber.subscribe(subscription_path, callback=callback)

    while True:
        import time
        time.sleep(60)


if __name__ == "__main__":
    main()
