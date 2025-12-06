import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from storage_minio import upload_to_minio
from google.cloud import pubsub_v1

BUCKET_NAME = "ml-drift-datasets"
PROJECT_ID = "focus-mechanic-474016-s2"
TOPIC_NAME = "drift_jobs"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

app = FastAPI(title="Drift Detection Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def publish_job_to_pubsub(job_message: dict):
    job_bytes = json.dumps(job_message).encode("utf-8")
    future = publisher.publish(topic_path, job_bytes)
    print(f"[API] Published job to Pub/Sub: {job_message}")
    return future.result()

@app.post("/check-drift")
async def check_drift(
    baseline: UploadFile = File(...),
    drift: UploadFile = File(...),
):
    os.makedirs("tmp", exist_ok=True)

    # Save baseline locally
    baseline_local = os.path.join("tmp", f"baseline_{baseline.filename}")
    with open(baseline_local, "wb") as f:
        shutil.copyfileobj(baseline.file, f)

    # Save drift locally
    drift_local = os.path.join("tmp", f"drift_{drift.filename}")
    with open(drift_local, "wb") as f:
        shutil.copyfileobj(drift.file, f)

    # Upload to MinIO
    baseline_key = f"baselines/{baseline.filename}"
    drift_key = f"drifts/{drift.filename}"

    baseline_uri = upload_to_minio(BUCKET_NAME, baseline_local, baseline_key)
    drift_uri = upload_to_minio(BUCKET_NAME, drift_local, drift_key)

    # Create job
    job = {
        "bucket": BUCKET_NAME,
        "baseline_key": baseline_key,
        "drift_key": drift_key,
        "job_type": "drift_check"
    }

    publish_job_to_pubsub(job)

    return {
        "status": "queued",
        "baseline_uri": baseline_uri,
        "drift_uri": drift_uri,
        "job": job,
    }


@app.get("/latest-result")
async def latest_result():
    """
    Returns the most recent drift metrics saved by the worker.
    The worker writes data/latest_result.json.
    """
    latest_path = os.path.join("data", "latest_result.json")
    if not os.path.exists(latest_path):
        return {"status": "no_result_yet"}

    with open(latest_path, "r") as f:
        metrics = json.load(f)

    return {
        "status": "ok",
        "metrics": metrics,
    }
