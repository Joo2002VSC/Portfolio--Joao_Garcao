import spacy
import os
import pandas as pd
from collections import Counter

# Pasta onde estão os CSV originais
DATASETS_FOLDER = "Datasets"  
RESULTS_FOLDER = "Resultados"

os.makedirs(RESULTS_FOLDER, exist_ok=True)

nlp = spacy.load("pt_core_news_lg")

def get_bigrams(doc):
    tokens = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    return zip(tokens, tokens[1:])

def process_dataset(file_path):
    df = pd.read_csv(file_path)
    texts = df['Resposta'].dropna().tolist()

    bigram_counter = Counter()
    total_bigrams = 0

    for text in texts:
        doc = nlp(text)
        bigrams = list(get_bigrams(doc))
        bigram_counter.update(bigrams)
        total_bigrams += len(bigrams)

    return bigram_counter, total_bigrams

def save_top_bigrams(counter, total, dataset_name):
    top_10 = counter.most_common(10)
    data = []
    for bigram, count in top_10:
        data.append({
            'bigram': " ".join(bigram),
            'frequency_absolute': count,
            'frequency_relative': count / total if total > 0 else 0
        })

    df = pd.DataFrame(data)
    output_path = os.path.join(RESULTS_FOLDER, f"colocacoes_{dataset_name}.csv")
    df.to_csv(output_path, index=False)
    print(f"[INFO] Guardado: {output_path}")

def main():
    combined_counter = Counter()
    combined_total = 0

    for filename in os.listdir(DATASETS_FOLDER):
        if filename.endswith(".csv"):
            path = os.path.join(DATASETS_FOLDER, filename)
            dataset_name = os.path.splitext(filename)[0]

            print(f"[INFO] A processar: {filename}")
            counter, total = process_dataset(path)
            save_top_bigrams(counter, total, dataset_name)

            combined_counter.update(counter)
            combined_total += total

    # Salvar top bigrams do conjunto combinado
    save_top_bigrams(combined_counter, combined_total, "total")

if __name__ == "__main__":
    main()
