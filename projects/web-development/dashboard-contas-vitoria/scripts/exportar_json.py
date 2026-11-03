"""Exporta os dados do projeto contas-vitoria-sql para o dashboard.

O painel apresenta apenas as contas da Vitória SC – Futebol, SAD. Gera dois ficheiros em data/:
  - contas.json     indicadores da SAD por época (vistas v_kpis e v_dr), dados desportivos e fontes
  - consultas.json  as consultas de sql/04_analises.sql relativas à SAD e as consultas complementares
                    do painel (sql/indicadores_dashboard.sql): título, secção, conceitos SQL, código e resultado

O dashboard não refaz cálculos que já existem no projeto SQL: lê os resultados das próprias consultas.
Antes de gravar, o script faz verificações de coerência e pára se alguma falhar.

Uso (na pasta do dashboard):
    python scripts/exportar_json.py
    python scripts/exportar_json.py --projeto caminho/para/contas-vitoria-sql
"""

import argparse
import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROJETO_PADRAO = RAIZ.parent.parent / "data-analysis" / "contas-vitoria-sql"
SAIDA = RAIZ / "data"

BASE = {
    "epocas": "SELECT epoca_id AS id FROM epoca ORDER BY ano_inicio",
    "kpis": """
        SELECT entidade_id AS entidade, epoca_id AS epoca,
               vendas_servicos, gastos_pessoal, resultado_liquido,
               mais_valias_liquidas, rl_sem_mais_valias, pct_pessoal_receitas,
               juros, ativo_total, passivo_total, capital_proprio, caixa
        FROM v_kpis WHERE entidade_id = 'SAD' ORDER BY epoca_id""",
    "desporto": """
        SELECT epoca_id AS epoca, posicao_liga, pontos, media_espectadores,
               competicao_europeia, fase_europeia, trofeu
        FROM desempenho_desportivo ORDER BY epoca_id""",
    "dr": """
        SELECT entidade_id AS entidade, epoca_id AS epoca, vendas_servicos, rendimentos_operacionais,
               -gastos_pessoal AS gastos_pessoal, -fse AS fse, resultado_operacional, resultado_liquido
        FROM v_dr WHERE entidade_id = 'SAD' ORDER BY epoca_id""",
    "fontes": "SELECT epoca_id AS epoca, estado, documentos FROM fonte WHERE entidade_id = 'SAD' ORDER BY epoca_id",
}

# Consultas do projeto que não entram no painel, por não tratarem só das contas da SAD:
# comparam entidades (10, 11, 16, 17, 19) ou usam tabelas com dados consolidados
# (receitas_composicao: 5, 6, 18, 47; gastos_pessoal_composicao: 13, 24).
EXCLUIDAS = {5, 6, 10, 11, 13, 16, 17, 18, 19, 24, 47}

SEPARADOR = re.compile(r"^-- =+\s*$")
SQL_DASHBOARD = RAIZ / "sql" / "indicadores_dashboard.sql"
DESLOCAMENTO = 100  # as consultas complementares D1, D2… ficam com os números 101, 102…


def ler_consultas(ficheiro: Path) -> list[dict]:
    """Divide 04_analises.sql em consultas ("-- @q N. Título") e guarda a secção de cada uma."""
    linhas = ficheiro.read_text(encoding="utf-8").splitlines()
    consultas, seccao, atual = [], "Resultados, receitas e estrutura", None
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        # Cabeçalho de secção: três linhas "-- ====" / "-- TÍTULO" / "-- ===="
        if SEPARADOR.match(linha) and i + 2 < len(linhas) and SEPARADOR.match(linhas[i + 2]) \
                and "04_analises" not in linhas[i + 1]:
            seccao = linhas[i + 1].lstrip("- ").strip().capitalize().replace("r&c", "R&C")
            i += 3
            continue
        if linha.startswith("-- @q "):
            m = re.match(r"-- @q (\d+)\.\s*(.+)", linha)
            atual = {"n": int(m.group(1)), "titulo": m.group(2).strip(), "seccao": seccao, "linhas_sql": []}
            consultas.append(atual)
        elif atual is not None:
            atual["linhas_sql"].append(linha)
        i += 1

    for c in consultas:
        corpo = "\n".join(c.pop("linhas_sql")).strip()
        conceitos = re.search(r"^-- Conceitos?:\s*(.+)$", corpo, flags=re.M)
        c["conceitos"] = conceitos.group(1).strip() if conceitos else ""
        c["sql"] = corpo
    return consultas


def ler_complementares(ficheiro: Path) -> list[dict]:
    """Consultas do próprio dashboard ("-- @d D1. Título"), separadas das 59 do projeto."""
    texto = ficheiro.read_text(encoding="utf-8")
    consultas = []
    for bloco in re.split(r"^-- @d ", texto, flags=re.M)[1:]:
        cabeca, _, corpo = bloco.partition("\n")
        m = re.match(r"D(\d+)\.\s*(.+)", cabeca.strip())
        conceitos = re.search(r"^-- Conceitos?:\s*(.+)$", corpo, flags=re.M)
        consultas.append({
            "n": DESLOCAMENTO + int(m.group(1)), "codigo": f"D{m.group(1)}", "titulo": m.group(2).strip(),
            "seccao": "Consultas complementares do painel", "conceitos": conceitos.group(1).strip() if conceitos else "",
            "sql": corpo.strip(),
        })
    return consultas


def executar(con: sqlite3.Connection, consultas: list[dict]) -> None:
    for c in consultas:
        cur = con.execute(c["sql"])
        c["colunas"] = [d[0] for d in cur.description]
        c["linhas"] = [list(r) for r in cur.fetchall()]


def verificar(base: dict, consultas: list[dict]) -> list[str]:
    """Verificações de coerência entre a vista v_kpis e as consultas que o dashboard usa."""
    erros = []
    por_n = {c["n"]: c for c in consultas}
    numeros = sorted(n for n in por_n if n < DESLOCAMENTO)
    if numeros != list(range(1, len(numeros) + 1)):
        erros.append(f"Numeração das consultas com falhas: {numeros}")

    sad = {k["epoca"]: k for k in base["kpis"]}
    q1 = por_n[1]
    for epoca, rl, *_ in q1["linhas"]:
        if sad.get(epoca, {}).get("resultado_liquido") != rl:
            erros.append(f"Consulta 1 e v_kpis divergem no resultado da SAD em {epoca}")

    q7 = por_n[7]
    i = {c: q7["colunas"].index(c) for c in ("epoca", "ativo_total", "passivo_total", "capital_proprio")}
    for linha in q7["linhas"]:
        at, ps, cp = linha[i["ativo_total"]], linha[i["passivo_total"]], linha[i["capital_proprio"]]
        if None not in (at, ps, cp) and abs((at - ps) - cp) > 2:
            erros.append(f"Balanço não fecha em {linha[i['epoca']]}: ativo − passivo ≠ capital próprio")

    # Os rácios de D1 têm de bater com a consulta 29 do projeto (SAD)
    q29 = {l[0]: l for l in por_n[29]["linhas"]}
    d1 = por_n[DESLOCAMENTO + 1]
    j = {c: d1["colunas"].index(c) for c in ("epoca", "endividamento", "autonomia_pct")}
    for l in d1["linhas"]:
        if l[j["epoca"]] in q29:
            r = q29[l[j["epoca"]]]
            if abs(r[1] - l[j["endividamento"]]) > 0.011 or abs(r[2] - l[j["autonomia_pct"]]) > 0.11:
                erros.append(f"D1 e consulta 29 divergem em {l[j['epoca']]}")

    # D6 tem de reproduzir o resultado líquido de v_kpis e o resultado operacional de D2
    d6, d2 = por_n.get(106), por_n.get(102)
    if d6 and d2:
        rl = {k["epoca"]: k["resultado_liquido"] for k in base["kpis"]}
        ro = {l[0]: l[1] for l in d2["linhas"]}
        j = {c: d6["colunas"].index(c) for c in ("epoca", "resultado_operacional", "resultado_liquido")}
        for l in d6["linhas"]:
            e = l[j["epoca"]]
            if rl.get(e) != l[j["resultado_liquido"]] or ro.get(e) != l[j["resultado_operacional"]]:
                erros.append(f"D6 diverge de v_kpis ou de D2 em {e}")
    for c in consultas:
        if not c["linhas"]:
            erros.append(f"Consulta {c['n']} não devolveu linhas")
    return erros


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--projeto", type=Path, default=PROJETO_PADRAO, help="pasta do projeto contas-vitoria-sql")
    args = p.parse_args()
    db, sql = args.projeto / "vsc_contas.db", args.projeto / "sql" / "04_analises.sql"
    for f in (db, sql):
        if not f.exists():
            sys.exit(f"Não encontrado: {f}")

    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    base = {chave: [dict(l) for l in con.execute(q)] for chave, q in BASE.items()}
    base["epocas"] = [e["id"] for e in base["epocas"]]
    con.row_factory = None
    consultas = ler_consultas(sql)
    for c in consultas:
        c["codigo"] = str(c["n"])
    if SQL_DASHBOARD.exists():
        consultas += ler_complementares(SQL_DASHBOARD)
    executar(con, consultas)
    con.close()

    erros = verificar(base, consultas)
    if erros:
        sys.exit("Verificação falhou:\n  " + "\n  ".join(erros))
    n_total = sum(c["n"] < DESLOCAMENTO for c in consultas)
    # Consultas sobre o Clube ou o Grupo consolidado: ficam no projeto SQL, fora do âmbito do painel
    consultas = [c for c in consultas if c["n"] not in EXCLUIDAS]

    gerado = date.today().isoformat()
    SAIDA.mkdir(exist_ok=True)
    (SAIDA / "contas.json").write_text(
        json.dumps({"gerado": gerado, "unidade": "EUR", **base}, ensure_ascii=False, indent=1), encoding="utf-8")
    (SAIDA / "consultas.json").write_text(
        json.dumps({"gerado": gerado, "fonte": "sql/04_analises.sql", "total_projeto": n_total,
                    "excluidas": sorted(EXCLUIDAS), "consultas": consultas}, ensure_ascii=False),
        encoding="utf-8")
    seccoes = sorted({c["seccao"] for c in consultas})
    print(f"data/contas.json: {len(base['kpis'])} linhas de indicadores, {len(base['epocas'])} épocas")
    n_proj = sum(c["n"] < DESLOCAMENTO for c in consultas)
    print(f"data/consultas.json: {n_proj} consultas do projeto relativas à SAD + {len(consultas) - n_proj} complementares, "
          f"{len(seccoes)} secções; verificações OK")


if __name__ == "__main__":
    main()
