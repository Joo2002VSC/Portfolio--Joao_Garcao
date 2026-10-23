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

FONTE = "Fontes: Relatórios e Contas da Vitória SC SAD e VSC Contas (vitoriasempre.net) · Análise: João Garção"

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


def guardar(fig, nome, fonte=FONTE):
    fig.patches.append(Rectangle((0, 0), 1, 0.006, transform=fig.transFigure,
                                 color=AMARELO, zorder=0))
    fig.text(0.035, 0.03, fonte, fontsize=8, color=CINZA_ESCURO)
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


def divida_e_juros(con):
    rows = q(con, """SELECT epoca_id, financiamentos_nc, financiamentos_c, juros_suportados
                     FROM balanco_sad_rc WHERE financiamentos_nc IS NOT NULL ORDER BY epoca_id""")
    taxas = dict(q(con, """WITH f AS (SELECT epoca_id, financiamentos_nc + financiamentos_c AS fin,
                                juros_suportados AS j,
                                LAG(financiamentos_nc + financiamentos_c) OVER (ORDER BY epoca_id) AS ant
                                FROM balanco_sad_rc WHERE financiamentos_nc IS NOT NULL)
                           SELECT epoca_id, 100.0 * j / ((fin + ant) / 2.0) FROM f WHERE ant IS NOT NULL"""))
    epocas = [r[0] for r in rows]
    x = range(len(epocas))
    fig, ax = figura("Dívida financeira e juros da SAD",
                     "Financiamentos obtidos a 30 de junho (esquerda) e juros suportados na época (direita) · Fonte: R&C da SAD")
    fig.delaxes(ax)
    topo = 1 - 0.62 / 5.6 - 0.95 / 5.6
    ax1 = fig.add_axes([0.085, 0.14, 0.40, topo - 0.14])
    ax2 = fig.add_axes([0.57, 0.14, 0.40, topo - 0.14])
    ax1.bar(x, [r[1] for r in rows], color=CINZA, width=0.68, label="Médio e longo prazo")
    ax1.bar(x, [r[2] for r in rows], bottom=[r[1] for r in rows], color=PRETO, width=0.68,
            label="Curto prazo (< 1 ano)")
    for i, r in enumerate(rows):
        ax1.text(i, r[1] + r[2] + 0.6e6, euros_m(r[1] + r[2], 1), ha="center", fontsize=7.5)
    ax1.set_xticks(list(x), [e[2:] for e in epocas], fontsize=8.5)
    ax1.yaxis.set_major_formatter(eixo_m)
    ax1.set_ylim(0, 40e6)
    ax1.legend(loc="upper left", fontsize=8.5)
    ax1.set_title("Financiamentos obtidos", loc="left", fontsize=10.5, fontweight="bold")
    ax2.bar(x, [r[3] or 0 for r in rows], color=AMARELO, edgecolor=PRETO, linewidth=0.6, width=0.68)
    for i, r in enumerate(rows):
        t = taxas.get(r[0])
        rot = (euros_m(r[3], 1) if r[3] else "0") + (f"\n{t:.0f}%".replace(".", ",") if t else "")
        ax2.text(i, (r[3] or 0) + 0.1e6, rot, ha="center", fontsize=7.5, linespacing=1.1)
    ax2.set_xticks(list(x), [e[2:] for e in epocas], fontsize=8.5)
    ax2.yaxis.set_major_formatter(eixo_m)
    ax2.set_ylim(0, 6.2e6)
    ax2.set_title("Juros suportados · % = taxa de juro implícita", loc="left", fontsize=10.5, fontweight="bold")
    guardar(fig, "07_divida_e_juros.png")


def racios_balanco(con):
    rows = q(con, """SELECT epoca_id, 1.0 * passivo_total / ativo_total, 1.0 * ativo_corrente / passivo_corrente
                     FROM balanco_sad_rc ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    x = range(len(epocas))
    fig, ax = figura("Endividamento e liquidez da SAD",
                     "Acima de 1, o passivo supera o ativo (falência técnica) · Abaixo de 1, as dívidas de curto prazo superam o ativo de curto prazo")
    ax.axhline(1, color=PRETO, linewidth=1, linestyle=(0, (4, 3)))
    ax.text(len(epocas) - 0.6, 1.03, "limiar = 1", fontsize=8.5, color=TEXTO_2, ha="right")
    ax.fill_between(x, 1, [r[1] for r in rows], where=[r[1] > 1 for r in rows], interpolate=True,
                    color=AMARELO, alpha=0.45, linewidth=0)
    ax.plot(x, [r[1] for r in rows], color=PRETO, linewidth=2.4, marker="o", markersize=6,
            label="Endividamento (passivo / ativo)")
    ax.plot(x, [r[2] for r in rows], color=CINZA_ESCURO, linewidth=2.4, marker="o", markersize=6,
            markerfacecolor=BRANCO, markeredgewidth=2, label="Liquidez geral (ativo corrente / passivo corrente)")
    for i, r in enumerate(rows):
        if r[0] in ("2013/14", "2023/24", "2018/19"):
            ax.annotate(f"{r[1]:.2f}".replace(".", ","), (i, r[1]), xytext=(0, 9), textcoords="offset points",
                        ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(list(x), epocas, fontsize=9)
    ax.set_ylim(0, 2.2)
    ax.set_yticks([0, 0.5, 1, 1.5, 2], ["0", "0,5", "1,0", "1,5", "2,0"])
    ax.legend(loc="upper center", ncols=2, fontsize=9)
    guardar(fig, "08_endividamento_liquidez.png")


def funcionarios(con):
    rows = q(con, """SELECT epoca_id, jogadores,
                            COALESCE(treinadores_profissional,0) + COALESCE(treinadores_formacao,0),
                            COALESCE(apoio_futebol_profissional,0) + COALESCE(outro_pessoal,0),
                            funcionarios, total_gastos_pessoal / funcionarios
                     FROM pessoal_sad ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    x = range(len(epocas))
    fig, ax = figura("Funcionários da SAD",
                     "Número médio de funcionários por categoria · Desde 2012/13, os jogadores quase duplicaram e o restante pessoal multiplicou-se por mais de 8")
    base = [0] * len(rows)
    for idx, nome, cor in [(1, "Jogadores", PRETO), (2, "Treinadores", CINZA_ESCURO), (3, "Staff e apoio", AMARELO)]:
        vals = [r[idx] for r in rows]
        ax.bar(x, vals, bottom=base, color=cor, width=0.68, label=nome, edgecolor=BRANCO, linewidth=1.2)
        base = [b + v for b, v in zip(base, vals)]
    for i, r in enumerate(rows):
        ax.text(i, r[4] + 4, str(r[4]), ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(list(x), epocas, fontsize=9)
    ax.set_ylim(0, 255)
    ax.set_ylabel("Funcionários")
    ax.legend(loc="upper left")
    guardar(fig, "09_funcionarios.png")


def barras_simples(ax, epocas, valores, cor=PRETO, rotulos=None, fmt=None):
    xs = range(len(epocas))
    ax.bar(xs, valores, color=cor, width=0.66, edgecolor=PRETO if cor in (AMARELO, AMARELO_CLARO) else cor,
           linewidth=0.6)
    ax.set_xticks(list(xs), epocas, fontsize=9)
    return xs


def reservas_ocultas(con):
    rows = q(con, """SELECT p.epoca_id, p.valor_bruto_alienado - p.amort_acumuladas_alienadas, t.vendas_brutas
                     FROM passes_jogadores p JOIN transferencias t
                       ON t.epoca_id = p.epoca_id AND t.entidade_id = 'SAD' ORDER BY p.epoca_id""")
    epocas = [r[0] for r in rows]
    fig, ax = figura("Quanto vale o plantel, de facto",
                     "SAD · Valor contabilístico dos passes vendidos vs. valor de venda · A diferença é a 'reserva oculta' do plantel")
    barras_agrupadas(ax, epocas, [
        ("Valor contabilístico dos jogadores vendidos", [r[1] for r in rows], CINZA),
        ("Vendas brutas", [r[2] for r in rows], PRETO),
    ], largura=0.72)
    for x, r in enumerate(rows):
        ax.annotate(f"{r[2] / r[1]:.0f}×", (x + 0.18, r[2]), xytext=(0, 4), textcoords="offset points",
                    ha="center", fontsize=9, fontweight="bold")
    ax.set_ylim(0, 55e6)
    ax.legend(loc="upper left")
    guardar(fig, "10_reservas_ocultas.png")


def alavancagem(con):
    rows = q(con, """SELECT epoca_id, vendas_servicos, -(gastos_pessoal + fse + depreciacoes)
                     FROM v_dr WHERE entidade_id = 'SAD' AND vendas_servicos IS NOT NULL ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    fig, ax = figura("Custos fixos vs. receitas",
                     "SAD · % = parte dos custos fixos coberta pelas receitas · O resto tem de vir da venda de jogadores")
    xs = range(len(epocas))
    ax.bar(xs, [r[2] for r in rows], color=CINZA_CLARO, width=0.7, label="Custos fixos (pessoal + FSE + depreciações)")
    ax.bar(xs, [r[1] for r in rows], color=PRETO, width=0.42, label="Receitas (vendas e serviços)")
    for x, r in enumerate(rows):
        ax.text(x, r[2] + 0.5e6, f"{100 * r[1] / r[2]:.0f}%", ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(list(xs), epocas, fontsize=9)
    ax.yaxis.set_major_formatter(eixo_m)
    ax.set_ylim(0, 40e6)
    ax.legend(loc="upper left")
    guardar(fig, "11_custos_fixos_vs_receitas.png")


def racio_uefa(con):
    rows = q(con, """WITH base AS (
                        SELECT p.epoca_id, p.rem_jogadores + p.rem_treinadores + j.amortizacoes AS c,
                               k.vendas_servicos AS r,
                               AVG(t.mais_valias_liquidas) OVER (ORDER BY p.epoca_id
                                   ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS mv
                        FROM pessoal_sad p
                        JOIN passes_jogadores j ON j.epoca_id = p.epoca_id
                        JOIN v_kpis k ON k.epoca_id = p.epoca_id AND k.entidade_id = 'SAD'
                        LEFT JOIN transferencias t ON t.epoca_id = p.epoca_id AND t.entidade_id = 'SAD'
                        WHERE p.rem_jogadores IS NOT NULL)
                     SELECT epoca_id, 100.0 * c / (r + mv), 100.0 * c / r FROM base ORDER BY epoca_id""")
    epocas = [r[0] for r in rows]
    fig, ax = figura("Rácio de custos do plantel (UEFA)",
                     "SAD · Salários de jogadores e treinadores + amortizações de passes ÷ receitas · Aproximação ao regulamento")
    barras_agrupadas(ax, epocas, [
        ("Com média de 3 épocas de vendas de jogadores", [r[1] for r in rows], AMARELO),
        ("Sem vendas de jogadores", [r[2] for r in rows], CINZA),
    ], largura=0.72)
    ax.axhline(70, color=PRETO, linewidth=1.2, linestyle=(0, (4, 3)))
    ax.text(len(epocas) - 0.5, 72, "limite UEFA: 70%", ha="right", fontsize=9, fontweight="bold")
    for x, r in enumerate(rows):
        ax.text(x - 0.18, r[1] + 2, f"{r[1]:.0f}%", ha="center", fontsize=8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylim(0, 230)
    ax.legend(loc="upper left")
    guardar(fig, "12_racio_custos_plantel_uefa.png")


def centralizacao(con):
    rows = q(con, """WITH RECURSIVE lugar(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM lugar WHERE n < 18)
                     SELECT n, 225000000 * 0.332 / 18, 225000000 * 0.442 * (19 - n) / 171.0 FROM lugar""")
    tv = q(con, "SELECT valor FROM receitas_composicao WHERE categoria='Direitos TV' AND epoca_id='2024/25'")[0][0]
    fig, ax = figura("Centralização dos direitos TV: quanto vale cada lugar",
                     "Simulação ilustrativa · Contrato de 250 M€ · Parte igual + mérito repartido de forma linear · Sem a componente de audiências")
    xs = range(len(rows))
    ax.bar(xs, [r[1] for r in rows], color=CINZA, width=0.68, label="Parte igual (33,2%)")
    ax.bar(xs, [r[2] for r in rows], bottom=[r[1] for r in rows], color=PRETO, width=0.68,
           label="Mérito desportivo (44,2%, ilustrativo)")
    for i in (4, 5, 8):
        ax.patches[18 + i].set_facecolor(AMARELO)
        ax.patches[18 + i].set_edgecolor(PRETO)
    ax.axhline(tv, color=PRETO, linewidth=1.2, linestyle=(0, (4, 3)))
    ax.text(17.4, tv + 0.4e6, f"Vitória hoje: {euros_m(tv, 1)}", ha="right", fontsize=9, fontweight="bold")
    ax.set_xticks(list(xs), [f"{r[0]}.º" for r in rows], fontsize=9)
    ax.yaxis.set_major_formatter(eixo_m)
    ax.set_ylim(0, 16e6)
    ax.set_xlabel("Lugar na Liga · a amarelo, os lugares do Vitória nas últimas épocas (5.º, 6.º e 9.º)")
    ax.legend(loc="upper right")
    guardar(fig, "13_centralizacao_por_lugar.png")


def custo_por_ponto(con):
    rows = q(con, """SELECT d.epoca_id, 1.0 * p.total_gastos_pessoal / d.pontos, d.pontos
                     FROM desempenho_desportivo d JOIN pessoal_sad p ON p.epoca_id = d.epoca_id
                     WHERE d.epoca_id >= '2013/14' ORDER BY d.epoca_id""")
    epocas = [r[0] for r in rows]
    fig, ax = figura("Quanto custa cada ponto",
                     "SAD · Gastos com pessoal ÷ pontos na Liga · Em 2014/15, um ponto custava 80 mil €; em 2024/25, 380 mil €")
    xs = barras_simples(ax, epocas, [r[1] for r in rows], cor=PRETO)
    for x, r in enumerate(rows):
        ax.text(x, r[1] + 8e3, f"{r[1] / 1e3:.0f} mil €\n{r[2]} pts", ha="center", fontsize=8, linespacing=1.1)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e3:.0f} mil €" if v else "0"))
    ax.set_ylim(0, 560e3)
    guardar(fig, "14_custo_por_ponto.png")


def pct(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",").replace("-", "−") + "%"


def taxas_juro(con):
    rows = q(con, """SELECT epoca_id, bce_deposito, euribor_12m, ot_portugal_10a,
                            credito_empresas_pt, vitoria_implicita
                     FROM v_taxas_epoca WHERE epoca_id BETWEEN '2016/17' AND '2025/26'
                     ORDER BY epoca_id""")
    ep = [r[0] for r in rows]
    xs = range(len(ep))
    fig, ax = figura("O Vitória paga juros muito acima do mercado",
                     "Médias por época (julho a junho) · Taxa implícita da SAD = juros suportados ÷ dívida financeira média")
    ax.plot(xs, [r[1] for r in rows], color=CINZA, linewidth=2, label="BCE · facilidade de depósito")
    ax.plot(xs, [r[2] for r in rows], color=CINZA_ESCURO, linewidth=2, linestyle=(0, (4, 2)),
            label="Euribor a 12 meses")
    ax.plot(xs, [r[3] for r in rows], color=PRETO, linewidth=1.6, linestyle=(0, (1, 1.6)),
            label="Estado português · obrigações a 10 anos")
    pts = [(i, r[4]) for i, r in enumerate(rows) if r[4] is not None]
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], marker="s", s=46, color=BRANCO,
               edgecolor=PRETO, linewidth=1.4, zorder=4,
               label="Empresas em Portugal · crédito novo (meses disponíveis)")
    vi = [(i, r[5]) for i, r in enumerate(rows) if r[5] is not None]
    ax.plot([p[0] for p in vi], [p[1] for p in vi], color=PRETO, linewidth=3.2, zorder=5)
    ax.scatter([p[0] for p in vi], [p[1] for p in vi], s=90, color=AMARELO, edgecolor=PRETO,
               linewidth=1.6, zorder=6, label="Vitória SC SAD · taxa implícita")
    for i, v in vi:
        ax.annotate(pct(v), (i, v), xytext=(0, 10), textcoords="offset points", ha="center",
                    fontsize=9, fontweight="bold")
    ax.axhline(0, color=PRETO, linewidth=0.8)
    ax.set_xticks(list(xs), ep)
    ax.set_ylim(-1.5, 17.5)
    ax.set_yticks(range(0, 18, 3))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.legend(loc="upper left", fontsize=9, ncol=2)
    guardar(fig, "15_taxas_de_juro.png",
            "Fontes: R&C da Vitória SC SAD · BCE · euribor-rates.eu · OCDE/FRED · Banco de Portugal · Análise: João Garção")


def dispersao_regressao(con):
    rows = q(con, """SELECT d.epoca_id, -(d.gastos_pessoal + d.fse + d.depreciacoes) / 1e6, s.posicao_liga,
                            s.fase_europeia
                     FROM v_dr d JOIN desempenho_desportivo s ON s.epoca_id = d.epoca_id
                     WHERE d.entidade_id = 'SAD' AND d.gastos_pessoal IS NOT NULL AND d.fse IS NOT NULL
                     ORDER BY d.epoca_id""")
    xs = [r[1] for r in rows]
    ys = [r[2] for r in rows]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    r2 = 1 - sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / sum((y - my) ** 2 for y in ys)
    fig, ax = figura("Despesas da SAD vs. classificação",
                     "Despesas = pessoal + FSE + depreciações e amortizações · Reta de regressão linear (mínimos quadrados), 12 épocas")
    lim = (5, 40)
    ax.plot(lim, [a + b * lim[0], a + b * lim[1]], color=PRETO, linewidth=2, zorder=2)
    for ep, x, y, fase in rows:
        europa = fase in ("Fase de grupos", "Oitavos de final")
        ax.scatter(x, y, s=150, color=AMARELO if europa else BRANCO, edgecolor=PRETO,
                   linewidth=1.6, zorder=3)
        desvio = {"2021/22": (0, 13), "2024/25": (0, 13), "2019/20": (0, -19),
                  "2013/14": (14, -3), "2015/16": (-14, -3)}.get(ep, (0, -17))
        ha = "left" if desvio[0] > 0 else "right" if desvio[0] < 0 else "center"
        ax.annotate(ep, (x, y), xytext=desvio, textcoords="offset points",
                    ha=ha, va="center", fontsize=8.5, color=TEXTO_2)
    num = lambda v, c: f"{v:.{c}f}".replace(".", ",")
    eq = (f"Lugar previsto = {num(a, 2)} {'−' if b < 0 else '+'} {num(abs(b), 3)} × despesas (M€)\n"
          f"R² = {num(r2, 2)}: as despesas explicam só {r2 * 100:.0f}% das diferenças de lugar.\n"
          f"Cada 10 M€ a mais valem, em média, {num(abs(b) * 10, 1)} lugares.")
    ax.text(0.985, 0.05, eq, transform=ax.transAxes, ha="right", va="bottom", fontsize=9.5,
            bbox=dict(boxstyle="square,pad=0.6", facecolor=CINZA_CLARO, edgecolor="none"))
    ax.scatter([], [], s=110, color=AMARELO, edgecolor=PRETO, label="Fase de grupos europeia ou mais")
    ax.scatter([], [], s=110, color=BRANCO, edgecolor=PRETO, label="Restantes épocas")
    ax.legend(loc="upper left")
    ax.invert_yaxis()
    ax.set_ylim(11.2, 2.8)
    ax.set_yticks(range(3, 12), [f"{i}.º" for i in range(3, 12)])
    ax.set_xlim(*lim)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f} M€"))
    ax.grid(axis="both")
    ax.set_xlabel("Despesas da SAD na época")
    ax.set_ylabel("Lugar na Liga")
    guardar(fig, "16_despesas_vs_classificacao.png")


def vendas_vs_receitas(con):
    rows = q(con, """SELECT t.epoca_id, d.vendas_servicos, t.vendas_brutas
                     FROM transferencias t JOIN v_dr d ON d.epoca_id = t.epoca_id AND d.entidade_id = 'SAD'
                     WHERE t.entidade_id = 'SAD' AND d.vendas_servicos IS NOT NULL ORDER BY t.epoca_id""")
    ep = [r[0] for r in rows]
    fig, ax = figura("A SAD vende mais em jogadores do que fatura na operação",
                     "Receitas da operação (vendas e serviços) vs. vendas brutas de jogadores · Rótulo: euros de vendas por cada euro de receita")
    barras_agrupadas(ax, ep, [("Receitas da operação", [r[1] for r in rows], CINZA),
                              ("Vendas brutas de jogadores", [r[2] for r in rows], AMARELO)])
    for i, (e, rec, ven) in enumerate(rows):
        ax.text(i, max(rec, ven) + 1.3e6, f"{ven / rec:.2f}×".replace(".", ","), ha="center",
                fontsize=10, fontweight="bold", **{"family": FAMILIA_TITULO})
    ax.set_ylim(0, 56e6)
    ax.legend(loc="upper left")
    guardar(fig, "17_vendas_vs_receitas.png")


def centralizacao_equilibrio(con):
    defice = q(con, """SELECT AVG(rl_sem_mais_valias) FROM v_kpis
                       WHERE entidade_id = 'SAD' AND epoca_id BETWEEN '2022/23' AND '2024/25'""")[0][0]
    tv = q(con, "SELECT valor FROM receitas_composicao WHERE categoria='Direitos TV' AND epoca_id='2024/25'")[0][0]
    cen = []
    for contrato in (200e6, 250e6, 300e6):
        for n in (4, 6, 9):
            novo = contrato * 0.9 * 0.332 / 18 + contrato * 0.9 * 0.442 * (19 - n) / 171
            cen.append((f"{contrato / 1e6:.0f} M€ · {n}.º lugar", novo - tv))
    fig, ax = figura("Centralização: ajuda, mas não fecha o défice sozinha",
                     f"Défice antes de vendas de jogadores: {euros_m(defice, 1)} por época (média 2022/23–2024/25) · Ganho face aos {euros_m(tv, 1)} de TV atuais",
                     altura=6.2, base=0.2)
    pos = ax.get_position()
    ax.set_position([0.17, pos.y0, 0.8, pos.height])
    ys = range(len(cen))[::-1]
    total = -defice
    for y, (rot, ganho) in zip(ys, cen):
        ax.barh(y, ganho, color=AMARELO, edgecolor=PRETO, linewidth=0.8, height=0.62)
        ax.barh(y, total - ganho, left=ganho, color=CINZA_CLARO, height=0.62)
        ax.text(ganho + 0.3e6, y, f"+{euros_m(ganho, 1)} · {ganho / total * 100:.0f}%".replace(".", ","),
                va="center", fontsize=9, fontweight="bold")
        ax.text(total - 0.3e6, y, f"faltam {euros_m(total - ganho, 1)}", va="center", ha="right",
                fontsize=9, color=TEXTO_2)
    ax.set_yticks(list(ys), [c[0] for c in cen], fontsize=9.5)
    ax.set_xlim(0, total)
    ax.set_xticks([0, 4e6, 8e6, 12e6, 16e6, 20e6])
    ax.xaxis.set_major_formatter(eixo_m)
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=AMARELO, edgecolor=PRETO, label="Coberto pela centralização"),
                       Patch(facecolor=CINZA_CLARO, label="Ainda a cobrir com vendas de jogadores ou cortes")],
              loc="upper center", bbox_to_anchor=(0.42, -0.08), ncol=2)
    guardar(fig, "18_centralizacao_equilibrio.png")


def painel_indicadores(con):
    rows = q(con, """SELECT d.epoca_id,
                       100.0 * (d.vendas_servicos + d.fse + d.gastos_pessoal) / d.vendas_servicos,
                       100.0 * d.resultado_liquido / b.ativo_total,
                       1.0 * (r.financiamentos_nc + r.financiamentos_c) / d.vendas_servicos,
                       100.0 * c.operacional / d.vendas_servicos
                     FROM v_dr d
                     JOIN balanco b ON b.entidade_id = 'SAD' AND b.epoca_id = d.epoca_id
                     LEFT JOIN balanco_sad_rc r ON r.epoca_id = d.epoca_id
                     LEFT JOIN cash_flow c ON c.entidade_id = 'SAD' AND c.epoca_id = d.epoca_id
                     WHERE d.entidade_id = 'SAD' AND d.vendas_servicos IS NOT NULL AND d.epoca_id >= '2016/17'
                     ORDER BY d.epoca_id""")
    ep = [r[0][2:] for r in rows]
    fig, ax0 = figura("Painel de indicadores financeiros",
                      "SAD · 2016/17 a 2024/25 · Percentagens sobre as receitas da operação (vendas e serviços), salvo indicação",
                      altura=7.4, base=0.1)
    ax0.remove()
    paineis = [
        ("Margem corrente sem vendas", "(receitas − pessoal − FSE) ÷ receitas", 1, "%"),
        ("Rendibilidade do ativo", "resultado líquido ÷ ativo", 2, "%"),
        ("Dívida financeira ÷ receitas", "vezes as receitas anuais", 3, "x"),
        ("Cash flow operacional", "fluxo de caixa da operação ÷ receitas", 4, "%"),
    ]
    pos = [(0.07, 0.5), (0.56, 0.5), (0.07, 0.1), (0.56, 0.1)]
    for (tit, sub, col, un), (x0, y0) in zip(paineis, pos):
        ax = fig.add_axes([x0, y0, 0.4, 0.25])
        vals = [r[col] for r in rows]
        cores = [AMARELO if (v or 0) >= 0 else PRETO for v in vals] if un == "%" else [PRETO] * len(vals)
        if un == "x":
            cores = [AMARELO if v < 1 else PRETO for v in vals]
        ax.bar(range(len(vals)), vals, color=cores, edgecolor=PRETO, linewidth=0.6, width=0.7)
        ax.axhline(0, color=PRETO, linewidth=1)
        ax.set_xticks(range(len(ep)), ep, fontsize=8.5)
        ax.tick_params(axis="y", labelsize=8.5)
        fmt = (lambda v, _: f"{v:.0f}%") if un == "%" else (lambda v, _: f"{v:.1f}×".replace(".", ","))
        ax.yaxis.set_major_formatter(FuncFormatter(fmt))
        ax.set_title(tit.upper(), loc="left", fontsize=10.5, pad=20, **TITULO)
        ax.text(0, 1.04, sub, transform=ax.transAxes, fontsize=8.5, color=TEXTO_2)
        ultimo = vals[-1]
        ax.annotate(pct(ultimo, 0) if un == "%" else f"{ultimo:.1f}×".replace(".", ","),
                    (len(vals) - 1, ultimo), xytext=(0, 5 if ultimo >= 0 else -12),
                    textcoords="offset points", ha="center", fontsize=8.5, fontweight="bold")
    guardar(fig, "19_painel_indicadores.png")


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
    divida_e_juros(con)
    racios_balanco(con)
    funcionarios(con)
    reservas_ocultas(con)
    alavancagem(con)
    racio_uefa(con)
    centralizacao(con)
    custo_por_ponto(con)
    taxas_juro(con)
    dispersao_regressao(con)
    vendas_vs_receitas(con)
    centralizacao_equilibrio(con)
    painel_indicadores(con)


if __name__ == "__main__":
    main()
