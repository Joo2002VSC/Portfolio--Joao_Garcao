"""Exporta os dados do projeto contas-vitoria-sql para data/contas.json.

O dashboard não lê a base de dados diretamente: lê este JSON, gerado a partir
das vistas SQL do projeto de análise (v_kpis) e de duas tabelas de apoio.

Uso (na pasta do dashboard):
    python scripts/exportar_json.py
    python scripts/exportar_json.py --db caminho/para/vsc_contas.db
"""

import argparse
import json
import sqlite3
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DB_PADRAO = RAIZ.parent.parent / "data-analysis" / "contas-vitoria-sql" / "vsc_contas.db"
SAIDA = RAIZ / "data" / "contas.json"

CONSULTAS = {
    "entidades": "SELECT entidade_id AS id, nome, descricao FROM entidade",
    "epocas": "SELECT epoca_id AS id FROM epoca ORDER BY ano_inicio",
    # Indicadores por entidade e época, a partir da vista principal do projeto SQL
    "kpis": """
        SELECT entidade_id AS entidade, epoca_id AS epoca,
               vendas_servicos, gastos_pessoal, resultado_liquido,
               mais_valias_liquidas, rl_sem_mais_valias, pct_pessoal_receitas,
               juros, ativo_total, passivo_total, capital_proprio, caixa
        FROM v_kpis ORDER BY entidade_id, epoca_id""",
    "desporto": """
        SELECT epoca_id AS epoca, posicao_liga, pontos, media_espectadores,
               competicao_europeia, fase_europeia, trofeu
        FROM desempenho_desportivo ORDER BY epoca_id""",
    # Composição das receitas do grupo (só existe para o Consolidado)
    "receitas": """
        SELECT entidade_id AS entidade, epoca_id AS epoca, categoria, valor
        FROM receitas_composicao ORDER BY epoca_id, valor DESC""",
}


def exportar(db: Path) -> dict:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    dados = {"gerado": date.today().isoformat(), "unidade": "EUR"}
    for chave, sql in CONSULTAS.items():
        dados[chave] = [dict(linha) for linha in con.execute(sql)]
    con.close()
    dados["epocas"] = [e["id"] for e in dados["epocas"]]
    return dados


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DB_PADRAO)
    args = p.parse_args()
    if not args.db.exists():
        raise SystemExit(f"Base de dados não encontrada: {args.db}")
    dados = exportar(args.db)
    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{SAIDA.relative_to(RAIZ)}: {len(dados['kpis'])} linhas de indicadores, "
          f"{len(dados['epocas'])} épocas")


if __name__ == "__main__":
    main()
