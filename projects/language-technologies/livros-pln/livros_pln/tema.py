"""Identidade visual comum a todos os gráficos (matplotlib e Plotly).

Paleta discreta (azul-petróleo, azul-escuro, verde-acinzentado, cinzentos e um ocre de
destaque), fundo branco, grelhas leves, títulos informativos com subtítulo, números em
formato português (vírgula decimal, espaço nos milhares) e exportação em PNG e SVG.
As séries distinguem-se por cor e por forma do marcador, nunca só pela cor.
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import ticker  # noqa: E402

TINTA = "#1F2A33"
SUAVE = "#5B6670"
GRELHA = "#E3E7EB"
FUNDO = "#FFFFFF"
PETROLEO = "#1F5C6B"
PETROLEO_CLARO = "#9DBDC5"
AZUL_ESCURO = "#24405E"
VERDE_CINZA = "#6F9580"
CINZA = "#9AA3AB"
DESTAQUE = "#B9772E"
AMEIXA = "#7D6383"

SERIES = [PETROLEO, DESTAQUE, AZUL_ESCURO, VERDE_CINZA, AMEIXA, CINZA, "#3E8A9A", "#8C6D3F"]
MARCADORES = ["o", "s", "^", "D", "v", "P", "X", "h"]
LINGUAS = {"pt": (PETROLEO, "o", "português"), "fr": (AZUL_ESCURO, "s", "francês"), "en": (VERDE_CINZA, "^", "inglês")}
CLASSES_CORES = {"NOUN": PETROLEO, "VERB": DESTAQUE, "ADJ": VERDE_CINZA, "ADV": AMEIXA}
CLASSES_ABREV = {"NOUN": "s.", "VERB": "v.", "ADJ": "adj.", "ADV": "adv."}
FONTES = ["Inter", "Source Sans 3", "Source Sans Pro", "Helvetica Neue", "Arial", "DejaVu Sans"]
DPI = 200

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)


def aplicar():
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": FONTES, "font.size": 10,
        "text.color": TINTA, "axes.labelcolor": SUAVE, "axes.edgecolor": GRELHA, "axes.linewidth": 0.8,
        "axes.titlesize": 11, "axes.titleweight": "semibold", "axes.titlelocation": "left", "axes.titlepad": 8,
        "axes.titlecolor": TINTA, "axes.labelsize": 9.5, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True, "grid.color": GRELHA, "grid.linewidth": 0.7,
        "xtick.color": SUAVE, "ytick.color": SUAVE, "xtick.labelsize": 9, "ytick.labelsize": 9,
        "xtick.major.size": 0, "ytick.major.size": 0, "legend.frameon": False, "legend.fontsize": 9,
        "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO,
        "svg.fonttype": "none", "axes.formatter.use_locale": False,
    })


def num(v, casas: int = 1) -> str:
    """Número em formato português: 12 345,6."""
    if v is None or (isinstance(v, float) and v != v):
        return "—"
    texto = f"{v:,.{casas}f}".replace(",", " ").replace(".", ",")
    return "−" + texto[1:] if texto.startswith("-") else texto   # sinal de menos tipográfico


def formatador(casas: int = 0):
    return ticker.FuncFormatter(lambda x, _: num(x, casas))


def figura(nrows: int = 1, ncols: int = 1, largura: float = 9.0, altura: float = 5.0, **kw):
    aplicar()
    fig, axes = plt.subplots(nrows, ncols, figsize=(largura, altura), layout="constrained", **kw)
    return fig, axes


def cabecalho(fig, titulo: str, subtitulo: str = "", nota: str = ""):
    """Título e subtítulo alinhados à esquerda no topo; nota (fonte, método) no rodapé."""
    largura, altura = fig.get_size_inches()
    topo = (0.78 if subtitulo else 0.5) / altura        # polegadas reservadas para título e subtítulo
    base = (0.36 if nota else 0.06) / altura            # polegadas reservadas para a nota
    # rect = (esquerda, base, largura, altura) da zona onde o constrained layout coloca os eixos
    fig.get_layout_engine().set(rect=(0, base, 1, 1 - topo - base))
    fig.text(0.008, 1 - 0.1 / altura, titulo, ha="left", va="top", fontsize=13.5, fontweight="bold", color=TINTA)
    if subtitulo:
        fig.text(0.008, 1 - 0.38 / altura, subtitulo, ha="left", va="top", fontsize=10, color=SUAVE)
    if nota:
        fig.text(0.008, 0.08 / altura, nota, ha="left", va="bottom", fontsize=8, color=SUAVE)


def rotular_barras(ax, barras, valores, casas: int = 1, dentro_limite: float | None = None):
    """Escreve o valor no fim de cada barra horizontal."""
    maximo = max([v for v in valores if v == v] or [1])
    ax.set_xlim(0, maximo * 1.14)
    for b, v in zip(barras, valores):
        ax.text(b.get_width() + maximo * 0.01, b.get_y() + b.get_height() / 2, num(v, casas), va="center",
                ha="left", fontsize=8.5, color=SUAVE)


def guardar(fig, pasta: Path, nome: str, svg: bool = True) -> str:
    pasta.mkdir(parents=True, exist_ok=True)
    fig.savefig(pasta / f"{nome}.png", dpi=DPI)
    if svg:
        fig.savefig(pasta / f"{nome}.svg")
    plt.close(fig)
    return f"{nome}.png"


# --- Plotly -------------------------------------------------------------------------------------------------------

PLOTLY_FONTE = "Inter, Source Sans 3, Helvetica Neue, Arial, sans-serif"
