# **ML Data Drift Detection System**

### *Real-Time Drift Monitoring Using FastAPI, RabbitMQ, MinIO, and Sentence Transformers*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/FastAPI-High%20Performance-green" />
  <img src="https://img.shields.io/badge/RabbitMQ-Message%20Broker-orange" />
  <img src="https://img.shields.io/badge/MinIO-Object%20Storage-yellow" />
  <img src="https://img.shields.io/badge/SentenceTransformers-Embeddings-purple" />
</p>

---

# **Project Overview**

Modern machine learning systems degrade over time because **real-world data changes** — a phenomenon known as **Data Drift**.
This project builds a fully functional, local and scalable **Drift Detection Pipeline** inspired by real MLOps production systems.

Users upload:

* A **baseline dataset** (historical training data)
* A **drift dataset** (new incoming data)

The system then:

1. Stores both datasets in **MinIO** (local object storage)
2. Queues a processing job in **RabbitMQ**
3. Worker service:

   * Downloads both datasets
   * Computes semantic embeddings
   * Calculates drift score
   * Determines if the model must be updated

---

# **Why This Project Matters for Big Companies**

Data drift severely impacts **model accuracy**, **business KPIs**, and **revenue**.

### Example: E-commerce

User behavior changes → recommendation models become outdated → fewer conversions.

### Example: Banks

Fraud patterns evolve → fraud models miss new attacks → financial losses.

### Example: Uber / Lyft

City mobility trends shift → demand prediction models degrade → pricing errors.

### Example: Amazon

Seasonal/market trends change → inventory forecasting fails → overstock/stockouts.

---

# **How This Project Solves Real Enterprise Problems**

| Problem                                          | How This Project Helps                                  |
| ------------------------------------------------ | ------------------------------------------------------- |
| **Models degrade silently**                      | Continuous monitoring detects drift early               |
| **No visibility into incoming data changes**     | Semantic drift scoring reveals hidden text shifts       |
| **Retraining ML models is expensive**            | Drift thresholding triggers retraining only when needed |
| **Distributed systems need scalable monitoring** | RabbitMQ enables multi-worker scale                     |
| **Cloud object storage is costly**               | MinIO provides free, local S3-like storage              |

This project is essentially a **mini-production MLOps drift monitoring engine**, fully local and free to run.

---

# **Technologies Used**

| Technology                | Purpose                                     |
| ------------------------- | ------------------------------------------- |
| **FastAPI**               | Upload datasets, trigger drift checks       |
| **MinIO (S3-compatible)** | Store baseline + drift CSV files            |
| **Google-Pub-sub**              | Queue drift processing jobs asynchronously  |
| **SentenceTransformers**  | Generate embeddings for semantic comparison |
| **Python Worker Service** | Downloads datasets, computes drift          |
| **Docker**                | Containorisation                                |
| **Uvicorn**               | ASGI server for FastAPI                     |

---

# **End-to-End Workflow**

### 1️⃣ **User Uploads Data**

User calls `/check-drift` and uploads:

* `baseline.csv`
* `drift.csv`

### 2️⃣ **FastAPI Stores Files in MinIO**

Files stored in bucket structure:

```
ml-drift-datasets/
    baselines/
    drifts/
```

### 3️⃣ **FastAPI Sends Job to RabbitMQ**

Example message:

```json
{
  "bucket": "ml-drift-datasets",
  "baseline_key": "baselines/baseline.csv",
  "drift_key": "drifts/drift.csv"
}
```

### 4️⃣ **Worker Picks Job**

The worker:

* Downloads files from MinIO
* Encodes text with SentenceTransformer
* Computes drift via cosine distance

### 5️⃣ **Drift Score Computed**

```
drift_score = 1 - cosine_similarity(baseline_mean, drift_mean)
```

### 6️⃣ **Decision**

| Drift Score | Meaning                |
| ----------- | ---------------------- |
| < 0.10      | No drift               |
| 0.10–0.20   | Moderate drift         |
| > 0.20      | High Drift Detected |

---

# **Sample Output**

```
[WORKER] Drift detection START
[WORKER] Baseline shape: (1000, 1)
[WORKER] Drift shape: (1000, 1)

[WORKER] DRIFT SCORE = 0.2431
[WORKER] 🚨 HIGH DRIFT DETECTED!
```

---

# **Running the Project**

## 1. Install dependencies

```
pip install -r requirements.txt
```

---

## 2. Start MinIO

```powershell
docker run -p 9000:9000 -p 9001:9001 ^
  -e MINIO_ROOT_USER=minioadmin ^
  -e MINIO_ROOT_PASSWORD=minioadmin ^
  -v "C:\minio-data:/data" ^
  quay.io/minio/minio server /data --console-address ":9001"
```

Open UI → [http://localhost:9001](http://localhost:9001)
Create bucket: `ml-drift-datasets`

---

## 3. Start RabbitMQ (Windows)

```
net start RabbitMQ
```

Management UI → [http://localhost:15672](http://localhost:15672)
Login: `guest / guest`

---

## 4. Start the Worker

```
python -m workers.worker
```

---

## 5. Start FastAPI

```
uvicorn api.main:app --reload
```

Open API docs → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
Upload baseline + drift.


# 📜 **License**

MIT License – free for everyone.
