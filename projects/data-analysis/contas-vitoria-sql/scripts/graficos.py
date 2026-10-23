"""Gera os gráficos do projeto (PNG) a partir de vsc_contas.db.

Uso (a partir da raiz do projeto, depois de build_db.py):
    python scripts/graficos.py

Requer: matplotlib
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parent.parent
DB = RAIZ / "vsc_contas.db"
OUT = RAIZ / "graficos"

# Paleta categórica (ordem fixa) e tokens de texto/superfície
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": TEXT_2,
    "xtick.color": TEXT_2, "ytick.color": TEXT_2, "text.color": TEXT,
    "font.size": 10, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "legend.frameon": False, "axes.axisbelow": True,
})

milhoes = FuncFormatter(lambda v, _: f"{v / 1e6:.0f} M€".replace("-", "−"))


def q(con, sql):
    return con.execute(sql).fetchall()


def guardar(fig, nome, fonte="Fonte: VSC Contas (vitoriasempre.net), a partir dos R&C auditados"):
    fig.text(0.01, 0.01, fonte, fontsize=8, color=TEXT_2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / nome, dpi=150)
    plt.close(fig)
    print(f"  {nome}")


def resultado_por_entidade(con):
    rows = q(con, """SELECT epoca_id, rl_sad, rl_clube, rl_consolidado
                     FROM v_resultado_por_entidade WHERE epoca_id >= '2017/18'""")
    epocas = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    w = 0.26
    for i, (nome, cor) in enumerate(zip(["SAD", "Clube", "Consolidado"], SERIES)):
        xs = [x + (i - 1) * w for x in range(len(epocas))]
        ax.bar(xs, [r[i + 1] or 0 for r in rows], width=w - 0.03, color=cor, label=nome)
    ax.axhline(0, color=TEXT_2, linewidth=1)
    ax.set_xticks(range(len(epocas)), epocas)
    ax.yaxis.set_major_formatter(milhoes)
    ax.set_title("Resultado líquido por entidade")
    ax.legend(loc="lower left", ncols=3)
    guardar(fig, "01_resultado_por_entidade.png")


def receitas_vs_pessoal(con):
    rows = q(con, """SELECT epoca_id, vendas_servicos, gastos_pessoal
                     FROM v_kpis WHERE entidade_id = 'SAD' AND vendas_servicos IS NOT NULL
                     ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(epocas, [r[1] for r in rows], color=SERIES[0], linewidth=2, marker="o", markersize=5)
    ax.plot(epocas, [r[2] for r in rows], color=SERIES[1], linewidth=2, marker="o", markersize=5)
    i = epocas.index("2021/22")
    ax.annotate("Gastos com pessoal", (epocas[i], rows[i][2]), xytext=(0, 10),
                textcoords="offset points", ha="center", color=TEXT_2)
    ax.annotate("Receitas (vendas e serviços)", (epocas[i], rows[i][1]), xytext=(0, -18),
                textcoords="offset points", ha="center", color=TEXT_2)
    ax.yaxis.set_major_formatter(milhoes)
    ax.set_ylim(0, None)
    ax.tick_params(axis="x", rotation=45)
    ax.set_title("SAD: de 2020/21 a 2023/24, o pessoal custou mais do que as receitas")
    guardar(fig, "02_receitas_vs_pessoal_sad.png")


def dependencia_vendas(con):
    rows = q(con, """SELECT epoca_id, resultado_liquido, rl_sem_mais_valias
                     FROM v_kpis WHERE entidade_id = 'SAD' AND mais_valias_liquidas IS NOT NULL
                     ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    w = 0.38
    ax.bar([x - w / 2 for x in range(len(epocas))], [r[1] for r in rows], width=w - 0.03,
           color=SERIES[0], label="Resultado líquido")
    ax.bar([x + w / 2 for x in range(len(epocas))], [r[2] for r in rows], width=w - 0.03,
           color=SERIES[1], label="Resultado sem mais-valias de jogadores")
    ax.axhline(0, color=TEXT_2, linewidth=1)
    ax.set_xticks(range(len(epocas)), epocas)
    ax.yaxis.set_major_formatter(milhoes)
    ax.set_title("SAD: sem vender jogadores, todas as épocas dariam prejuízo")
    ax.legend(loc="lower left")
    guardar(fig, "03_dependencia_vendas_jogadores.png")


def composicao_receitas(con):
    grupos = ["Direitos TV", "Competições UEFA + Nacionais", "Sócios e Camarotes",
              "Patrocínios e Publicidade", "Bilhética"]
    rows = q(con, "SELECT epoca_id, categoria, valor FROM receitas_composicao ORDER BY epoca_id")
    epocas = sorted({r[0] for r in rows})
    dados = {g: [0] * len(epocas) for g in grupos + ["Outras"]}
    for e, cat, v in rows:
        dados[cat if cat in grupos else "Outras"][epocas.index(e)] += v
    totais = [sum(dados[g][i] for g in dados) for i in range(len(epocas))]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    base = [0.0] * len(epocas)
    for g, cor in zip(dados, SERIES):
        pct = [100 * dados[g][i] / totais[i] for i in range(len(epocas))]
        ax.bar(epocas, pct, bottom=base, color=cor, label=g.replace(" + Nacionais", ""),
               width=0.7, edgecolor=SURFACE, linewidth=1.5)
        base = [b + p for b, p in zip(base, pct)]
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_title("Composição das receitas operacionais")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncols=6, fontsize=8.5)
    guardar(fig, "04_composicao_receitas.png")


def balanco_sad(con):
    rows = q(con, """SELECT epoca_id, ativo_total, passivo_total, capital_proprio
                     FROM balanco WHERE entidade_id = 'SAD' ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(epocas, [r[1] for r in rows], color=SERIES[0], linewidth=2, marker="o", markersize=5)
    ax.plot(epocas, [r[2] for r in rows], color=SERIES[1], linewidth=2, marker="o", markersize=5)
    ax.fill_between(epocas, [r[1] for r in rows], [r[2] for r in rows],
                    where=[r[2] > r[1] for r in rows], color=SERIES[1], alpha=0.12,
                    interpolate=True)
    ax.annotate("Passivo", (epocas[-1], rows[-1][2]), xytext=(-6, 8),
                textcoords="offset points", ha="right", color=TEXT_2)
    ax.annotate("Ativo", (epocas[-1], rows[-1][1]), xytext=(-10, -20),
                textcoords="offset points", ha="right", color=TEXT_2)
    ax.annotate("Capital próprio negativo\n(passivo > ativo)", ("2022/23", 45e6),
                ha="center", color=TEXT_2, fontsize=9)
    ax.yaxis.set_major_formatter(milhoes)
    ax.set_ylim(0, None)
    ax.tick_params(axis="x", rotation=45)
    ax.set_title("SAD: ativo vs passivo a 30 de junho")
    guardar(fig, "05_balanco_sad.png")


def main():
    OUT.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    print("Gráficos gerados:")
    resultado_por_entidade(con)
    receitas_vs_pessoal(con)
    dependencia_vendas(con)
    composicao_receitas(con)
    balanco_sad(con)


if __name__ == "__main__":
    main()
