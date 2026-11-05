import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import DATASET_PATH

df = pd.read_csv(DATASET_PATH)

vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(df["text"])

def retrieve_top_k(question, k):
    q_vec = vectorizer.transform([question])
    sims = cosine_similarity(q_vec, X)[0]

    top_idx = sims.argsort()[::-1][:k]

    hits = []
    for i in top_idx:
        hits.append({
            "idx": int(i),
            "score": float(sims[i]),
            "section": df.iloc[i]["section"],
            "text": df.iloc[i]["text"]
        })

    return hits