"""Gera as faixas de cabeçalho do README em Archivo Expanded.

O Markdown do GitHub não permite escolher tipos de letra, por isso os
títulos das secções são imagens com a identidade visual dos gráficos:
faixa amarela, número da secção num bloco preto e título em Archivo
Expanded ExtraBold.

Uso (a partir da raiz do projeto):
    python scripts/cabecalhos.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ / "fontes"
OUT = RAIZ / "graficos" / "cabecalhos"

AMARELO = "#F5D510"
PRETO = "#111111"

SECCOES = [
    ("01", "resumo", "Resumo"),
    ("02", "indicadores", "Indicadores-chave"),
    ("03", "conclusoes", "Principais conclusões"),
    ("04", "relatorios", "Relatórios"),
    ("05", "modelo-de-dados", "Modelo de dados"),
    ("06", "como-usar", "Como usar"),
    ("07", "fontes-e-limitacoes", "Fontes e limitações"),
    ("08", "identidade-visual", "Identidade visual"),
]


def fonte(nome):
    return font_manager.FontProperties(fname=str(FONTES / nome))


def faixa(numero, ficheiro, titulo):
    largura, altura = 16, 1.1           # polegadas; 1600 x 110 px a 100 dpi
    fig = plt.figure(figsize=(largura, altura), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), largura, altura, color=AMARELO))
    ax.add_patch(Rectangle((0, 0), 1.25, altura, color=PRETO))
    ax.text(0.625, altura / 2, numero, color=AMARELO, ha="center", va="center",
            fontproperties=fonte("ArchivoExpanded-ExtraBold.ttf"), fontsize=26)
    ax.text(1.65, altura / 2, titulo.upper(), color=PRETO, ha="left", va="center",
            fontproperties=fonte("ArchivoExpanded-ExtraBold.ttf"), fontsize=30)
    ax.text(largura - 0.35, altura / 2, "VITÓRIA SC · CONTAS EM SQL", color=PRETO,
            ha="right", va="center", alpha=0.55,
            fontproperties=fonte("Archivo-Bold.ttf"), fontsize=12)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{numero}_{ficheiro}.png", dpi=100)
    plt.close(fig)


def main():
    for numero, ficheiro, titulo in SECCOES:
        faixa(numero, ficheiro, titulo)
        print(f"OK  {numero}_{ficheiro}.png")


if __name__ == "__main__":
    main()
