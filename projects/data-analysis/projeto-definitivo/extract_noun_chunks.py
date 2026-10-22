import spacy
import pandas as pd
from collections import Counter
import os
import glob

nlp = spacy.load("pt_core_news_lg")

def extract_noun_chunks(text):
    doc = nlp(text)
    return [chunk.text.lower() for chunk in doc.noun_chunks]

def process_file(file_path):
    df = pd.read_csv(file_path)
    all_text = " ".join(df["Pergunta"].fillna("") + " " + df["Resposta"].fillna(""))
    chunks = extract_noun_chunks(all_text)
    return Counter(chunks)

def main():
    dataset_paths = glob.glob("Datasets/*.csv")
    total_counts = Counter()

    for path in dataset_paths:
        total_counts += process_file(path)

    top_10 = total_counts.most_common(10)
    df = pd.DataFrame(top_10, columns=["Noun Chunk", "Frequência Absoluta"])
    df.to_csv("CSV/noun_chunks_frequencia_absoluta.csv", index=False)

    total = sum(total_counts.values())
    df["Frequência Relativa"] = df["Frequência Absoluta"] / total
    df.to_csv("CSV/noun_chunks_frequencia_relativa.csv", index=False)

if __name__ == "__main__":
    main()
