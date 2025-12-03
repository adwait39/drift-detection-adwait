import numpy as np
from scipy.stats import entropy, ks_2samp
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(texts):
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def semantic_drift(base, new):
    base_emb = embed(base)
    new_emb  = embed(new)
    sims = 1 - cdist(new_emb, base_emb, metric="cosine")
    nn = sims.max(axis=1)

    return {
        "semantic_mean": float(nn.mean()),
        "semantic_median": float(np.median(nn)),
        "semantic_min": float(nn.min())
    }


def topic_drift(base, new, k=6):
    base_emb = embed(base)
    new_emb  = embed(new)

    kmb = KMeans(n_clusters=k).fit(base_emb)
    kmn = KMeans(n_clusters=k).fit(new_emb)

    sim = 1 - cdist(kmn.cluster_centers_, kmb.cluster_centers_, metric="cosine")
    shift = 1 - sim.max(axis=1)

    base_dist = np.bincount(kmb.labels_, minlength=k) / len(kmb.labels_)
    new_dist  = np.bincount(kmn.labels_, minlength=k) / len(kmn.labels_)

    kl = float(entropy(new_dist + 1e-9, base_dist + 1e-9))

    return {
        "topic_shift_mean": float(shift.mean()),
        "topic_shift_max": float(shift.max()),
        "topic_kl": kl
    }


def lexical_drift(base, new, top_n=50):
    vec = TfidfVectorizer(stop_words="english")
    vec.fit(base + new)

    b = vec.transform(base).mean(axis=0).A1
    n = vec.transform(new).mean(axis=0).A1
    terms = np.array(vec.get_feature_names_out())

    base_top = set(terms[np.argsort(b)[-top_n:]])
    new_top  = set(terms[np.argsort(n)[-top_n:]])

    overlap = len(base_top & new_top) / top_n

    return {"lexical_overlap": float(overlap)}


def psi(expected, actual, bins=10):
    expected = np.array(expected)
    actual   = np.array(actual)

    edges = np.quantile(expected, np.linspace(0,1,bins+1))
    exp_hist,_ = np.histogram(expected, bins=edges)
    act_hist,_ = np.histogram(actual, bins=edges)

    exp_pct = exp_hist / max(exp_hist.sum(),1)
    act_pct = act_hist / max(act_hist.sum(),1)

    return float(np.sum((act_pct - exp_pct) * np.log((act_pct + 1e-6)/(exp_pct + 1e-6))))

def statistical_drift(base, new):
    base_len = np.array([len(t.split()) for t in base])
    new_len  = np.array([len(t.split()) for t in new])

    return {
        "length_psi": psi(base_len, new_len),
        "length_ks_p": float(ks_2samp(base_len, new_len).pvalue)
    }


def ood_drift(base, new, threshold=0.55):
    base_emb = embed(base)
    new_emb  = embed(new)

    sims = 1 - cdist(new_emb, base_emb, metric="cosine")
    nn = sims.max(axis=1)

    ood = (nn < threshold).mean()

    return {
        "ood_rate": float(ood),
        "ood_min": float(nn.min()),
        "ood_mean": float(nn.mean())
    }
------ drift_detection.py