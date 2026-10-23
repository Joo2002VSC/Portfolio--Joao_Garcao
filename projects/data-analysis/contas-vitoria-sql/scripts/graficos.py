"""Gera os gráficos do projeto (PNG) a partir de vsc_contas.db.

Uso (a partir da raiz do projeto, depois de build_db.py):
    python scripts/graficos.py

Requer: matplotlib

Identidade visual inspirada nos documentos financeiros do Vitória SC:
faixa amarela com título a negro, cinzentos neutros e valores negativos
entre parênteses, como nas demonstrações financeiras.
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parent.parent
DB = RAIZ / "vsc_contas.db"
OUT = RAIZ / "graficos"

# ---------------------------------------------------------------------
# Paleta
# ---------------------------------------------------------------------
AMARELO = "#F5D510"        # amarelo dos documentos
AMARELO_CLARO = "#FAEB8A"
PRETO = "#111111"
CINZA_ESCURO = "#6F6D6E"   # cinzento das linhas de total
CINZA = "#A9A7A8"
CINZA_CLARO = "#EBEBEB"    # cinzento das linhas de subtotal
BRANCO = "#FFFFFF"
TEXTO_2 = "#4A4949"

FONTE = "Fonte: VSC Contas (vitoriasempre.net), a partir dos Relatórios e Contas auditados · Análise: João Garção"

from matplotlib import font_manager

# Tipos de letra incluídos no projeto (pasta fontes/, licença OFL):
# Archivo Expanded nos títulos e números de destaque, Archivo no restante texto.
FONTES = RAIZ / "fontes"
for _f in FONTES.glob("*.ttf"):
    font_manager.fontManager.addfont(str(_f))
_disponiveis = {f.name for f in font_manager.fontManager.ttflist}
FAMILIA = "Archivo" if "Archivo" in _disponiveis else "DejaVu Sans"
FAMILIA_TITULO = "Archivo Expanded" if "Archivo Expanded" in _disponiveis else FAMILIA
TITULO = {"family": FAMILIA_TITULO, "fontweight": "heavy"}

plt.rcParams.update({
    "font.family": FAMILIA,
    "font.size": 10.5,
    "figure.facecolor": BRANCO, "axes.facecolor": BRANCO,
    "axes.edgecolor": CINZA_CLARO, "axes.labelcolor": TEXTO_2,
    "xtick.color": TEXTO_2, "ytick.color": TEXTO_2, "text.color": PRETO,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": CINZA_CLARO, "grid.linewidth": 1,
    "axes.axisbelow": True, "legend.frameon": False,
    "xtick.major.size": 0, "ytick.major.size": 0,
})


def euros_m(v, casas=0):
    """Formato financeiro: 7 M€ e negativos entre parênteses, (15 M€)."""
    txt = f"{abs(v) / 1e6:.{casas}f}".replace(".", ",") + " M€"
    return f"({txt})" if v < 0 else txt


eixo_m = FuncFormatter(lambda v, _: euros_m(v) if v else "0")


def q(con, sql):
    return con.execute(sql).fetchall()


def figura(titulo, subtitulo, altura=5.6, base=0.14):
    """Figura com faixa amarela de título, como nos documentos do clube."""
    fig = plt.figure(figsize=(11, altura))
    topo = 1 - 0.62 / altura
    fig.patches.append(Rectangle((0, topo), 1, 1 - topo, transform=fig.transFigure,
                                 color=AMARELO, zorder=0))
    fig.text(0.035, topo + (1 - topo) / 2, titulo.upper(), fontsize=14.5, va="center",
             color=PRETO, **TITULO)
    fig.text(0.035, topo - 0.32 / altura, subtitulo, fontsize=10.5, color=TEXTO_2, va="center")
    ax = fig.add_axes([0.085, base, 0.885, topo - 0.62 / altura - base])
    return fig, ax


def guardar(fig, nome):
    fig.patches.append(Rectangle((0, 0), 1, 0.006, transform=fig.transFigure,
                                 color=AMARELO, zorder=0))
    fig.text(0.035, 0.03, FONTE, fontsize=8, color=CINZA_ESCURO)
    fig.savefig(OUT / nome, dpi=170)
    plt.close(fig)
    print(f"  {nome}")


def barras_agrupadas(ax, epocas, series, largura=0.8):
    n = len(series)
    w = largura / n
    for i, (nome, valores, cor) in enumerate(series):
        xs = [x + (i - (n - 1) / 2) * w for x in range(len(epocas))]
        ax.bar(xs, [v or 0 for v in valores], width=w * 0.88, color=cor, label=nome,
               edgecolor=PRETO if cor in (AMARELO, AMARELO_CLARO) else cor, linewidth=0.6)
    ax.axhline(0, color=PRETO, linewidth=1.1)
    ax.set_xticks(range(len(epocas)), epocas)
    ax.yaxis.set_major_formatter(eixo_m)


# ---------------------------------------------------------------------
# Capa / resumo
# ---------------------------------------------------------------------
def capa(con):
    rl_2425 = q(con, """SELECT resultado_liquido FROM v_dr
                        WHERE entidade_id='SAD' AND epoca_id='2024/25'""")[0][0]
    rl_2526, cp_2526 = q(con, """SELECT k.resultado_liquido, k.capital_proprio FROM v_kpis k
                                 WHERE k.entidade_id='SAD' AND k.epoca_id='2025/26'""")[0]
    sem_mv = q(con, """SELECT rl_sem_mais_valias FROM v_kpis
                       WHERE entidade_id='SAD' AND epoca_id='2024/25'""")[0][0]

    fig = plt.figure(figsize=(11, 4.4))
    fig.patches.append(Rectangle((0, 0.52), 1, 0.48, transform=fig.transFigure, color=AMARELO))
    fig.text(0.04, 0.83, "AS CONTAS DO VITÓRIA SC", fontsize=27, color=PRETO, **TITULO)
    fig.text(0.04, 0.70, "Análise financeira em SQL  ·  SAD, Clube e Grupo consolidado  ·  2012/13 – 2025/26",
             fontsize=12, color=PRETO)
    fig.text(0.04, 0.585, "SQLITE   ·   PYTHON   ·   MATPLOTLIB", fontsize=9.5, fontweight="bold",
             color=PRETO, alpha=0.75)

    kpis = [
        ("RESULTADO SAD 2024/25", euros_m(rl_2425, 1), "recorde, com Europa e vendas"),
        ("SEM VENDAS DE JOGADORES", euros_m(sem_mv, 1), "o mesmo ano, sem mais-valias"),
        ("RESULTADO SAD 2025/26", euros_m(rl_2526, 1), "sem Europa"),
        ("CAPITAL PRÓPRIO SAD", euros_m(cp_2526, 1), "a 30/06/2026"),
    ]
    larg = 0.92 / len(kpis)
    for i, (rot, val, nota) in enumerate(kpis):
        x = 0.04 + i * larg
        fig.patches.append(Rectangle((x, 0.08), larg - 0.015, 0.36, transform=fig.transFigure,
                                     color=CINZA_CLARO))
        fig.text(x + 0.015, 0.37, rot, fontsize=8.5, fontweight="bold", color=TEXTO_2)
        fig.text(x + 0.015, 0.22, val, fontsize=21, color=PRETO, **TITULO)
        fig.text(x + 0.015, 0.125, nota, fontsize=8.5, color=TEXTO_2)
    fig.savefig(OUT / "00_capa.png", dpi=170)
    plt.close(fig)
    print("  00_capa.png")


# ---------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------
def resultado_por_entidade(con):
    rows = q(con, """SELECT epoca_id, rl_sad, rl_clube, rl_consolidado
                     FROM v_resultado_por_entidade WHERE epoca_id >= '2017/18'""")
    epocas = [r[0] for r in rows]
    fig, ax = figura("Resultado líquido por entidade",
                     "SAD, Clube e Grupo consolidado, por época (exercício a 30 de junho) · 2025/26: só SAD, comunicado de contas")
    barras_agrupadas(ax, epocas, [
        ("SAD", [r[1] for r in rows], PRETO),
        ("Grupo consolidado", [r[3] for r in rows], CINZA),
        ("Clube", [r[2] for r in rows], AMARELO),
    ])
    for x, r in enumerate(rows):
        if r[1] is not None and abs(r[1]) > 5e6:
            # valor escrito na vertical, dentro da barra da SAD
            ax.text(x - 0.267, r[1] / 2, euros_m(r[1], 1), rotation=90, ha="center", va="center",
                    fontsize=9, fontweight="bold", color=AMARELO if r[1] < 0 else BRANCO)
    ax.legend(loc="lower left", ncols=3)
    guardar(fig, "01_resultado_por_entidade.png")


def receitas_vs_pessoal(con):
    rows = q(con, """SELECT epoca_id, vendas_servicos, gastos_pessoal
                     FROM v_kpis WHERE entidade_id = 'SAD' AND vendas_servicos IS NOT NULL
                     ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    rec, pes = [r[1] for r in rows], [r[2] for r in rows]
    fig, ax = figura("Receitas vs. gastos com pessoal",
                     "SAD · Entre 2020/21 e 2023/24, os gastos com pessoal superaram as receitas")
    x = range(len(epocas))
    ax.fill_between(x, rec, pes, where=[p > r for p, r in zip(pes, rec)], interpolate=True,
                    color=AMARELO, alpha=0.55, linewidth=0, label="Pessoal acima das receitas")
    ax.plot(x, rec, color=PRETO, linewidth=2.4, marker="o", markersize=6, label="Receitas (vendas e serviços)")
    ax.plot(x, pes, color=CINZA_ESCURO, linewidth=2.4, marker="o", markersize=6,
            markerfacecolor=BRANCO, markeredgewidth=2, label="Gastos com pessoal")
    i = epocas.index("2020/21")
    ax.annotate(f"{100 * pes[i] / rec[i]:.0f}% das receitas", (i, pes[i]), xytext=(0, 10),
                textcoords="offset points", ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(list(x), epocas, rotation=0, fontsize=9)
    ax.yaxis.set_major_formatter(eixo_m)
    ax.set_ylim(0, 25e6)
    ax.legend(loc="upper left")
    guardar(fig, "02_receitas_vs_pessoal_sad.png")


def dependencia_vendas(con):
    rows = q(con, """SELECT epoca_id, resultado_liquido, rl_sem_mais_valias
                     FROM v_kpis WHERE entidade_id = 'SAD' AND mais_valias_liquidas IS NOT NULL
                     ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    fig, ax = figura("Dependência das vendas de jogadores",
                     "SAD · Sem as mais-valias das transferências, todas as épocas teriam dado prejuízo")
    barras_agrupadas(ax, epocas, [
        ("Resultado líquido", [r[1] for r in rows], PRETO),
        ("Resultado sem mais-valias de jogadores", [r[2] for r in rows], AMARELO),
    ], largura=0.72)
    for x, r in enumerate(rows):
        ax.annotate(euros_m(r[2], 1), (x + 0.18, r[2]), xytext=(0, -13), textcoords="offset points",
                    ha="center", fontsize=8, color=TEXTO_2)
    ax.set_ylim(-29e6, 11e6)
    ax.legend(loc="upper left", ncols=2)
    guardar(fig, "03_dependencia_vendas_jogadores.png")


def composicao_receitas(con):
    grupos = [("Direitos TV", PRETO, BRANCO),
              ("Competições UEFA + Nacionais", AMARELO, PRETO),
              ("Sócios e Camarotes", CINZA_ESCURO, BRANCO),
              ("Patrocínios e Publicidade", CINZA, PRETO),
              ("Bilhética", AMARELO_CLARO, PRETO),
              ("Outras", CINZA_CLARO, PRETO)]
    nomes = [g[0] for g in grupos]
    rows = q(con, "SELECT epoca_id, categoria, valor FROM receitas_composicao ORDER BY epoca_id")
    epocas = sorted({r[0] for r in rows})
    dados = {g: [0] * len(epocas) for g in nomes}
    for e, cat, v in rows:
        dados[cat if cat in nomes else "Outras"][epocas.index(e)] += v
    totais = [sum(dados[g][i] for g in nomes) for i in range(len(epocas))]

    fig, ax = figura("Composição das receitas operacionais",
                     "Peso de cada fonte de receita (%) · Os direitos TV dominam, exceto em anos europeus",
                     altura=6.2, base=0.2)
    base = [0.0] * len(epocas)
    for nome, cor, cor_txt in grupos:
        pct = [100 * dados[nome][i] / totais[i] for i in range(len(epocas))]
        ax.bar(epocas, pct, bottom=base, color=cor, width=0.68, edgecolor=BRANCO, linewidth=1.5,
               label=nome.replace(" + Nacionais", ""))
        for i, p in enumerate(pct):
            if p >= 6:
                ax.text(i, base[i] + p / 2, f"{p:.0f}%", ha="center", va="center",
                        fontsize=8.5, fontweight="bold", color=cor_txt)
        base = [b + p for b, p in zip(base, pct)]
    ax.set_ylim(0, 100)
    ax.grid(False)
    ax.set_yticks([])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncols=6, fontsize=9,
              handlelength=1.2, columnspacing=1.4)
    guardar(fig, "04_composicao_receitas.png")


def balanco_sad(con):
    rows = q(con, """SELECT epoca_id, ativo_total, passivo_total, capital_proprio
                     FROM balanco WHERE entidade_id = 'SAD' ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    at, ps = [r[1] for r in rows], [r[2] for r in rows]
    x = range(len(epocas))
    fig, ax = figura("Ativo vs. passivo da SAD",
                     "Balanço a 30 de junho · A área amarela é o capital próprio negativo (passivo > ativo) · 2025/26: comunicado de contas")
    ax.fill_between(x, at, ps, where=[p > a for p, a in zip(ps, at)], interpolate=True,
                    color=AMARELO, alpha=0.55, linewidth=0, label="Capital próprio negativo")
    ax.plot(x, ps, color=PRETO, linewidth=2.4, marker="o", markersize=6, label="Passivo")
    ax.plot(x, at, color=CINZA_ESCURO, linewidth=2.4, marker="o", markersize=6,
            markerfacecolor=BRANCO, markeredgewidth=2, label="Ativo")
    ultimo = rows[-1]
    ax.annotate(f"Capital próprio\n{euros_m(ultimo[3], 1)}\nem {ultimo[0]}", (len(epocas) - 1.5, (ultimo[1] + ultimo[2]) / 2 - 11e6),
                ha="center", va="center", fontsize=9, fontweight="bold")
    ax.set_xticks(list(x), epocas, fontsize=9)
    ax.yaxis.set_major_formatter(eixo_m)
    ax.set_ylim(0, max(ps) * 1.12)
    ax.legend(loc="upper left")
    guardar(fig, "05_balanco_sad.png")


def posicao_vs_pessoal(con):
    rows = q(con, """SELECT d.epoca_id, d.posicao_liga, k.gastos_pessoal, d.fase_europeia
                     FROM desempenho_desportivo d
                     JOIN v_kpis k ON k.epoca_id = d.epoca_id AND k.entidade_id = 'SAD'
                     WHERE k.gastos_pessoal IS NOT NULL ORDER BY d.epoca_id""")
    fig, ax = figura("Salários vs. classificação",
                     "SAD · Gastos com pessoal e lugar na Liga em cada época · Gastar mais não garantiu melhores lugares")
    estilos = {
        "Fase de grupos": (AMARELO, PRETO, "Europa: fase de grupos ou mais"),
        "Oitavos de final": (AMARELO, PRETO, "Europa: fase de grupos ou mais"),
        "Pré-eliminatória": (CINZA, CINZA_ESCURO, "Europa: só pré-eliminatórias"),
        None: (BRANCO, PRETO, "Sem Europa"),
    }
    vistos = set()
    for ep, pos, pes, fase in rows:
        face, borda, rot = estilos[fase]
        ax.scatter(pes, pos, s=150, color=face, edgecolor=borda, linewidth=1.6, zorder=3,
                   label=None if rot in vistos else rot)
        vistos.add(rot)
        esquerda = ep in ("2013/14", "2021/22")
        ax.annotate(ep, (pes, pos), xytext=(-11 if esquerda else 11, -3), textcoords="offset points",
                    ha="right" if esquerda else "left", fontsize=8.5, color=TEXTO_2)
    corr = q(con, """WITH x AS (SELECT k.gastos_pessoal g, d.posicao_liga p FROM v_kpis k
                     JOIN desempenho_desportivo d ON d.epoca_id = k.epoca_id
                     WHERE k.entidade_id = 'SAD' AND k.gastos_pessoal IS NOT NULL),
                     m AS (SELECT AVG(g) mg, AVG(p) mp FROM x)
                     SELECT SUM((g-mg)*(p-mp)) / (sqrt(SUM((g-mg)*(g-mg))) * sqrt(SUM((p-mp)*(p-mp))))
                     FROM x, m""")[0][0]
    ax.text(0.99, 0.04, f"Correlação: {corr:.1f}".replace(".", ",").replace("-", "−") + " (fraca)",
            transform=ax.transAxes, ha="right", fontsize=9.5, fontweight="bold")
    ax.invert_yaxis()
    ax.set_yticks(range(1, 12), [f"{i}.º" for i in range(1, 12)])
    ax.set_ylim(11, 3)
    ax.set_xlim(3e6, 23e6)
    ax.xaxis.set_major_formatter(eixo_m)
    ax.grid(axis="both")
    ax.set_xlabel("Gastos com pessoal da SAD")
    ax.set_ylabel("Lugar na Liga")
    ax.legend(loc="lower center", bbox_to_anchor=(0.62, 0.02))
    guardar(fig, "06_salarios_vs_classificacao.png")


def main():
    OUT.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    print("Gráficos gerados:")
    capa(con)
    resultado_por_entidade(con)
    receitas_vs_pessoal(con)
    dependencia_vendas(con)
    composicao_receitas(con)
    balanco_sad(con)
    posicao_vs_pessoal(con)


if __name__ == "__main__":
    main()
