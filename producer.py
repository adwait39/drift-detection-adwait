import os
import time
import json
import pandas as pd
import pika

# -----------------------------
# CONFIG
# -----------------------------
RABBITMQ_HOST = "localhost"
QUEUE_NAME = "ml_drift_stream"

BASELINE_PATH = os.path.join("data", "baseline_1000.csv")
DRIFT_DIR = os.path.join("data", "drift_sets")  # folder with drift_*.csv


# -----------------------------
# RABBITMQ CONNECTION
# -----------------------------
def get_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    # durable queue survives server restarts
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    return connection, channel


# -----------------------------
# HELPERS
# -----------------------------
def load_text_column(df: pd.DataFrame) -> pd.Series:
    """
    Try to pick the column that contains the text/query.
    For your files, the last column is the query text
    (the first one looks like an index).
    """
    text_col = df.columns[-1]
    return df[text_col].astype(str)


def send_dataframe(df: pd.DataFrame, source_type: str, drift_type: str | None, channel):
    """
    Send each row as one message into RabbitMQ.
    """
    text_series = load_text_column(df)

    for i, text in text_series.items():
        message = {
            "source": source_type,        # "baseline" or "drift"
            "drift_type": drift_type,     # e.g. "semantic", "lexical", ...
            "index": int(i),
            "text": text,
        }

        body = json.dumps(message).encode("utf-8")

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            ),
        )

        print(f"[PRODUCER] Sent: {message}")
        # Small sleep to simulate streaming; tweak as you like
        time.sleep(0.05)


def stream_baseline(channel):
    print("=== Streaming BASELINE data ===")
    df = pd.read_csv(BASELINE_PATH)
    send_dataframe(df, source_type="baseline", drift_type=None, channel=channel)


def stream_all_drift_sets(channel):
    print("=== Streaming DRIFT data ===")

    # Sort files so they go in order drift_1_..., drift_2_..., ...
    files = sorted(
        f for f in os.listdir(DRIFT_DIR)
        if f.lower().endswith(".csv")
    )

    for filename in files:
        path = os.path.join(DRIFT_DIR, filename)

        # Try to extract drift type from filename: drift_1_semantic.csv -> "semantic"
        drift_type = filename
        if filename.startswith("drift_"):
            parts = filename.split("_", 2)  # ["drift", "1", "semantic.csv"]
            if len(parts) == 3:
                drift_type = parts[2].split(".")[0]

        print(f"\n--- Streaming {filename} (drift_type={drift_type}) ---")
        df = pd.read_csv(path)
        send_dataframe(df, source_type="drift", drift_type=drift_type, channel=channel)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    connection, channel = get_channel()

    try:
        # 1) Send baseline queries
        stream_baseline(channel)

        # 2) Then send all drift sets (these are your test scenarios)
        stream_all_drift_sets(channel)

        print("\nAll data sent. Closing connection.")
    finally:
        connection.close()
