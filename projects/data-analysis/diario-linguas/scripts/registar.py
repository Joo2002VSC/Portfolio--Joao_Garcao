"""
Regista os teus próprios dados no Diário de Aprendizagem de Línguas.

Exemplos:
    python scripts/registar.py iniciar                      # cria uma BD vazia (nl, fr, it)
    python scripts/registar.py sessao nl 30 vocabulário --recurso Duolingo
    python scripts/registar.py palavra nl "de fiets" "a bicicleta" --classe nome --tema "dia a dia"
    python scripts/registar.py revisao nl "de fiets" certo
    python scripts/registar.py revisao fr "éventuellement" errado
    python scripts/registar.py resumo

A data é hoje por omissão; usa --data AAAA-MM-DD para registar outro dia.
"""

import argparse
import sqlite3
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BD = RAIZ / "dados" / "diario.db"
ESQUEMA = RAIZ / "sql" / "01_schema.sql"

IDIOMAS_INICIAIS = [
    ("nl", "Neerlandês", "A2", "Chegar a B1"),
    ("fr", "Francês", "B2", "Manter o nível"),
    ("it", "Italiano", "A2", "Consolidar o A2"),
]
TIPOS = ["vocabulário", "gramática", "conversa", "leitura", "áudio/vídeo"]
CLASSES = ["nome", "verbo", "adjetivo", "advérbio", "expressão", "outro"]


def ligar() -> sqlite3.Connection:
    if not BD.exists():
        sys.exit("Ainda não há base de dados. Corre primeiro:  python scripts/registar.py iniciar")
    con = sqlite3.connect(BD)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def id_idioma(con, codigo: str) -> int:
    linha = con.execute("SELECT id FROM idiomas WHERE codigo = ?", (codigo,)).fetchone()
    if not linha:
        sys.exit(f"Língua desconhecida: {codigo}")
    return linha[0]


def iniciar(a):
    if BD.exists() and not a.forcar:
        sys.exit(f"{BD.relative_to(RAIZ)} já existe. Usa --forcar para a apagar e começar do zero.")
    BD.parent.mkdir(parents=True, exist_ok=True)
    if BD.exists():
        BD.unlink()
    con = sqlite3.connect(BD)
    con.executescript(ESQUEMA.read_text(encoding="utf-8"))
    con.executemany("INSERT INTO idiomas (codigo, nome, nivel_atual, objetivo) VALUES (?,?,?,?)",
                    IDIOMAS_INICIAIS)
    con.commit()
    print("Base de dados vazia criada. Boa aprendizagem!")


def sessao(a):
    con = ligar()
    con.execute("INSERT INTO sessoes (idioma_id, data, duracao_min, tipo, recurso, notas) VALUES (?,?,?,?,?,?)",
                (id_idioma(con, a.idioma), a.data, a.minutos, a.tipo, a.recurso, a.notas))
    con.commit()
    print(f"Sessão registada: {a.idioma} · {a.minutos} min · {a.tipo}")


def palavra(a):
    con = ligar()
    try:
        con.execute("INSERT INTO palavras (idioma_id, termo, traducao_pt, classe, tema, data_adicionada) "
                    "VALUES (?,?,?,?,?,?)",
                    (id_idioma(con, a.idioma), a.termo, a.traducao, a.classe, a.tema, a.data))
    except sqlite3.IntegrityError:
        sys.exit(f"'{a.termo}' já está registada em {a.idioma}.")
    con.commit()
    print(f"Palavra registada: {a.termo} → {a.traducao}")


def revisao(a):
    con = ligar()
    linha = con.execute("SELECT id FROM palavras WHERE idioma_id = ? AND termo = ?",
                        (id_idioma(con, a.idioma), a.termo)).fetchone()
    if not linha:
        sys.exit(f"'{a.termo}' não existe em {a.idioma}. Regista-a primeiro com o comando 'palavra'.")
    sess = con.execute("SELECT id FROM sessoes WHERE idioma_id = ? AND data = ? ORDER BY id DESC LIMIT 1",
                       (id_idioma(con, a.idioma), a.data)).fetchone()
    con.execute("INSERT INTO revisoes (palavra_id, sessao_id, data, acertou) VALUES (?,?,?,?)",
                (linha[0], sess[0] if sess else None, a.data, 1 if a.resultado == "certo" else 0))
    con.commit()
    print(f"Revisão registada: {a.termo} — {a.resultado}")


def resumo(_a):
    con = ligar()
    for nome, palavras, sessoes, minutos, ultima in con.execute("""
        SELECT i.nome,
               (SELECT COUNT(*) FROM palavras p WHERE p.idioma_id = i.id),
               COUNT(s.id), COALESCE(SUM(s.duracao_min), 0), MAX(s.data)
        FROM idiomas i LEFT JOIN sessoes s ON s.idioma_id = i.id
        GROUP BY i.id"""):
        print(f"{nome:<11} {palavras:>4} palavras · {sessoes:>3} sessões · {minutos:>5} min · última: {ultima or '—'}")


def main():
    hoje = date.today().isoformat()
    p = argparse.ArgumentParser(description="Diário de Aprendizagem de Línguas")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("iniciar", help="criar uma base de dados vazia")
    s.add_argument("--forcar", action="store_true", help="apagar a BD existente")
    s.set_defaults(f=iniciar)

    s = sub.add_parser("sessao", help="registar uma sessão de estudo")
    s.add_argument("idioma"); s.add_argument("minutos", type=int); s.add_argument("tipo", choices=TIPOS)
    s.add_argument("--recurso"); s.add_argument("--notas"); s.add_argument("--data", default=hoje)
    s.set_defaults(f=sessao)

    s = sub.add_parser("palavra", help="registar uma palavra nova")
    s.add_argument("idioma"); s.add_argument("termo"); s.add_argument("traducao")
    s.add_argument("--classe", choices=CLASSES); s.add_argument("--tema"); s.add_argument("--data", default=hoje)
    s.set_defaults(f=palavra)

    s = sub.add_parser("revisao", help="registar se acertaste ou erraste uma palavra")
    s.add_argument("idioma"); s.add_argument("termo"); s.add_argument("resultado", choices=["certo", "errado"])
    s.add_argument("--data", default=hoje)
    s.set_defaults(f=revisao)

    s = sub.add_parser("resumo", help="ver um resumo rápido")
    s.set_defaults(f=resumo)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
