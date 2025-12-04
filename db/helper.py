from db import test_connection
from db import insert_metrics
test_connection()

from db import create_table_if_not_exists
create_table_if_not_exists()

dummy = {
    "dataset": "sample1",
    "semantic_mean": 0.8,
    "semantic_median": 0.75,
    "semantic_min": 0.6,
    "topic_shift_mean": 0.12,
    "topic_shift_max": 0.20,
    "topic_kl": 2.1,
    "lexical_overlap": 0.55,
    "length_psi": 0.02,
    "length_ks_p": 0.0002,
    "ood_rate": 0.10,
    "ood_min": 0.06,
    "ood_mean": 0.09
}

insert_metrics(dummy)
