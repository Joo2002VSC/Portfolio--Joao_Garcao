"""
Gera os gráficos do Diário de Aprendizagem de Línguas a partir da base de dados.
Cada gráfico corresponde a uma consulta SQL (ver sql/02_consultas.sql).

Uso:
    python scripts/graficos.py
Saída:
    graficos/*.png
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

RAIZ = Path(__file__).resolve().parent.parent
BD = RAIZ / "dados" / "diario.db"
SAIDA = RAIZ / "graficos"

# --- Paleta (validada para daltonismo; ordem fixa, a cor segue a língua) ---
COR = {"Neerlandês": "#2a78d6", "Francês": "#eb6834", "Italiano": "#1baf7a"}
ORDEM = list(COR)
SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
MUTED = "#898781"
GRELHA = "#e1e0d9"
AZUL_SEQ = ["#ecf3fc", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "figure.facecolor": SUPERFICIE,
    "axes.facecolor": SUPERFICIE,
    "savefig.facecolor": SUPERFICIE,
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "text.color": TEXTO,
    "axes.labelcolor": TEXTO_2,
    "axes.edgecolor": GRELHA,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": TEXTO_2,
    "ytick.labelcolor": TEXTO_2,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": GRELHA,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "legend.frameon": False,
})

MESES_PT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def fmt_mes(x, _pos=None):
    d = mdates.num2date(x)
    return MESES_PT[d.month - 1]


def titulo(ax, texto, sub=None):
    ax.set_title(texto, loc="left", fontsize=14, fontweight="bold", color=TEXTO, pad=26 if sub else 12)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10, color=TEXTO_2, va="bottom")


def legenda(ax, **kw):
    handles = [plt.Line2D([], [], color=COR[l], lw=6) for l in ORDEM]
    ax.legend(handles, ORDEM, ncol=3, loc="upper left", bbox_to_anchor=(0, -0.08),
              fontsize=10, handlelength=1.2, **kw)


def rotulos_finais(ax, x, valores, fmt):
    """Etiquetas diretas no fim das linhas, afastadas para não se sobreporem."""
    passo = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.065
    ordenadas = sorted(valores.items(), key=lambda kv: kv[1])
    posicoes, ultimo = {}, None
    for lingua, v in ordenadas:
        y = v if ultimo is None else max(v, ultimo + passo)
        posicoes[lingua], ultimo = y, y
    for lingua, v in valores.items():
        ax.text(x, posicoes[lingua], fmt(lingua, v), va="center",
                fontsize=10, color=TEXTO_2, clip_on=False)


def guardar(fig, nome):
    SAIDA.mkdir(exist_ok=True)
    fig.savefig(SAIDA / nome, dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("  ✓", nome)


# ---------------------------------------------------------------------------
# 1. Palavras novas por semana  (P1)
# ---------------------------------------------------------------------------
def palavras_por_semana(con):
    df = pd.read_sql_query("""
        SELECT date(p.data_adicionada, 'weekday 0', '-6 days') AS semana,
               i.nome AS idioma, COUNT(*) AS n
        FROM palavras p JOIN idiomas i ON i.id = p.idioma_id
        GROUP BY semana, idioma
    """, con, parse_dates=["semana"])
    semanas = pd.date_range(df.semana.min(), df.semana.max(), freq="W-MON")
    tabela = df.pivot(index="semana", columns="idioma", values="n").reindex(semanas).fillna(0)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    finais = {}
    for lingua in ORDEM:
        y = tabela[lingua].rolling(3, min_periods=1).mean()   # média móvel de 3 semanas
        ax.plot(tabela.index, y, color=COR[lingua], lw=2, solid_capstyle="round")
        finais[lingua] = y.iloc[-1]
    ax.set_ylim(0, None)
    ax.set_xlim(tabela.index[0], tabela.index[-1])
    rotulos_finais(ax, tabela.index[-1] + pd.Timedelta(days=3), finais,
                   lambda l, v: f"{l}  {v:.1f}")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(fmt_mes)
    ax.set_ylabel("palavras novas / semana")
    titulo(ax, "Quantas palavras novas aprendo por semana?",
           "Média móvel de 3 semanas, por língua")
    legenda(ax)
    guardar(fig, "1_palavras_por_semana.png")


# ---------------------------------------------------------------------------
# 2. Vocabulário acumulado  (E4)
# ---------------------------------------------------------------------------
def vocabulario_acumulado(con):
    df = pd.read_sql_query("""
        SELECT i.nome AS idioma, p.data_adicionada AS data,
               SUM(COUNT(*)) OVER (PARTITION BY i.nome ORDER BY p.data_adicionada) AS total
        FROM palavras p JOIN idiomas i ON i.id = p.idioma_id
        GROUP BY i.nome, p.data_adicionada
    """, con, parse_dates=["data"])
    fim = pd.read_sql_query("SELECT MAX(data) AS d FROM sessoes", con, parse_dates=["d"]).d[0]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    finais = {}
    for lingua in ORDEM:
        sub = df[df.idioma == lingua]
        x = list(sub.data) + [fim]
        y = list(sub.total) + [sub.total.iloc[-1]]
        ax.step(x, y, where="post", color=COR[lingua], lw=2)
        finais[lingua] = y[-1]
    ax.set_ylim(0, None)
    ax.set_xlim(df.data.min(), fim)
    rotulos_finais(ax, fim + pd.Timedelta(days=3), finais, lambda l, v: f"{l}  {int(v)}")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(fmt_mes)
    ax.set_ylabel("palavras no total")
    titulo(ax, "Vocabulário acumulado", "Total de palavras e expressões registadas por língua")
    legenda(ax)
    guardar(fig, "2_vocabulario_acumulado.png")


# ---------------------------------------------------------------------------
# 3. Que língua estou a negligenciar?  (P2)
# ---------------------------------------------------------------------------
def linguas_negligenciadas(con):
    df = pd.read_sql_query("""
        WITH hoje AS (SELECT MAX(data) AS d FROM sessoes)
        SELECT i.nome AS idioma,
               CAST(julianday(hoje.d) - julianday(MAX(s.data)) AS INT) AS dias,
               SUM(CASE WHEN s.data > date(hoje.d, '-30 days') THEN s.duracao_min ELSE 0 END) AS ult30,
               SUM(s.duracao_min) * 30.0 /
                   (julianday(hoje.d) - julianday(MIN(s.data)) + 1) AS media30
        FROM sessoes s JOIN idiomas i ON i.id = s.idioma_id CROSS JOIN hoje
        GROUP BY i.nome
    """, con).set_index("idioma").loc[ORDEM[::-1]]

    fig, ax = plt.subplots(figsize=(10, 3.6))
    y = np.arange(len(df))
    ax.barh(y, df.ult30, height=0.5, color=[COR[l] for l in df.index])
    ax.scatter(df.media30, y, marker="|", s=900, color=TEXTO, linewidths=2, zorder=3)
    for i, (lingua, r) in enumerate(df.iterrows()):
        dias = int(r.dias)
        if dias == 0:
            estado = "estudei hoje"
        elif dias > 14:
            estado = f"sem estudar há {dias} dias"
        else:
            estado = f"última sessão há {dias} dia{'s' if dias != 1 else ''}"
        ax.text(max(r.ult30, r.media30) + 8, i, f"{int(r.ult30)} min   ·   {estado}",
                va="center", fontsize=10, color=TEXTO_2)
    ax.set_yticks(y, df.index, fontsize=11, color=TEXTO)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlim(0, df[["ult30", "media30"]].max().max() * 1.75)
    ax.set_xlabel("minutos de estudo nos últimos 30 dias")
    titulo(ax, "Que língua tenho negligenciado?",
           "Barra = últimos 30 dias  ·  traço preto = a minha média de 30 dias no período todo")
    guardar(fig, "3_linguas_negligenciadas.png")


# ---------------------------------------------------------------------------
# 4. Palavras que erro mais  (P3)
# ---------------------------------------------------------------------------
def palavras_mais_erradas(con):
    df = pd.read_sql_query("""
        SELECT idioma, termo, traducao_pt, revisoes, erros, taxa_erro_pct
        FROM v_desempenho_palavras
        WHERE revisoes >= 4
        ORDER BY taxa_erro_pct DESC, erros DESC
        LIMIT 12
    """, con).iloc[::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(df))
    ax.barh(y, df.taxa_erro_pct, height=0.6, color=[COR[l] for l in df.idioma])
    for i, r in enumerate(df.itertuples()):
        ax.text(r.taxa_erro_pct + 1.2, i, f"{r.taxa_erro_pct:.0f}%  ({r.erros}/{r.revisoes})",
                va="center", fontsize=9.5, color=TEXTO_2)
    rotulos = [f"{r.termo}  ·  {r.traducao_pt}" for r in df.itertuples()]
    ax.set_yticks(y, rotulos, fontsize=10, color=TEXTO)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.set_xlabel("taxa de erro nas revisões (mín. 4 revisões)")
    titulo(ax, "Que palavras erro mais vezes?", "As 12 palavras com maior taxa de erro, em todas as línguas")
    legenda(ax)
    ax.get_legend().set_bbox_to_anchor((0, -0.11))
    guardar(fig, "4_palavras_mais_erradas.png")


# ---------------------------------------------------------------------------
# 5. A revisão funciona?  (E6)
# ---------------------------------------------------------------------------
def curva_revisao(con):
    df = pd.read_sql_query("""
        WITH numeradas AS (
            SELECT r.acertou, i.nome AS idioma,
                   ROW_NUMBER() OVER (PARTITION BY r.palavra_id ORDER BY r.data, r.id) AS n
            FROM revisoes r
            JOIN palavras p ON p.id = r.palavra_id
            JOIN idiomas  i ON i.id = p.idioma_id
        )
        SELECT MIN(n, 8) AS n, 100.0 * SUM(1 - acertou) / COUNT(*) AS taxa, COUNT(*) AS tentativas
        FROM numeradas GROUP BY MIN(n, 8) ORDER BY 1
    """, con)

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.bar(df.n, df.taxa, width=0.6, color=AZUL_SEQ[4])
    for r in df.itertuples():
        ax.text(r.n, r.taxa + 1, f"{r.taxa:.0f}%", ha="center", fontsize=10, color=TEXTO_2)
    ax.set_xticks(df.n, [f"{n}.ª" if n < 8 else "8.ª+" for n in df.n])
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, df.taxa.max() * 1.25)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.set_xlabel("n.º da revisão da mesma palavra")
    ax.set_ylabel("taxa de erro")
    titulo(ax, "A revisão funciona?", "Taxa de erro conforme quantas vezes já revi a palavra (todas as línguas)")
    guardar(fig, "5_curva_revisao.png")


# ---------------------------------------------------------------------------
# 6. Calendário de estudo (estilo GitHub)
# ---------------------------------------------------------------------------
def calendario(con):
    df = pd.read_sql_query("SELECT data, SUM(duracao_min) AS m FROM sessoes GROUP BY data",
                           con, parse_dates=["data"]).set_index("data").m
    inicio = df.index.min().date()
    inicio -= timedelta(days=inicio.weekday())
    fim = df.index.max().date()
    dias = pd.date_range(inicio, fim)
    valores = df.reindex(dias).fillna(0)
    n_sem = (len(dias) + 6) // 7
    grelha = np.full((7, n_sem), np.nan)
    for k, (d, v) in enumerate(valores.items()):
        grelha[d.weekday(), k // 7] = v

    cmap = LinearSegmentedColormap.from_list("azul", AZUL_SEQ)
    cmap.set_under(GRELHA)
    fig, ax = plt.subplots(figsize=(11, 2.9))
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    vmax = np.nanpercentile(grelha[grelha > 0], 95)
    for semana in range(n_sem):
        for dia in range(7):
            v = grelha[dia, semana]
            if np.isnan(v):
                continue
            cor = GRELHA if v == 0 else cmap(min(v / vmax, 1) * 0.85 + 0.15)
            ax.add_patch(plt.Rectangle((semana + 0.08, 6 - dia + 0.08), 0.84, 0.84,
                                       color=cor, linewidth=0))
    ax.set_xlim(0, n_sem)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.set_yticks([6.5, 4.5, 2.5, 0.5], ["seg", "qua", "sex", "dom"], fontsize=9)
    ax.tick_params(length=0)
    marcas = [(k, d) for k, d in enumerate(dias[::7]) if d.day <= 7]
    ax.set_xticks([k + 0.5 for k, _ in marcas], [MESES_PT[d.month - 1] for _, d in marcas], fontsize=9)
    ax.xaxis.tick_top()
    total_dias = int((valores > 0).sum())
    ax.set_title(f"Calendário de estudo  ·  {total_dias} dias com estudo em {len(dias)}",
                 loc="left", fontsize=14, fontweight="bold", pad=24)
    # legenda de intensidade
    ax.text(n_sem - 7.6, -0.75, "menos", fontsize=9, color=TEXTO_2, ha="right", va="center")
    for j, f in enumerate([0, 0.25, 0.5, 0.75, 1]):
        cor = GRELHA if f == 0 else cmap(f * 0.85 + 0.15)
        ax.add_patch(plt.Rectangle((n_sem - 7.3 + j, -1.17), 0.84, 0.84, color=cor, clip_on=False))
    ax.text(n_sem - 2.2, -0.75, "mais minutos", fontsize=9, color=TEXTO_2, va="center")
    guardar(fig, "6_calendario_estudo.png")


def main():
    print("A gerar gráficos…")
    with sqlite3.connect(BD) as con:
        palavras_por_semana(con)
        vocabulario_acumulado(con)
        linguas_negligenciadas(con)
        palavras_mais_erradas(con)
        curva_revisao(con)
        calendario(con)


if __name__ == "__main__":
    main()
