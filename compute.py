import pandas as pd
from drift_detection import *
from Db import db


def load_texts(path):
    df = pd.read_csv(path, header=None)
    col = df.columns[0]
    return df[col].astype(str).tolist()


def compute_all(baseline, drift, name):
    r = {"dataset": name}
    r.update(semantic_drift(baseline, drift))
    r.update(topic_drift(baseline, drift))
    r.update(lexical_drift(baseline, drift))
    r.update(statistical_drift(baseline, drift))
    r.update(ood_drift(baseline, drift))
    return r


if __name__ == "__main__":
    baseline = load_texts("data/drift_sets/baseline_1000.csv")
    drift    = load_texts("data/drift_sets/drift_1_semantic.csv")

    metrics = compute_all(baseline, drift, "drift_sample")

    print(metrics)

    #db.insert_metrics(metrics)
