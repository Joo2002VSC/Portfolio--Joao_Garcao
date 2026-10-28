"""Corre todas as consultas de sql/02_consultas.sql, grava os resultados em
resultados.md e gera os gráficos da pasta graficos/.

Uso (a partir da pasta leituras-sql/):
    python scripts/importar.py && python scripts/gerar_resultados.py
"""
import re
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PASTA = Path(__file__).resolve().parent.parent   # leituras-sql/
con = sqlite3.connect(PASTA / "dados" / "leituras.db")

# ---------- 1. resultados.md ----------
sql = (PASTA / "sql" / "02_consultas.sql").read_text(encoding="utf-8")
blocos = re.split(r"^-- @ ", sql, flags=re.M)[1:]

saida = ["# Resultados das consultas\n",
         "_Gerado automaticamente por `gerar_resultados.py`._\n"]
for bloco in blocos:
    titulo, consulta = bloco.split("\n", 1)
    df = pd.read_sql_query(consulta, con)
    saida.append(f"\n## {titulo.strip()}\n")
    saida.append(df.fillna("").to_markdown(index=False))
    saida.append("\n")
(PASTA / "resultados.md").write_text("\n".join(saida), encoding="utf-8")

# ---------- 2. gráficos ----------
GRAF = PASTA / "graficos"
GRAF.mkdir(exist_ok=True)
COR = "#7a4b2a"
plt.rcParams.update({"figure.dpi": 150, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 10})

def guardar(nome):
    plt.tight_layout()
    plt.savefig(GRAF / nome)
    plt.close()

# Livros por ano
df = pd.read_sql_query("""
    SELECT strftime('%Y', data_lida) AS ano, COUNT(*) AS livros
    FROM leituras WHERE estante='read' AND data_lida IS NOT NULL
    GROUP BY ano ORDER BY ano""", con)
ax = df.plot.bar(x="ano", y="livros", color=COR, legend=False, figsize=(7, 4), rot=0)
ax.bar_label(ax.containers[0])
ax.set(title="Livros lidos por ano", xlabel="", ylabel="livros")
guardar("livros_por_ano.png")

# Ritmo acumulado 2025 vs 2026
df = pd.read_sql_query("""
    SELECT strftime('%Y', data_lida) AS ano, CAST(strftime('%m', data_lida) AS INT) AS mes,
           COUNT(*) AS livros
    FROM leituras WHERE estante='read' AND strftime('%Y', data_lida) IN ('2025','2026')
    GROUP BY ano, mes""", con)
fig, ax = plt.subplots(figsize=(7, 4))
for ano, cor in (("2025", "#b9a48f"), ("2026", COR)):
    s = df[df.ano == ano].set_index("mes")["livros"].reindex(range(1, 13), fill_value=0).cumsum()
    if ano == "2026":
        s = s.loc[: int(df[df.ano == ano].mes.max())]
    ax.plot(s.index, s.values, marker="o", color=cor, label=ano)
ax.set_xticks(range(1, 13), ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"])
ax.set(title="Livros lidos — acumulado ao longo do ano", ylabel="livros")
ax.legend(frameon=False)
guardar("ritmo_2025_vs_2026.png")

# Distribuição das notas
df = pd.read_sql_query("""
    SELECT nota, COUNT(*) AS livros FROM leituras
    WHERE estante='read' AND nota IS NOT NULL GROUP BY nota ORDER BY nota""", con)
ax = df.plot.bar(x="nota", y="livros", color=COR, legend=False, figsize=(7, 4), rot=0)
ax.bar_label(ax.containers[0])
ax.set(title="Distribuição das minhas notas", xlabel="nota (estrelas)", ylabel="livros")
guardar("distribuicao_notas.png")

# Época de publicação
df = pd.read_sql_query("""
    SELECT (b.ano_original / 50) * 50 AS periodo, COUNT(*) AS livros
    FROM leituras l JOIN livros b USING (livro_id)
    WHERE l.estante='read' AND b.ano_original >= 1800
    GROUP BY periodo ORDER BY periodo""", con)
df["periodo"] = df.periodo.astype(str) + "–" + (df.periodo + 49).astype(str)
ax = df.plot.barh(x="periodo", y="livros", color=COR, legend=False, figsize=(7, 4))
ax.bar_label(ax.containers[0])
ax.set(title="Livros lidos por época de 1.ª publicação", xlabel="livros", ylabel="")
guardar("epoca_publicacao.png")

print("resultados.md e gráficos gerados.")
