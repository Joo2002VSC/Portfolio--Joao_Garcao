import pandas as pd
import spacy
from collections import Counter
import glob
import os


nlp = spacy.load("pt_core_news_lg")

def type_token_ratio(text):
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if token.is_alpha]
    types = set(tokens)
    return len(types) / len(tokens) if tokens else 0

def main():
    paths = glob.glob("Datasets/*.csv")
    results = []

    for path in paths:
        df = pd.read_csv(path)
        for speaker in ["Entrevistador", "Entrevistante"]:
            texts = df[speaker].dropna().tolist()
            full_text = " ".join(texts)
            ttr = type_token_ratio(full_text)
            results.append({"Ficheiro": os.path.basename(path), "Interlocutor": speaker, "TTR": ttr})

    result_df = pd.DataFrame(results)
    result_df.to_csv("CSV/ttr_por_interlocutor.csv", index=False)

if __name__ == "__main__":
    main()
