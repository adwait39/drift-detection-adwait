import json
import pandas as pd
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote
from sqlalchemy import text
from dotenv import load_dotenv


load_dotenv()
# ============================================================
# POSTGRES CONNECTION
# ============================================================
USER = os.getenv("USER") 
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DB = os.getenv("DB")

enc_pw = quote(PASSWORD)

engine = create_engine(
    f"postgresql+psycopg2://{USER}:{enc_pw}@{HOST}:{PORT}/{DB}?sslmode=require"
)


def log(msg):
    print(f"\033[92m{msg}\033[0m")  

def log_error(msg):
    print(f"\033[91m{msg}\033[0m")  



def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            log(f"[DB] Connected successfully → {result.scalar()}")
    except Exception as e:
        log_error(f"[DB] Connection FAILED → {e}")


def create_table_if_not_exists(table="drift_metrics"):
    query = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        id SERIAL PRIMARY KEY,
        dataset TEXT,
        semantic_mean FLOAT,
        semantic_median FLOAT,
        semantic_min FLOAT,
        topic_shift_mean FLOAT,
        topic_shift_max FLOAT,
        topic_kl FLOAT,
        lexical_overlap FLOAT,
        length_psi FLOAT,
        length_ks_p FLOAT,
        ood_rate FLOAT,
        ood_min FLOAT,
        ood_mean FLOAT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(query))
            log("[DB] drift_metrics table verified/created.")
    except Exception as e:
        log_error(f"[DB] Table creation FAILED → {e}")




def insert_metrics(metrics: dict, table="drift_metrics"):
    try:
        clean = {}
        for k, v in metrics.items():
            clean[k] = json.dumps(v) if isinstance(v, (list, dict)) else v

        columns = ", ".join(clean.keys())
        values = ", ".join([f":{k}" for k in clean.keys()])

        query = text(f"""
            INSERT INTO {table} ({columns})
            VALUES ({values})
        """)

        with engine.begin() as conn:
            conn.execute(query, clean)

        print(f"[DB] Inserted metrics for dataset → {metrics.get('dataset')}")

    except Exception as e:
        print(f"[DB] INSERT FAILED → {e}")


def fetch_last_row(table="drift_metrics"):
    try:
        with engine.connect() as conn:
            df = pd.read_sql(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 1;", conn)
            log("[DB] Last row:")
            print(df)
    except Exception as e:
        log_error(f"[DB] FETCH FAILED → {e}")

if __name__ == "__main__":
    test_connection()
    create_table_if_not_exists()
    fetch_last_row()
