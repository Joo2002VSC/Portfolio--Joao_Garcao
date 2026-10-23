"""
Corre todas as consultas de sql/02_consultas.sql e mostra os resultados em tabela.
Alternativa ao cliente `sqlite3` para quem não o tem instalado.

Uso:
    python scripts/executar_consultas.py
"""

import re
import sqlite3
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BD = RAIZ / "dados" / "diario.db"
CONSULTAS = RAIZ / "sql" / "02_consultas.sql"


def blocos(sql: str):
    """Divide o ficheiro em (título, consulta), ignorando comandos '.xxx' do cliente sqlite3."""
    sql = "\n".join(l for l in sql.splitlines() if not l.startswith("."))
    for parte in sql.split(";"):
        corpo = parte.strip()
        if not re.search(r"\b(SELECT|WITH)\b", corpo, re.I):
            continue
        titulos = re.findall(r"^--\s*([PE]\d+\..*|Média.*)$", corpo, re.M)
        titulo = titulos[-1] if titulos else "Consulta"
        yield titulo, corpo


def main() -> None:
    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 20)
    with sqlite3.connect(BD) as con:
        for titulo, consulta in blocos(CONSULTAS.read_text(encoding="utf-8")):
            print(f"\n=== {titulo} ===")
            print(pd.read_sql_query(consulta, con).to_string(index=False))


if __name__ == "__main__":
    main()
