import streamlit as st
import requests
import pandas as pd

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Drift Detection UI", layout="wide")
st.title("📊 Drift Detection – Pub/Sub + MinIO + Gmail")

st.markdown(
    "Upload **baseline** and **drift** CSVs, send a job via FastAPI → "
    "**Google Pub/Sub → Worker → Gmail → Results**."
)

# -------------------------------------------------
# 1️⃣ Upload baseline & drift → /check-drift
# -------------------------------------------------
st.subheader("1. Upload Baseline & Drift Datasets")

col1, col2 = st.columns(2)

with col1:
    baseline_file = st.file_uploader(
        "Baseline CSV", type=["csv"], key="baseline_uploader"
    )

with col2:
    drift_file = st.file_uploader(
        "Drift CSV", type=["csv"], key="drift_uploader"
    )

if st.button("🚀 Run Drift Check"):
    if not baseline_file or not drift_file:
        st.error("Please upload **both** baseline and drift CSV files.")
    else:
        files = {
            "baseline": (baseline_file.name, baseline_file.getvalue(), "text/csv"),
            "drift": (drift_file.name, drift_file.getvalue(), "text/csv"),
        }

        with st.spinner("Uploading files & queuing Pub/Sub job..."):
            try:
                r = requests.post(f"{FASTAPI_URL}/check-drift", files=files)
            except Exception as e:
                st.error(f"Error talking to FastAPI: {e}")
            else:
                if r.status_code == 200:
                    data = r.json()
                    st.success("Job queued successfully ✅")
                    st.json(data)
                    st.info("Your worker will process this job and Gmail alert will be sent.")
                else:
                    st.error(f"Backend error: {r.status_code} - {r.text}")

st.markdown("---")

# -------------------------------------------------
# 2️⃣ Fetch & display latest drift metrics
# -------------------------------------------------
st.subheader("2. View Latest Drift Result from Worker")

st.caption(
    "After the worker finishes and sends you a Gmail alert, click the button below "
    "to fetch the latest metrics saved by the worker."
)

if st.button("🔄 Fetch Latest Result"):
    with st.spinner("Calling /latest-result..."):
        try:
            r = requests.get(f"{FASTAPI_URL}/latest-result")
        except Exception as e:
            st.error(f"Error talking to FastAPI: {e}")
        else:
            if r.status_code != 200:
                st.error(f"Backend error: {r.status_code} - {r.text}")
            else:
                payload = r.json()
                if payload.get("status") != "ok":
                    st.warning("No result found yet. Wait for the worker to finish.")
                else:
                    metrics = payload.get("metrics", {})
                    st.success("Latest drift metrics:")
                    st.json(metrics)

                    # If metrics are numeric, show a nice table + bar chart.
                    if isinstance(metrics, dict):
                        # Build dataframe from numeric items only
                        numeric_items = {
                            k: v for k, v in metrics.items()
                            if isinstance(v, (int, float))
                        }
                        if numeric_items:
                            df = pd.DataFrame(
                                [numeric_items], index=["metrics"]
                            ).T
                            st.write("Metrics table:")
                            st.dataframe(df)

                            st.write("Bar chart:")
                            st.bar_chart(df)
