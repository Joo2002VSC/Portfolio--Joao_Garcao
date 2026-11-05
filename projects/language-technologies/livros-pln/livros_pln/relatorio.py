"""Relatórios em Markdown, legíveis diretamente no GitHub."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def _num(v, casas=2) -> str:
    if v is None or (isinstance(v, float) and v != v):
        return "—"
    if isinstance(v, int) or (isinstance(v, float) and v.is_integer() and abs(v) >= 1000):
        return f"{int(v):,}".replace(",", " ")
    return f"{v:.{casas}f}".replace(".", ",")


def _tabela(linhas: list[list], cabecalho: list[str]) -> str:
    out = ["| " + " | ".join(cabecalho) + " |", "| " + " | ".join("---" for _ in cabecalho) + " |"]
    out += ["| " + " | ".join(str(c) for c in l) + " |" for l in linhas]
    return "\n".join(out)


INDICADORES = [
    ("Dimensão", [("palavras", "Palavras", 0), ("frases", "Frases", 0), ("paragrafos", "Parágrafos", 0),
                  ("tempo_leitura_horas", "Tempo de leitura (horas, a 230 palavras/min)", 1)]),
    ("Léxico", [("vocabulario", "Vocabulário (formas distintas)", 0), ("lemas_distintos", "Lemas distintos", 0),
                ("mattr_500", "Variedade lexical (MATTR, janela 500)", 3), ("ttr", "TTR (depende do tamanho)", 3),
                ("hapax_pct", "Hapax (% do vocabulário)", 1), ("yule_k", "K de Yule", 1),
                ("densidade_lexical_pct", "Densidade lexical (%)", 1),
                ("palavra_media_letras", "Palavra média (letras)", 2)]),
    ("Sintaxe e legibilidade", [("frase_media_palavras", "Frase média (palavras)", 1),
                                ("frase_mediana_palavras", "Frase mediana (palavras)", 0),
                                ("frase_maxima_palavras", "Frase mais longa (palavras)", 0),
                                ("paragrafo_medio_palavras", "Parágrafo médio (palavras)", 1),
                                ("dialogo_pct", "Parágrafos de diálogo (%)", 1),
                                ("legibilidade", "Legibilidade (Flesch adaptado)", 1)]),
    ("Pontuação (por 1000 palavras)", [("virgula_por_1000", "Vírgula", 1), ("ponto_por_1000", "Ponto", 1),
                                       ("ponto_e_virgula_por_1000", "Ponto e vírgula", 1),
                                       ("exclamacao_por_1000", "Exclamação", 1),
                                       ("interrogacao_por_1000", "Interrogação", 1),
                                       ("reticencias_por_1000", "Reticências", 1),
                                       ("travessao_por_1000", "Travessão", 1)]),
    ("Entidades (NER)", [("entidades_pessoa", "Pessoas distintas", 0), ("entidades_lugar", "Lugares distintos", 0),
                         ("entidades_organizacao", "Organizações distintas", 0)]),
]

CAMPOS_META = [("titulo", "Título"), ("autor", "Autor"), ("ano", "Ano"), ("data", "Data"),
               ("publicacao_original", "Publicação original"), ("tradutor", "Tradutor"), ("editora", "Editora"),
               ("lingua_declarada", "Língua declarada"), ("identificador", "Identificador"), ("fonte", "Fonte"),
               ("assuntos", "Assuntos")]


def livro(r: dict, freq: pd.DataFrame, ents: pd.DataFrame, pasta: Path):
    i, m, p = r["indicadores"], r["metadados"], r["processamento"]
    s = [f"# {r['titulo']}", ""]
    if r.get("autor"):
        s += [f"**{r['autor']}**" + (f" · {r['ano']}" if r.get("ano") else ""), ""]
    s += ["[← Todos os livros](../../README.md)", "", "## Metadados", ""]
    meta = [[rot, m[k]] for k, rot in CAMPOS_META if m.get(k)]
    meta += [["Ficheiro", f"`{r['ficheiro']}` ({r['formato'].upper()})"],
             ["Língua detetada", f"{r['lingua_nome']} (modelo `{r['modelo_spacy']}`)"]]
    s += [_tabela(meta, ["Campo", "Valor"]), ""]
    s += ["## Indicadores", ""]
    for grupo, campos in INDICADORES:
        s += [f"**{grupo}**", "", _tabela([[rot, _num(i.get(k), c)] for k, rot, c in campos], ["Indicador", "Valor"]), ""]
    s[-1:] = [f"Legibilidade: **{i['legibilidade_escala']}**.", ""]
    for g in r["graficos"]:
        s += [f"![{g}](graficos/{g})", ""]
    s += ["## Lemas mais frequentes", "",
          _tabela([[l.lema, l.pos, l.ocorrencias, _num(l.por_1000_palavras)] for l in freq.head(30).itertuples()],
                  ["Lema", "Classe", "Ocorrências", "Por 1000 palavras"]), ""]
    if not ents.empty:
        s += ["## Entidades mais mencionadas", "",
              _tabela([[e.tipo, e.entidade, e.ocorrencias] for e in ents.groupby("tipo").head(10).itertuples()],
                      ["Tipo", "Entidade", "Ocorrências"]), ""]
    s += ["## Ficheiros", "", "- [`indicadores.json`](indicadores.json) · todos os indicadores e metadados",
          "- [`frequencias.csv`](frequencias.csv) · 200 lemas mais frequentes",
          "- [`entidades.csv`](entidades.csv) · entidades por tipo",
          "- [`evolucao.csv`](evolucao.csv) · indicadores por décimo do livro", "",
          f"<sub>Processado em {p['data']} · livros_pln {p['versao']} · código `{p['versao_codigo']}`"
          + (f" · commit `{p['commit']}`" if p.get("commit") else "") + "</sub>", ""]
    (pasta / "README.md").write_text("\n".join(s), encoding="utf-8")


def corpus(t: pd.DataFrame, figs: list[str], saida: Path, versao: str, codigo: str, commit: str | None):
    # sem data nem commit atual: o ficheiro só muda quando os resultados mudam
    s = ["# Resultados", "",
         f"Gerado automaticamente por livros_pln {versao} (código `{codigo}`). Não editar à mão: estes "
         "ficheiros são reescritos sempre que o código muda. O commit e a data de processamento de cada "
         "livro estão no respetivo relatório.", ""]
    if t.empty:
        (saida / "README.md").write_text("\n".join(s + ["Ainda não há livros processados.", ""]), encoding="utf-8")
        return
    s += [f"**{len(t)} livros · {_num(int(t.palavras.sum()), 0)} palavras** · "
          + ", ".join(f"{n} em {lg}" for lg, n in t.lingua.map({"pt": "português", "fr": "francês",
                                                                     "en": "inglês"}).value_counts().items()), ""]
    linhas = [[f"[{r.titulo}](livros/{r.id}/README.md)", r.autor or "—", r.lingua, _num(r.palavras, 0),
               _num(r.mattr_500, 3), _num(r.frase_media_palavras, 1), _num(r.densidade_lexical_pct, 1),
               f"{_num(r.legibilidade, 0)} ({r.legibilidade_escala})"]
              for r in t.sort_values(["autor", "titulo"], na_position="last").itertuples()]
    s += [_tabela(linhas, ["Livro", "Autor", "Língua", "Palavras", "MATTR", "Frase média", "Densidade lexical (%)",
                           "Legibilidade"]), ""]
    for g in figs:
        s += [f"![{g}](graficos/{g})", ""]
    s += ["Tabela completa: [`indicadores.csv`](indicadores.csv) (uma linha por livro, todos os indicadores).", ""]
    (saida / "README.md").write_text("\n".join(s), encoding="utf-8")
