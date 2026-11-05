import pandas as pd
from textblob import TextBlob
import glob
import os


def sentiment_score(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def main():
    paths = glob.glob("Datasets/*.csv")
    results = []

    for path in paths:
        df = pd.read_csv(path)
        for role in ["Entrevistador", "Entrevistante"]:
            texts = df[role].dropna().tolist()
            full_text = " ".join(texts)
            score = sentiment_score(full_text)
            results.append({"Ficheiro": os.path.basename(path), "Interlocutor": role, "Sentimento": score})

    pd.DataFrame(results).to_csv("CSV/sentimentos.csv", index=False)

if __name__ == "__main__":
    main()
