import spacy
import pandas as pd
import os
from collections import Counter

def lemmatize_text(text, nlp):
    doc = nlp(text)
    return [token.lemma_.lower() for token in doc if token.is_alpha]

def main():
    nlp = spacy.load("pt_core_news_sm")  # modelo português spaCy
    datasets_folder = "Datasets"
    dataset_files = [
        "dataset_corpus_entrevista_mariana.csv",
        "dataset_corpus_entrevista_joana.csv",
        "dataset_corpus_entrevista_joao.csv"
    ]
    
    all_lemmas = []
    
    for filename in dataset_files:
        path = os.path.join(datasets_folder, filename)
        df = pd.read_csv(path)
        
        # Ajusta aqui o nome da coluna que contém o texto a analisar
        text_column = "Resposta"  
        
        for text in df[text_column].dropna():
            lemmas = lemmatize_text(text, nlp)
            all_lemmas.extend(lemmas)
    
    lemma_counts = Counter(all_lemmas)
    
    total_lemmas = sum(lemma_counts.values())
    
    # Criar DataFrame com frequências absoluta e relativa
    df_lemmas = pd.DataFrame(lemma_counts.items(), columns=["Lema", "Frequência Absoluta"])
    df_lemmas["Frequência Relativa"] = df_lemmas["Frequência Absoluta"] / total_lemmas
    
    # Ordenar por frequência absoluta descendente
    df_lemmas = df_lemmas.sort_values(by="Frequência Absoluta", ascending=False)
    
    # Guardar CSV para o generate_graphs.py
    df_lemmas.to_csv("CSV/lemmas_frequencia.csv", index=False)
    print("[INFO] CSV com lemas e frequências salvo em CSV/lemmas_frequencia.csv")

if __name__ == "__main__":
    main()
