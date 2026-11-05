"""Gráficos por livro e de comparação entre livros (matplotlib, a partir de DataFrames pandas)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .indicadores import CLASSES, NOMES_CLASSES  # noqa: E402

AZUL, VERMELHO, VERDE, CINZA = "#1f4e79", "#c0504d", "#4f8a3a", "#7f7f7f"
CORES_LINGUA = {"pt": AZUL, "fr": VERMELHO, "en": VERDE}


def _estilo():
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlelocation": "left", "figure.dpi": 120, "savefig.bbox": "tight"})


def _guardar(fig, destino: Path):
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino)
    plt.close(fig)


def por_livro(titulo: str, freq: pd.DataFrame, pos: pd.Series, frases: pd.Series, evol: pd.DataFrame,
              ents: pd.DataFrame, pasta: Path) -> list[str]:
    _estilo()
    ficheiros = []

    top = freq.head(25).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.barh(top.lema, top.ocorrencias, color=AZUL)
    ax.set_title(f"Palavras de conteúdo mais frequentes (lemas)\n{titulo}")
    ax.set_xlabel("ocorrências")
    _guardar(fig, pasta / "frequencias.png")
    ficheiros.append("frequencias.png")

    p = pos.reindex(CLASSES).fillna(0).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh([NOMES_CLASSES[c] for c in p.index], p.values, color=AZUL)
    ax.set_title(f"Classes gramaticais (% das palavras)\n{titulo}")
    _guardar(fig, pasta / "classes-gramaticais.png")
    ficheiros.append("classes-gramaticais.png")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    limite = int(frases.quantile(0.99))
    ax.hist(frases.clip(upper=limite), bins=range(1, limite + 2), color=AZUL)
    ax.axvline(frases.mean(), color=VERMELHO, lw=1.5, label=f"média: {frases.mean():.1f}".replace(".", ","))
    ax.axvline(frases.median(), color=CINZA, lw=1.5, ls="--", label=f"mediana: {frases.median():.0f}")
    ax.legend(frameon=False)
    ax.set_xlabel("palavras por frase (até ao percentil 99)")
    ax.set_ylabel("frases")
    ax.set_title(f"Comprimento das frases\n{titulo}")
    _guardar(fig, pasta / "comprimento-frases.png")
    ficheiros.append("comprimento-frases.png")

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharex=True, layout="constrained")
    for ax, (col, rot, cor) in zip(axes, [("mattr_500", "Variedade lexical (MATTR)", AZUL),
                                          ("frase_media_palavras", "Frase média (palavras)", VERMELHO),
                                          ("densidade_lexical_pct", "Densidade lexical (%)", VERDE)]):
        ax.plot(evol.parte, evol[col], marker="o", color=cor)
        ax.set_title(rot)
        ax.set_xticks(evol.parte)
        ax.set_xlabel("décimo do livro")
    fig.suptitle(f"Evolução ao longo do livro · {titulo}", x=0.01, ha="left", fontweight="bold")
    _guardar(fig, pasta / "evolucao.png")
    ficheiros.append("evolucao.png")

    tipos = [t for t in ("pessoa", "lugar") if t in set(ents.tipo)]
    if tipos:
        fig, axes = plt.subplots(1, len(tipos), figsize=(6 * len(tipos), 5.5), squeeze=False, layout="constrained")
        for ax, tipo in zip(axes[0], tipos):
            sub = ents[ents.tipo == tipo].head(15).iloc[::-1]
            ax.barh(sub.entidade, sub.ocorrencias, color=AZUL if tipo == "pessoa" else VERDE)
            ax.set_title({"pessoa": "Pessoas", "lugar": "Lugares"}[tipo])
        fig.suptitle(f"Entidades mais mencionadas (NER) · {titulo}", x=0.01, ha="left", fontweight="bold")
        _guardar(fig, pasta / "entidades.png")
        ficheiros.append("entidades.png")
    return ficheiros


def corpus(tabela: pd.DataFrame, pasta: Path) -> list[str]:
    """Comparação entre livros. `tabela` tem uma linha por livro."""
    _estilo()
    if tabela.empty:
        return []
    t = tabela.copy()
    t["rotulo"] = t.titulo.fillna(t.id).str.slice(0, 40)
    cores = [CORES_LINGUA.get(lg, CINZA) for lg in t.lingua]
    metricas = [("mattr_500", "Variedade lexical (MATTR)"), ("frase_media_palavras", "Frase média (palavras)"),
                ("legibilidade", "Legibilidade (Flesch adaptado)"), ("densidade_lexical_pct", "Densidade lexical (%)"),
                ("dialogo_pct", "Parágrafos de diálogo (%)"), ("palavras", "Palavras")]
    altura = max(3.5, 0.45 * len(t) + 1.5)
    fig, axes = plt.subplots(2, 3, figsize=(14, 2 * altura), sharey=True, layout="constrained")
    ordem = t.sort_values("palavras")
    for ax, (col, rot) in zip(axes.flat, metricas):
        ax.barh(ordem.rotulo, ordem[col], color=[CORES_LINGUA.get(lg, CINZA) for lg in ordem.lingua])
        ax.set_title(rot)
    from matplotlib.patches import Patch

    nomes = {"pt": "português", "fr": "francês", "en": "inglês"}
    fig.legend(handles=[Patch(color=c, label=nomes[lg]) for lg, c in CORES_LINGUA.items()],
               loc="upper right", ncol=3, frameon=False)
    fig.suptitle("Comparação entre livros", x=0.01, ha="left", fontweight="bold")
    _guardar(fig, pasta / "comparacao.png")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(t.frase_media_palavras, t.mattr_500, s=40 + t.palavras / t.palavras.max() * 600, c=cores, alpha=0.75)
    for _, r in t.iterrows():
        ax.annotate(r.rotulo, (r.frase_media_palavras, r.mattr_500), fontsize=8, xytext=(6, 4),
                    textcoords="offset points")
    ax.set_xlabel("frase média (palavras)")
    ax.set_ylabel("variedade lexical (MATTR)")
    ax.set_title("Complexidade sintática e variedade lexical (tamanho = número de palavras)")
    _guardar(fig, pasta / "dispersao.png")
    return ["comparacao.png", "dispersao.png"]
