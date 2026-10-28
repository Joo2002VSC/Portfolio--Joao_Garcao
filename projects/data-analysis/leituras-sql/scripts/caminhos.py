"""Caminhos partilhados pelos scripts.

A análise funciona em dois sítios:
  * dentro do blog            ->  Blog/analise-sql/
  * no Portfolio              ->  projects/data-analysis/leituras-sql/
                                  (com o blog em projects/web-development/blog-literario/)
Em ambos os casos o CSV do Goodreads vive em  <blog>/assets/goodreads_library_export.csv
"""
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent          # analise-sql/ ou leituras-sql/


def _encontrar_blog() -> Path:
    candidatos = [
        PASTA.parent,                                            # Blog/analise-sql
        PASTA.parent.parent / "web-development" / "blog-literario",  # Portfolio
    ]
    for c in candidatos:
        if (c / "index.html").exists() and (c / "assets").is_dir():
            return c
    raise FileNotFoundError("Não encontrei a pasta do blog (com index.html e assets/).")


BLOG = _encontrar_blog()
CSV = BLOG / "assets" / "goodreads_library_export.csv"
DB = PASTA / "dados" / "leituras.db"
SCHEMA = PASTA / "sql" / "01_schema.sql"
CONSULTAS = PASTA / "sql" / "02_consultas.sql"
CORRECOES = PASTA / "dados" / "titulos_blog.csv"     # títulos/autores como aparecem no blog
SAIDA_BLOG = BLOG / "assets" / "dados"                # estatisticas.js e leituras.js
GRAFICOS = PASTA / "graficos"
