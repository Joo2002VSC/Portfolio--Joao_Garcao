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
    return round(float(v)) if v not in ("", None) else None


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

    for r in ler_csv("desempenho_desportivo.csv"):
        con.execute(
            "INSERT INTO desempenho_desportivo VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (r["epoca"], int(r["posicao_liga"]), num(r["pontos"]), num(r["media_espectadores"]),
             r["competicao_europeia"] or None,
             r["fase_europeia"] or None, r["trofeu"] or None, r["nota"] or None),
        )

    def dinheiro(v):
        return round(float(v)) if v not in ("", None) else None

    for r in ler_csv("balanco_sad_rc.csv"):
        valores = [dinheiro(r[k]) for k in list(r)[1:-1]]
        con.execute("INSERT INTO balanco_sad_rc VALUES (?" + ", ?" * 13 + ")",
                    [r["epoca"], *valores, r["documento"]])

    for r in ler_csv("pessoal_sad.csv"):
        valores = [dinheiro(r[k]) for k in list(r)[1:-1]]
        con.execute("INSERT INTO pessoal_sad VALUES (?" + ", ?" * 16 + ")",
                    [r["epoca"], *valores, r["documento"]])

    for r in ler_csv("divergencias.csv"):
        con.execute(
            "INSERT INTO divergencia (fonte, epoca_id, indicador, valor_fonte, valor_rc, diferenca, nota) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (r["fonte"], r["epoca"], r["indicador"], float(r["valor_fonte"]), float(r["valor_rc"]),
             float(r["diferenca"]), r["nota"] or None),
        )

    def carregar(ficheiro, tabela, colunas, numericas):
        """Carrega um CSV para uma tabela; colunas numéricas arredondadas ao euro."""
        for r in ler_csv(ficheiro):
            valores = [dinheiro(r[c]) if c in numericas else (r[c] or None) for c in colunas]
            con.execute(f"INSERT INTO {tabela} ({', '.join(destino.get(c, c) for c in colunas)}) "
                        f"VALUES ({', '.join('?' * len(colunas))})", valores)

    destino = {"epoca": "epoca_id", "treinador": "nome"}
    carregar("balanco_rubricas.csv", "balanco_rubrica",
             ["epoca", "lado", "prazo", "rubrica", "valor"], {"valor"})
    carregar("passes_jogadores.csv", "passes_jogadores",
             ["epoca", "valor_liquido_inicio", "aquisicoes", "amortizacoes", "valor_bruto_alienado",
              "amort_acumuladas_alienadas", "rescisoes_bruto", "rescisoes_amort_acumuladas",
              "valor_liquido_fim", "documento"],
             {"valor_liquido_inicio", "aquisicoes", "amortizacoes", "valor_bruto_alienado",
              "amort_acumuladas_alienadas", "rescisoes_bruto", "rescisoes_amort_acumuladas",
              "valor_liquido_fim"})
    carregar("partes_relacionadas.csv", "partes_relacionadas",
             ["epoca", "rubrica", "sentido", "valor", "documento"], {"valor"})
    carregar("auditoria.csv", "auditoria",
             ["epoca", "parecer_auditor", "artigo_35_no_relatorio", "nota"], {"artigo_35_no_relatorio"})
    carregar("financiamento_detalhe.csv", "financiamento_detalhe",
             ["data_ref", "instrumento", "total", "menos_1_ano", "entre_1_3_anos", "documento"],
             {"total", "menos_1_ano", "entre_1_3_anos"})
    carregar("reexpressao.csv", "reexpressao",
             ["epoca", "indicador", "valor_original", "valor_reexpresso", "documento"],
             {"valor_original", "valor_reexpresso"})
    carregar("treinadores.csv", "treinador", ["periodo", "treinador", "tipo"], set())

    for r in ler_csv("taxas_referencia.csv"):
        con.execute("INSERT INTO taxa_referencia VALUES (?, ?, ?, ?)",
                    (r["data"], r["indicador"], float(r["taxa_pct"]), r["fonte"]))
    for r in ler_csv("bce_taxas.csv"):
        con.execute("INSERT INTO bce_taxa VALUES (?, ?, ?)",
                    (r["data_efeito"], float(r["facilidade_deposito"]), float(r["refinanciamento"])))

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
