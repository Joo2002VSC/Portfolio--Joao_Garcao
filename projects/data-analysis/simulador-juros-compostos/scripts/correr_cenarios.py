"""
Corre os quatro cenários, gera os gráficos em graficos/ e a tabela em resultados.md.

Uso:  python scripts/correr_cenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from simulador import CENARIOS, simular  # noqa: E402

GRAFICOS = RAIZ / "graficos"
VERDE, AZUL, AMBAR, CINZA, TINTA = "#1f6f5c", "#2a5fa8", "#c47d14", "#5d6b66", "#18221f"
CORES_CENARIO = {"Base": VERDE, "Pessimista": "#b23a3a", "Otimista": AZUL, "Estagflação": AMBAR}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c9d2ce", "axes.labelcolor": TINTA, "xtick.color": CINZA, "ytick.color": CINZA,
    "axes.grid": True, "axes.formatter.useoffset": False, "grid.color": "#e3e9e6", "grid.linewidth": 0.8, "figure.dpi": 130,
})


def euros(v, _=None) -> str:
    if abs(v) >= 1e6:
        return f"{v / 1e6:.1f} M€".replace(".", ",")
    if abs(v) >= 1e3:
        return f"{v / 1e3:.0f} k€"
    return f"{v:.0f} €"


def fmt(v: float) -> str:
    return f"{v:,.0f} €".replace(",", " ")


def grafico_leque(r, nome: str, ficheiro: str) -> None:
    p10, p25, p50, p75, p90 = r.percentis()
    anos, inv = r.anos, r.investido.mean(axis=1)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.fill_between(anos, p10, p90, color=VERDE, alpha=0.14, lw=0, label="10–90%")
    ax.fill_between(anos, p25, p75, color=VERDE, alpha=0.28, lw=0, label="25–75%")
    ax.plot(anos, p50, color=VERDE, lw=2.4, label="Mediana")
    ax.plot(anos, inv, color=CINZA, lw=1.4, ls="--", label="Total investido")
    ax.plot(anos, r.deterministico, color=AMBAR, lw=1.4, ls=":", label="Juros compostos simples")
    ax.scatter([anos[-1]], [p50[-1]], color=VERDE, zorder=5, s=24)
    ax.annotate(euros(p50[-1]), (anos[-1], p50[-1]), xytext=(-8, 8), textcoords="offset points",
                ha="right", color=VERDE, fontweight="bold")
    ax.yaxis.set_major_formatter(FuncFormatter(euros))
    ax.set_xlim(anos[0], anos[-1])
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(0, None)
    ax.set_title(f"Cenário {nome}: 2000 simulações, valores nominais", loc="left", fontweight="bold", color=TINTA)
    ax.legend(frameon=False, ncol=3, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(GRAFICOS / ficheiro)
    plt.close(fig)


def grafico_cenarios(resultados: dict) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for nome, r in resultados.items():
        p10, _, p50, _, p90 = r.percentis(real=True)
        cor = CORES_CENARIO[nome]
        ax.fill_between(r.anos, p10, p90, color=cor, alpha=0.08, lw=0)
        ax.plot(r.anos, p50, color=cor, lw=2, label=f"{nome}: {euros(p50[-1])}")
    inv = next(iter(resultados.values())).investido.mean(axis=1)
    ax.plot(next(iter(resultados.values())).anos, inv, color=CINZA, ls="--", lw=1.3, label="Investido (nominal)")
    ax.yaxis.set_major_formatter(FuncFormatter(euros))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(0, None)
    ax.set_title("Mediana por cenário, em € de hoje (faixa: 10–90%)", loc="left", fontweight="bold", color=TINTA)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "2_cenarios_comparados.png")
    plt.close(fig)


def grafico_distribuicao(r) -> None:
    final = r.real[-1]
    objetivo = r.parametros.objetivo_real
    hi = np.percentile(final, 97)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    bins = np.linspace(0, hi, 40)
    n, b, patches = ax.hist(final[final <= hi], bins=bins, edgecolor="white", lw=0.5)
    for patch, esq in zip(patches, b[:-1]):
        patch.set_facecolor(VERDE if esq >= objetivo else "#c9d2ce")
    ax.axvline(objetivo, color="#b23a3a", ls="--", lw=1.4)
    prob = (final >= objetivo).mean()
    ax.text(objetivo, ax.get_ylim()[1] * 0.92, f"  objetivo {euros(objetivo)}: {prob:.0%} dos cenários acima",
            color="#b23a3a", va="top")
    ax.xaxis.set_major_formatter(FuncFormatter(euros))
    ax.set_yticks([])
    ax.grid(False)
    ax.set_title(f"Valor em {r.anos[-1]}, em € de hoje (cenário Base, sem os 3% mais altos)", loc="left", fontweight="bold", color=TINTA)
    fig.tight_layout()
    fig.savefig(GRAFICOS / "3_distribuicao_final.png")
    plt.close(fig)


def grafico_alocacao(base) -> None:
    pesos = np.arange(0, 1.01, 0.1)
    meds, p10s, p90s = [], [], []
    for w in pesos:
        f = simular(base.com(peso_cripto=float(w))).real[-1]
        meds.append(np.median(f)); p10s.append(np.percentile(f, 10)); p90s.append(np.percentile(f, 90))
    fig, ax = plt.subplots(figsize=(9, 3.8))
    x = pesos * 100
    ax.fill_between(x, p10s, p90s, color=AMBAR, alpha=0.15, lw=0, label="10–90%")
    ax.plot(x, meds, color=AMBAR, lw=2.2, marker="o", ms=4, label="Mediana")
    ax.yaxis.set_major_formatter(FuncFormatter(euros))
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(euros))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    ax.set_xlabel("% da carteira em cripto")
    ax.set_title("Mais cripto alarga o leque; acima de ~70% a mediana desce (€ de hoje, log)",
                 loc="left", fontweight="bold", color=TINTA)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "4_efeito_alocacao_cripto.png")
    plt.close(fig)


def pct(v) -> str:
    return "—" if v is None else f"{v * 100:.1f} %".replace(".", ",")


def tabela_md(resultados: dict) -> str:
    linhas = [
        "| Cenário | Investido | Mediana (nominal) | Mediana (€ de hoje) | P10–P90 (€ de hoje) | TIR real mediana | P(objetivo) | P(perda real) | Queda máx. mediana |",
        "|---|--:|--:|--:|--:|--:|--:|--:|--:|",
    ]
    for nome, r in resultados.items():
        s = r.resumo_final()
        linhas.append(
            f"| {nome} | {fmt(s['investido_medio'])} | {fmt(s['mediana_nominal'])} | **{fmt(s['mediana_real'])}** "
            f"| {fmt(s['p10_real'])} – {fmt(s['p90_real'])} | {pct(s['tir_real'][50])} | {pct(s['prob_objetivo'])} "
            f"| {pct(s['prob_perda_real'])} | {pct(s['drawdown_mediano'])} |"
        )
    return "\n".join(linhas)


def main() -> None:
    GRAFICOS.mkdir(exist_ok=True)
    resultados = {nome: simular(p) for nome, p in CENARIOS.items()}
    base = resultados["Base"]

    grafico_leque(base, "Base", "1_leque_cenario_base.png")
    grafico_cenarios(resultados)
    grafico_distribuicao(base)
    grafico_alocacao(CENARIOS["Base"])

    p = base.parametros
    texto = f"""# Resultados

Gerado por `scripts/correr_cenarios.py`. Plano comum a todos os cenários: {fmt(p.capital_inicial)} iniciais,
{fmt(p.aporte)} por mês (+{p.crescimento_aporte:.0%} ao ano), {1 - p.peso_cripto:.0%} ações / {p.peso_cripto:.0%} cripto,
rebalanceamento anual, de {base.anos[0]} a {base.anos[-1]}. Objetivo: {fmt(p.objetivo_real)} em € de hoje.

{tabela_md(resultados)}

Todos os cenários usam o mesmo plano e a mesma semente aleatória (números aleatórios comuns),
por isso as diferenças entre linhas vêm dos pressupostos de mercado e não do acaso da simulação.

- **Mediana**: metade dos cenários termina acima deste valor. *Nominal* = euros do ano final; *€ de hoje* = poder de compra atual.
- **P10–P90**: 80 % dos cenários terminam dentro deste intervalo.
- **TIR real mediana**: rentabilidade anual ponderada pelo dinheiro, já descontada a inflação.
- **P(objetivo)**: probabilidade de chegar ao objetivo em poder de compra de hoje.
- **P(perda real)**: probabilidade de o valor final valer menos do que o dinheiro investido, ambos em € de hoje.
- **Queda máx. mediana**: maior queda, do pico ao mínimo, da unidade de participação da carteira (*drawdown*).
"""
    (RAIZ / "resultados.md").write_text(texto, encoding="utf-8")
    print(tabela_md(resultados))


if __name__ == "__main__":
    main()
