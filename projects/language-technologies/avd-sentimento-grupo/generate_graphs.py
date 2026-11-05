import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_compact_bar(df, coluna_x, coluna_y, title, filename):
    plt.figure(figsize=(10, 6))
    sns.barplot(x=coluna_y, y=coluna_x, data=df)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"Graficos/{filename}")
    plt.close()

def main():
    noun_abs = pd.read_csv("CSV/noun_chunks_frequencia_absoluta.csv")
    plot_compact_bar(noun_abs, "Noun Chunk", "Frequência Absoluta", 
                     "Top 10 Noun Chunks (Frequência Absoluta)", 
                     "noun_chunks_frequencia_absoluta.png")

    noun_rel = pd.read_csv("CSV/noun_chunks_frequencia_relativa.csv")
    plot_compact_bar(noun_rel, "Noun Chunk", "Frequência Relativa", 
                     "Top 10 Noun Chunks (Frequência Relativa)", 
                     "noun_chunks_frequencia_relativa.png")

if __name__ == "__main__":
    main()
