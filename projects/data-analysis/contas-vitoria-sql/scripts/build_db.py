"""Constrói a base de dados vsc_contas.db a partir dos ficheiros SQL e CSV.

Uso (a partir da raiz do projeto):
    python scripts/build_db.py

Só usa a biblioteca padrão do Python (sqlite3 + csv).
"""
import csv
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "data"
SQL = RAIZ / "sql"
DB = RAIZ / "vsc_contas.db"


def ler_csv(nome):
    with open(DADOS / nome, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    """Converte para inteiro; célula vazia = valor não disponível (NULL)."""
    return int(v) if v not in ("", None) else None


def carregar_dr(con, ficheiro, entidade):
    """Demonstração de resultados: CSV largo -> tabela longa."""
    for linha in ler_csv(ficheiro):
        epoca = linha.pop("epoca")
        for rubrica, valor in linha.items():
            if valor != "":
                con.execute(
                    "INSERT INTO demonstracao_resultados VALUES (?, ?, ?, ?)",
                    (entidade, epoca, rubrica, int(valor)),
                )


def carregar_largo_categorias(con, ficheiro, tabela, entidade):
    """Composições (receitas, pessoal): uma coluna por categoria -> linhas."""
    for linha in ler_csv(ficheiro):
        epoca = linha.pop("epoca")
        for categoria, valor in linha.items():
            con.execute(
                f"INSERT INTO {tabela} VALUES (?, ?, ?, ?)",
                (entidade, epoca, categoria, int(valor)),
            )


def main():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")

    con.executescript((SQL / "01_schema.sql").read_text(encoding="utf-8"))
    con.executescript((SQL / "02_dimensoes.sql").read_text(encoding="utf-8"))

    carregar_dr(con, "dr_sad.csv", "SAD")
    carregar_dr(con, "dr_clube.csv", "CLUBE")
    carregar_dr(con, "dr_consolidado.csv", "CONSOLIDADO")

    for r in ler_csv("balanco.csv"):
        con.execute(
            "INSERT INTO balanco VALUES (?, ?, ?, ?, ?, ?)",
            (r["entidade"], r["epoca"], num(r["ativo_total"]), num(r["passivo_total"]),
             num(r["capital_proprio"]), num(r["caixa"])),
        )

    for r in ler_csv("cash_flow.csv"):
        con.execute(
            "INSERT INTO cash_flow VALUES (?, ?, ?, ?, ?)",
            (r["entidade"], r["epoca"], num(r["operacional"]),
             num(r["investimento"]), num(r["financiamento"])),
        )

    carregar_largo_categorias(con, "receitas_composicao.csv", "receitas_composicao", "CONSOLIDADO")
    carregar_largo_categorias(con, "gastos_pessoal_composicao.csv",
                              "gastos_pessoal_composicao", "CONSOLIDADO")

    for r in ler_csv("transferencias.csv"):
        con.execute(
            "INSERT INTO transferencias VALUES (?, ?, ?, ?, ?)",
            (r["entidade"], r["epoca"], num(r["vendas_brutas"]),
             num(r["custo_vendas"]), num(r["mais_valias_liquidas"])),
        )

    for r in ler_csv("operacao_jogador.csv"):
        con.execute(
            "INSERT INTO operacao_jogador (epoca_id, jogador, tipo, clube) VALUES (?, ?, ?, ?)",
            (r["epoca"], r["jogador"], r["tipo"], r["clube"] or None),
        )

    for r in ler_csv("divida.csv"):
        con.execute(
            "INSERT INTO divida VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (r["data_ref"], r["credor"], r["tipo"], int(r["total"]), num(r["menos_1_ano"]),
             num(r["entre_1_3_anos"]), num(r["mais_3_anos"]), r["nota"] or None),
        )

    for r in ler_csv("fonte.csv"):
        con.execute("INSERT INTO fonte VALUES (?, ?, ?, ?)",
                    (r["entidade"], r["epoca"], r["estado"], r["documentos"]))

    for r in ler_csv("evento.csv"):
        con.execute(
            "INSERT INTO evento (entidade_id, epoca_id, tipo, descricao, valor) VALUES (?, ?, ?, ?, ?)",
            (r["entidade"], r["epoca"], r["tipo"], r["descricao"], num(r["valor"])),
        )

    con.executescript((SQL / "03_vistas.sql").read_text(encoding="utf-8"))
    con.commit()

    print(f"Base de dados criada: {DB.name}")
    for (t,) in con.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') "
        "AND name NOT LIKE 'sqlite_%' ORDER BY type, name"
    ):
        n = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"  {t:<30} {n:>4} linhas")
    con.close()


if __name__ == "__main__":
    main()
