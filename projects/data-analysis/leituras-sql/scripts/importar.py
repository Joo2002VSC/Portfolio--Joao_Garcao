"""Importa o CSV exportado do Goodreads para a base de dados SQLite dados/leituras.db.

Uso (a partir da pasta leituras-sql/):  python scripts/importar.py
"""
import csv
import sqlite3
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent   # leituras-sql/
CSV = PASTA / "dados" / "goodreads_library_export.csv"
DB = PASTA / "dados" / "leituras.db"
SCHEMA = PASTA / "sql" / "01_schema.sql"


def limpar_isbn(valor: str) -> str | None:
    # O Goodreads exporta ISBNs como ="9789727087983"
    valor = valor.replace("=", "").replace('"', "").strip()
    return valor or None


def inteiro(valor: str) -> int | None:
    # Campos vazios ou "0" (ex.: livros sem n.º de páginas) ficam NULL
    valor = valor.strip()
    return int(valor) or None if valor else None


def data(valor: str) -> str | None:
    # 2026/10/19 -> 2026-10-19 (formato ISO, que o SQLite entende)
    valor = valor.strip()
    return valor.replace("/", "-") if valor else None


def main() -> None:
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))

    with CSV.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    for l in linhas:
        con.execute(
            "INSERT OR IGNORE INTO autores (nome, nome_ordenado) VALUES (?, ?)",
            (l["Author"].strip(), l["Author l-f"].strip()),
        )
        autor_id = con.execute(
            "SELECT autor_id FROM autores WHERE nome = ?", (l["Author"].strip(),)
        ).fetchone()[0]

        con.execute(
            """INSERT INTO livros VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                int(l["Book Id"]), l["Title"].strip(), autor_id,
                l["Additional Authors"].strip() or None,
                limpar_isbn(l["ISBN13"]), l["Publisher"].strip() or None,
                l["Binding"].strip() or None, inteiro(l["Number of Pages"]),
                inteiro(l["Year Published"]), inteiro(l["Original Publication Year"]),
            ),
        )

        nota = float(l["My Rating"] or 0)
        con.execute(
            """INSERT INTO leituras VALUES (?,?,?,?,?,?,?)""",
            (
                int(l["Book Id"]), l["Exclusive Shelf"], nota or None,
                data(l["Date Read"]), data(l["Date Added"]),
                inteiro(l["Read Count"]) or 0,
                int("favorites" in l["Bookshelves"]),
            ),
        )

    con.commit()
    n = con.execute("SELECT COUNT(*) FROM livros").fetchone()[0]
    a = con.execute("SELECT COUNT(*) FROM autores").fetchone()[0]
    print(f"Importados {n} livros de {a} autores para {DB.name}")
    con.close()


if __name__ == "__main__":
    main()
