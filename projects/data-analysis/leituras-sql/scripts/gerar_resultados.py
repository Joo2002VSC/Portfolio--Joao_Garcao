"""Corre as consultas de sql/02_consultas.sql, grava os resultados em resultados.md
e gera os gráficos da pasta graficos/ (no estilo bege do Goodreads).

Uso:  python scripts/importar.py && python scripts/gerar_resultados.py
"""
import re
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from caminhos import CONSULTAS, DB, GRAFICOS, PASTA

con = sqlite3.connect(DB)

# ---------- 1. resultados.md ----------
blocos = re.split(r"^-- @ ", CONSULTAS.read_text(encoding="utf-8"), flags=re.M)[1:]
saida = ["# Resultados das consultas\n",
         "_Gerado automaticamente por `scripts/gerar_resultados.py`._\n"]
for bloco in blocos:
    titulo, consulta = bloco.split("\n", 1)
    df = pd.read_sql_query(consulta, con)
    saida += [f"\n## {titulo.strip()}\n", df.fillna("").to_markdown(index=False), "\n"]
(PASTA / "resultados.md").write_text("\n".join(saida), encoding="utf-8")

# ---------- 2. gráficos — paleta Goodreads ----------
BEGE, PAPEL = "#F4F1EA", "#FBF9F4"
TINTA, TINTA2, REGRA = "#382110", "#6B5A45", "#E3DCCB"
VERDE, LARANJA, CASTANHO_CLARO = "#008A7B", "#C76E1A", "#D3C5A8"

plt.rcParams.update({
    "figure.dpi": 160, "savefig.dpi": 160,
    "figure.facecolor": BEGE, "axes.facecolor": BEGE, "savefig.facecolor": BEGE,
    "font.family": "serif", "font.serif": ["Georgia", "DejaVu Serif"], "font.size": 10,
    "text.color": TINTA, "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2,
    "axes.edgecolor": REGRA, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.grid": True, "axes.grid.axis": "y",
    "grid.color": REGRA, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "xtick.major.size": 0, "ytick.major.size": 0,
})
GRAFICOS.mkdir(exist_ok=True)


def titulo(ax, t, sub=None):
    ax.set_title(t, loc="left", fontsize=14, fontweight="bold", color=TINTA, pad=22 if sub else 10)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9, color=TINTA2, va="bottom")


def guardar(fig, nome):
    fig.text(0.99, 0.01, "Dados: exportação do Goodreads · SQLite", ha="right", fontsize=7, color=TINTA2)
    fig.tight_layout()
    fig.savefig(GRAFICOS / nome)
    plt.close(fig)


def q(sql):
    return pd.read_sql_query(sql, con)


ano_ref = int(q("SELECT strftime('%Y', MAX(data_lida)) AS a FROM leituras").a[0])

# 1) livros por ano
df = q("""SELECT strftime('%Y', data_lida) AS ano, COUNT(*) AS livros
          FROM leituras WHERE estante='read' AND data_lida IS NOT NULL GROUP BY ano ORDER BY ano""")
fig, ax = plt.subplots(figsize=(7.2, 4))
cores = [VERDE if a == str(ano_ref) else CASTANHO_CLARO for a in df.ano]
barras = ax.bar(df.ano, df.livros, color=cores, width=0.55)
ax.bar_label(barras, padding=3, fontsize=9, color=TINTA)
titulo(ax, "Livros lidos por ano", f"{ano_ref} a verde · até {q('SELECT MAX(data_lida) d FROM leituras').d[0]}")
guardar(fig, "livros_por_ano.png")

# 2) ritmo acumulado
df = q(f"""SELECT strftime('%Y', data_lida) AS ano, CAST(strftime('%m', data_lida) AS INT) AS mes, COUNT(*) AS livros
           FROM leituras WHERE estante='read' AND strftime('%Y', data_lida) IN ('{ano_ref-1}','{ano_ref}')
           GROUP BY ano, mes""")
mes_ref = int(df[df.ano == str(ano_ref)].mes.max())
fig, ax = plt.subplots(figsize=(7.2, 4))
for ano, cor in ((str(ano_ref - 1), LARANJA), (str(ano_ref), VERDE)):
    s = df[df.ano == ano].set_index("mes")["livros"].reindex(range(1, 13), fill_value=0).cumsum()
    if ano == str(ano_ref):
        s = s.loc[:mes_ref]
        ax.fill_between(s.index, s.values, color=cor, alpha=0.09, linewidth=0)
    ax.plot(s.index, s.values, color=cor, linewidth=2, solid_capstyle="round")
    ax.plot(s.index[-1], s.values[-1], "o", color=cor, markersize=7, markeredgecolor=BEGE, markeredgewidth=2)
    ax.annotate(f"{ano} · {s.values[-1]}", (s.index[-1], s.values[-1]), xytext=(8, -3),
                textcoords="offset points", fontsize=9, fontweight="bold", color=TINTA)
ax.set_xticks(range(1, 13), ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"])
ax.set_xlim(0.7, 13.2)
titulo(ax, "Livros acumulados ao longo do ano", f"{ano_ref - 1} (laranja) vs {ano_ref} (verde)")
guardar(fig, "ritmo_ano_anterior_vs_atual.png")

# 3) notas
df = q("""SELECT CAST(nota AS INT) + CASE WHEN nota - CAST(nota AS INT) >= 0.25 THEN 0.5 ELSE 0 END AS estrelas,
                 COUNT(*) AS livros
          FROM leituras WHERE estante='read' AND nota IS NOT NULL GROUP BY estrelas ORDER BY estrelas""")
rot = ["★" * int(e) + ("½" if e % 1 else "") for e in df.estrelas]
fig, ax = plt.subplots(figsize=(7.2, 3.8))
b = ax.barh(rot, df.livros, color=LARANJA, height=0.55)
ax.bar_label(b, padding=4, fontsize=9, color=TINTA)
ax.grid(axis="x"); ax.grid(axis="y", visible=False)
ax.tick_params(axis="y", labelcolor=LARANJA, labelsize=11)
for t in ax.get_yticklabels():
    t.set_fontfamily("DejaVu Sans")   # tem o glifo ★
titulo(ax, "Como avalio o que leio", "Notas do Goodreads arredondadas à meia estrela")
guardar(fig, "distribuicao_notas.png")

# 4) autores
df = q("""SELECT a.nome AS autor, COUNT(*) AS livros
          FROM leituras l JOIN livros b USING (livro_id) JOIN autores a USING (autor_id)
          WHERE l.estante='read' GROUP BY a.autor_id HAVING COUNT(*) >= 2
          ORDER BY livros DESC, AVG(l.nota) DESC LIMIT 10""").iloc[::-1]
fig, ax = plt.subplots(figsize=(7.2, 4.4))
b = ax.barh(df.autor, df.livros, color=VERDE, height=0.55)
ax.bar_label(b, padding=4, fontsize=9, color=TINTA)
ax.grid(axis="x"); ax.grid(axis="y", visible=False)
ax.set_xticks(range(0, int(df.livros.max()) + 2))
titulo(ax, "Autores a que mais volto", "Livros lidos por autor (2 ou mais)")
guardar(fig, "autores_mais_lidos.png")

# 5) época de publicação
df = q("""SELECT CASE WHEN ano_original < 1800 THEN 'Antes de 1800'
                      WHEN ano_original < 1900 THEN 'Século XIX'
                      WHEN ano_original < 1950 THEN '1900–1949'
                      WHEN ano_original < 2000 THEN '1950–1999'
                      WHEN ano_original < 2015 THEN '2000–2014'
                      ELSE '2015 até hoje' END AS epoca, COUNT(*) AS livros, MIN(ano_original) AS o
          FROM leituras l JOIN livros b USING (livro_id)
          WHERE l.estante='read' AND b.ano_original IS NOT NULL GROUP BY epoca ORDER BY o DESC""")
fig, ax = plt.subplots(figsize=(7.2, 3.8))
b = ax.barh(df.epoca, df.livros, color=VERDE, height=0.55)
ax.bar_label(b, padding=4, fontsize=9, color=TINTA)
ax.grid(axis="x"); ax.grid(axis="y", visible=False)
titulo(ax, "De que época são os livros que leio", "Pelo ano da primeira publicação")
guardar(fig, "epoca_publicacao.png")

print("resultados.md e gráficos gerados.")
