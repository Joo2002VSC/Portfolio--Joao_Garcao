import sys
import os
import matplotlib.pyplot as plt
from textblob import TextBlob
from collections import defaultdict

def analisar_falas(ficheiro_txt):
    with open(ficheiro_txt, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    falas = []
    for linha in linhas:
        if ':' in linha:
            try:
                orador, fala = linha.split(':', 1)
                orador = orador.strip()
                fala = fala.strip()
                if fala:
                    falas.append((orador, fala))
            except ValueError:
                continue

    sentimentos_por_orador = defaultdict(list)

    for orador, fala in falas:
        blob = TextBlob(fala)
        polaridade = blob.sentiment.polarity
        subjetividade = blob.sentiment.subjectivity
        sentimentos_por_orador[orador].append((polaridade, subjetividade))

    medias = {}
    for orador, sentimentos in sentimentos_por_orador.items():
        polaridades = [p for p, _ in sentimentos]
        subjetividades = [s for _, s in sentimentos]
        media_polaridade = sum(polaridades) / len(polaridades)
        media_subjetividade = sum(subjetividades) / len(subjetividades)
        medias[orador] = (media_polaridade, media_subjetividade)

    return medias

def exportar_grafico(medias, diretorio_saida):
    oradores = list(medias.keys())
    polaridades = [val[0] for val in medias.values()]
    subjetividades = [val[1] for val in medias.values()]

    x = range(len(oradores))

    plt.figure(figsize=(10, 6))
    plt.bar(x, polaridades, width=0.4, label='Polaridade Média', align='center', alpha=0.7)
    plt.bar([i + 0.4 for i in x], subjetividades, width=0.4, label='Subjetividade Média', align='center', alpha=0.7)

    plt.xticks([i + 0.2 for i in x], oradores, rotation=45)
    plt.xlabel("Oradores")
    plt.ylabel("Pontuação")
    plt.title("Média de Polaridade e Subjetividade por Orador")
    plt.legend()
    plt.tight_layout()

    caminho_grafico = os.path.join(diretorio_saida, "grafico_sentimentos.png")
    plt.savefig(caminho_grafico)
    print(f"Gráfico guardado em: {caminho_grafico}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python SentimentoFalas.py <ficheiro.txt>")
        sys.exit(1)

    caminho_txt = sys.argv[1]
    diretorio_saida = os.path.dirname(caminho_txt)

    medias = analisar_falas(caminho_txt)
    exportar_grafico(medias, diretorio_saida)
