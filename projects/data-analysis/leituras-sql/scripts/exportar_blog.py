"""Corre as consultas de sql/03_blog.sql e escreve, na pasta assets/dados/ do blog:

  * estatisticas.js  ->  window.ESTATISTICAS  (página "Em Números" e contador da página inicial)
  * leituras.js      ->  window.LEITURAS      (página "Todas as Leituras")

Os títulos e autores mostrados no blog vêm de dados/titulos_blog.csv quando existem
(versões em português, sem "(Portuguese Edition)", etc.); os restantes são limpos
automaticamente a partir do Goodreads.

Uso:  python scripts/importar.py && python scripts/exportar_blog.py
"""
import csv
import json
import re
import sqlite3

from caminhos import CONSULTAS, CORRECOES, DB, SAIDA_BLOG

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MINUSCULAS = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "um", "uma",
              "the", "of", "and", "in", "to", "for"}


def limpar_titulo(t: str) -> str:
    t = re.sub(r"\s*\([^)]*\)", "", t)          # "(Portuguese Edition)", "(Persepolis, #1)"
    t = re.split(r"\s*--|:\s", t)[0]            # subtítulos e "-- (coleção)"
    t = t.strip(" .")
    if t.isupper():                               # "UMA HISTÓRIA DE XADREZ"
        palavras = t.lower().split()
        t = " ".join(p if i and p in MINUSCULAS else p.capitalize() for i, p in enumerate(palavras))
    return t


def estrelas(nota) -> str:
    if not nota:
        return ""
    inteiras = int(nota)
    return "★" * inteiras + ("½" if nota - inteiras >= 0.25 else "")


def blocos_sql(caminho):
    texto = caminho.read_text(encoding="utf-8")
    for bloco in re.split(r"^-- @ ", texto, flags=re.M)[1:]:
        chave, consulta = bloco.split("\n", 1)
        yield chave.strip(), consulta


def main() -> None:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    r = {chave: [dict(l) for l in con.execute(sql)]
         for chave, sql in blocos_sql(CONSULTAS.with_name("03_blog.sql"))}

    # títulos e autores "do blog"
    correcoes = {}
    if CORRECOES.exists():
        with CORRECOES.open(encoding="utf-8") as f:
            correcoes = {int(l["book_id"]): l for l in csv.DictReader(f)}

    livros = {}
    for l in r["lista"]:
        c = correcoes.get(l["id"], {})
        livros[l["id"]] = {
            "title": c.get("titulo") or limpar_titulo(l["titulo"]),
            "author": c.get("autor") or re.sub(r"\s+", " ", l["autor"]),
            "year_pub": str(c.get("ano_original") or l["ano_original"] or l["ano_edicao"] or ""),
            "year_read": str(l["ano_lido"] or "—"),
            "stars": estrelas(l["nota"]),
            "pages": str(l["paginas"] or ""),
        }
    # livros que não estão na estante "read" (a ler agora)
    def info(i):
        if i in livros:
            return {"title": livros[i]["title"], "author": livros[i]["author"]}
        t, a = con.execute("SELECT b.titulo, a.nome FROM livros b JOIN autores a USING (autor_id) "
                           "WHERE livro_id = ?", (i,)).fetchone()
        c = correcoes.get(i, {})
        return {"title": c.get("titulo") or limpar_titulo(t), "author": c.get("autor") or a}

    ref = r["referencia"][0]
    ano, ano_ant = ref["ano"], ref["ano"] - 1

    meses = {a: [{"mes": MESES[m], "livros": 0, "titulos": []} for m in range(12)] for a in (ano_ant, ano)}
    for linha in r["por_mes"]:
        alvo = meses[linha["ano"]][linha["mes"] - 1]
        alvo["livros"] = linha["livros"]
        alvo["titulos"] = [livros[int(i)]["title"] for i in linha["ids"].split(",")]

    def acumular(lista, ate=12):
        total, out = 0, []
        for m in lista[:ate]:
            total += m["livros"]
            out.append(total)
        return out

    estat = {
        "gerado_em": ref["data"],
        "ano": ano,
        "mes": ref["mes"],
        "resumo": r["resumo"][0],
        "por_ano": r["por_ano"],
        "meses": meses[ano],
        "acumulado": {"anterior": acumular(meses[ano_ant]),
                      "atual": acumular(meses[ano], ref["mes"])},
        "notas": r["notas"],
        "autores": r["autores"],
        "epocas": r["epocas"],
        "extensao": r["extensao"],
        "favoritos": [{**info(f["id"]), "nota": f["nota"], "favorito": bool(f["favorito"])}
                      for f in r["favoritos"]],
        "a_ler": [info(x["id"]) for x in r["a_ler"]],
        "pilha": r["pilha"][0],
        "espera": r["espera"][0],
        "extremos": [{**info(e["id"]), "tipo": e["tipo"], "paginas": e["paginas"]} for e in r["extremos"]],
    }

    SAIDA_BLOG.mkdir(parents=True, exist_ok=True)
    cabecalho = "/* Gerado automaticamente por analise-sql/scripts/exportar_blog.py — não editar à mão. */\n"
    (SAIDA_BLOG / "estatisticas.js").write_text(
        cabecalho + "window.ESTATISTICAS = " + json.dumps(estat, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8")
    (SAIDA_BLOG / "leituras.js").write_text(
        cabecalho + "window.LEITURAS = [\n" +
        ",\n".join(json.dumps(v, ensure_ascii=False) for v in livros.values()) + "\n];\n",
        encoding="utf-8")
    print(f"estatisticas.js e leituras.js ({len(livros)} livros) gerados em {SAIDA_BLOG}")


if __name__ == "__main__":
    main()
