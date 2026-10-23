"""Corre todas as consultas de sql/04_analises.sql e grava resultados.md.

Uso (a partir da raiz do projeto, depois de build_db.py):
    python scripts/correr_analises.py
"""
import re
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DB = RAIZ / "vsc_contas.db"
SQL = RAIZ / "sql" / "04_analises.sql"
SAIDA = RAIZ / "resultados.md"


def formatar(v):
    if v is None:
        return "—"
    if isinstance(v, int):
        return f"{v:,}".replace(",", " ")
    if isinstance(v, float):
        casas = 2 if abs(v) < 10 else 1
        return f"{v:.{casas}f}".replace(".", ",")
    return str(v)


def main():
    texto = SQL.read_text(encoding="utf-8")
    blocos = re.split(r"^-- @q ", texto, flags=re.M)[1:]
    con = sqlite3.connect(DB)
    linhas = ["# Resultados das análises", "",
              "Gerado automaticamente por `scripts/correr_analises.py`. Valores em euros.", ""]
    for bloco in blocos:
        titulo, _, corpo = bloco.partition("\n")
        cur = con.execute(corpo)
        cols = [d[0] for d in cur.description]
        dados = cur.fetchall()
        linhas += [f"## {titulo.strip()}", "",
                   "| " + " | ".join(cols) + " |",
                   "|" + "---|" * len(cols)]
        linhas += ["| " + " | ".join(formatar(v) for v in r) + " |" for r in dados]
        linhas.append("")
        print(f"OK  {titulo.strip()}  ({len(dados)} linhas)")
    SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\nResultados gravados em {SAIDA.name}")


if __name__ == "__main__":
    main()
