# **Project Overview**

# **ML Data Drift Detection System**

### *Real-Time Drift Monitoring Using FastAPI, RabbitMQ / PubSub, MinIO, and Sentence Transformers*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/FastAPI-High%20Performance-green" />
  <img src="https://img.shields.io/badge/RabbitMQ-Message%20Broker-orange" />
  <img src="https://img.shields.io/badge/MinIO-Object%20Storage-yellow" />
  <img src="https://img.shields.io/badge/SentenceTransformers-Embeddings-purple" />
</p>

---

# **Project Overview**

Machine learning models degrade over time as **data distributions shift**, a problem known as **Data Drift**.
This project implements a **production-inspired MLOps Drift Detection Pipeline**, designed to monitor dataset changes and notify when drift becomes harmful.

The system performs:

* Semantic drift detection
* Lexical / topic drift detection
* OOD (out-of-distribution) detection
* Threshold-based drift classification
* Optional Gmail / Gemini alerting
* Optional PostgreSQL storage for dashboards

Users upload:

* A **baseline dataset** (reference / training dataset)
* A **drift dataset** (new incoming data)

The system then:

1. Stores both datasets in **MinIO (S3-compatible storage)**

2. Publishes a drift detection job through **RabbitMQ or Google Pub/Sub**

3. Drift Detection Service (Worker):

   * Downloads target & reference datasets
   * Computes embeddings using transformer models
   * Calculates semantic, lexical, topic, and OOD drift
   * Generates drift metric reports

4. (Optional)

   * Stores drift metrics in **PostgreSQL**
   * Generates LLM-based summaries through **Gemini**
   * Sends email notifications

---

# **Why This Project Matters for Big Companies**

Data Drift impacts all industries relying on machine learning:

### **E-commerce**

User behavior changes → outdated recommendation engines → lower conversions.

### **Banking**

Fraud patterns evolve → models fail to detect new threats → financial loss.

### **Ride-Sharing**

Mobility/demand shifts → inaccurate surge pricing → revenue drop.

### **Retail / Amazon**

Seasonal or market trends shift → forecasting models degrade → overstock or stockouts.

---

# **How This Project Solves Enterprise Problems**

| Enterprise Problem           | How This System Helps                                   |
| ---------------------------- | ------------------------------------------------------- |
| Models degrade silently      | Continuous drift monitoring                             |
| Hidden data shifts           | Semantic, lexical, and topic drift metrics              |
| Costly model retraining      | Retraining triggered only when drift exceeds thresholds |
| Need for scalable monitoring | Pub/Sub or RabbitMQ ensures multi-worker scale          |
| High cloud storage cost      | MinIO provides free, local S3-like storage              |
| Need for alerting & insights | Gemini + Gmail notifications                            |

This system replicates **real-world MLOps drift pipelines**, fully local and free to run.

---

# **System Architecture (Based on Final Architecture Diagram)**

> *Note: The diagram is not included in the README, but the explanation below reflects the exact architecture.*

### **1️⃣ Client Layer**

* Uploads baseline & drift files
* Can be UI, script, Postman, or automated service

---

### **2️⃣ FastAPI Server**

* `/upload` or `/check-drift` endpoint
* Validates files
* Stores datasets into MinIO
* Publishes drift detection job to Pub/Sub / RabbitMQ

---

### **3️⃣ MinIO – S3-Compatible Object Storage**

Used to store:

```
ml-drift-datasets/
    baselines/
    drifts/
```

---

### **4️⃣ Google Pub/Sub or RabbitMQ**

Handles asynchronous job distribution:

* Ensures reliability
* Allows multi-worker scaling
* Decouples API from computation

---

### **5️⃣ Drift Detection Service (Worker)**

Responsibilities:

* Download datasets from MinIO
* Embed text using SentenceTransformers
* Compute drift metrics (semantic, lexical, topic, OOD)
* Format drift results
* (Optional) Store metrics in PostgreSQL

---

### **6️⃣ Gemini Notifications (Optional Enhancement)**

* Generates natural-language summaries of drift
* Sends alerts via Gmail or Slack

---

### **7️⃣ Analytics & Dashboards (Optional)**

* Visualize real-time & historical drift patterns
* Use PostgreSQL as the backend for storing metrics

---

# **Technologies Used**

| Technology                    | Purpose                           |
| ----------------------------- | --------------------------------- |
| **FastAPI**                   | Dataset upload, API gateway       |
| **MinIO (S3-compatible)**     | Object storage for CSV files      |
| **RabbitMQ / Google Pub/Sub** | Asynchronous drift job processing |
| **SentenceTransformers**      | Embedding-based semantic drift    |
| **Python Worker Service**     | Core drift engine                 |
| **PostgreSQL (Optional)**     | Store drift metrics               |
| **Gemini AI (Optional)**      | LLM drift summaries               |
| **Docker**                    | Containerization                  |
| **Uvicorn**                   | FastAPI ASGI server               |

---

# **End-to-End Workflow**

### **1️⃣ User Uploads Data**

User uploads:

* `baseline.csv`
* `drift.csv`

Endpoint:

```
POST /check-drift
```

---

### **2️⃣ FastAPI Stores Files in MinIO**

```
ml-drift-datasets/
    baselines/
    drifts/
```

---

### **3️⃣ FastAPI Publishes Job**

Example message:

```json
{
  "bucket": "ml-drift-datasets",
  "baseline_key": "baselines/baseline.csv",
  "drift_key": "drifts/drift.csv"
}
```

---

### **4️⃣ Worker Processes the Job**

Worker:

* Downloads datasets
* Embeds text using SentenceTransformer
* Computes cosine similarity-based drift

---

### **5️⃣ Drift Score**

```
drift_score = 1 - cosine_similarity(baseline_mean, drift_mean)
```

---



# **Running the Project**

## **1. Install dependencies**

```
pip install -r requirements.txt
```

---

## **2. Start MinIO**

```
docker run -p 9000:9000 -p 9001:9001 ^
  -e MINIO_ROOT_USER=minioadmin ^
  -e MINIO_ROOT_PASSWORD=minioadmin ^
  -v "C:\minio-data:/data" ^
  quay.io/minio/minio server /data --console-address ":9001"
```

---

## **3. Start the Worker**

```
python -m workers.worker
```

---

## **4. Start FastAPI**

```
uvicorn api.main:app --reload
```

---

# 📜 **License**

MIT License – Open-source and free to use.

---
