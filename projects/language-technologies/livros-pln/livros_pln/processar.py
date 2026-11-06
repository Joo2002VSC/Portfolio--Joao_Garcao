"""Processa livros (TXT ou EPUB, ficheiro ou link) e exporta indicadores, gráficos e painéis.

Uso:
    python -m livros_pln                                   # todos os livros de livros/ → resultados/
    python -m livros_pln --forcar                          # reprocessa tudo, mesmo sem alterações
    python -m livros_pln analisar livros/um-livro.epub     # um livro, com resumo no terminal
    python -m livros_pln analisar https://www.gutenberg.org/ebooks/40409 --abrir

Um livro é reprocessado quando muda o ficheiro, o seu dicionário de personagens, o código ou
os parâmetros (impressão digital dos ficheiros .py do pacote e de config/). Cada resultado
regista a versão, os parâmetros, as versões das bibliotecas e dos modelos e o commit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import webbrowser
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import pandas as pd

from . import (__version__, catalogo, configuracao, estilometria, exportar, fontes, graficos, indicadores, interativo,
               leitura, lingua, personagens, qualidade, relatorio, sentimento)
from .configuracao import PARAMETROS

PACOTE = Path(__file__).resolve().parent
BIBLIOTECAS = ["spacy", "pandas", "numpy", "scipy", "networkx", "matplotlib", "plotly", "ebooklib", "beautifulsoup4",
               "vaderSentiment", "leia-br", "vaderSentiment-fr"]


def versao_codigo() -> str:
    h = hashlib.sha256(__version__.encode())
    # o código, os parâmetros e as stopwords determinam os resultados
    config = PACOTE.parent / "config"
    tomls = [f for f in sorted(config.glob("*.toml")) if f.name not in ("pastas.toml", "pastas.exemplo.toml")]
    for f in sorted(PACOTE.glob("*.py")) + sorted(config.glob("*.txt")) + tomls:
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def commit_atual() -> str | None:
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"][:7]
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=PACOTE, check=True).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def ambiente(lg: str) -> dict:
    versoes = {}
    for b in BIBLIOTECAS:
        try:
            versoes[b] = metadata.version(b)
        except metadata.PackageNotFoundError:
            versoes[b] = None
    return {"python": platform.python_version(), "bibliotecas": versoes, "modelo": indicadores.info_modelo(lg)}


def _json(valor):
    if isinstance(valor, float) and valor != valor:
        return None
    if hasattr(valor, "item"):
        return valor.item()
    return valor


def dicionario_de(ficheiro: Path) -> Path:
    return ficheiro.parent / "personagens" / f"{leitura.slug(ficheiro.stem)}.json"


def _hash_dicionario(ficheiro: Path) -> str | None:
    d = dicionario_de(ficheiro)
    return leitura.impressao_digital(d) if d.exists() else None


class ErroLivro(Exception):
    pass


def processar_livro(ficheiro: Path, saida: Path, manuais: dict, codigo: str, commit: str | None,
                    offline: bool = False, p=PARAMETROS) -> dict:
    inicio = time.time()
    livro = leitura.ler(ficheiro)
    bruto = {**livro.metadados, "formato": livro.formato.upper(), **manuais.get(ficheiro.name, {})}
    lg, pontuacao = lingua.detetar(livro.texto)
    if bruto.get("lingua") in lingua.MODELOS:  # metadados.csv pode forçar a língua
        lg = bruto["lingua"]
    meta = leitura.principais(bruto, lingua.NOMES[lg].capitalize())

    avisos = qualidade.verificar_texto(livro.paragrafos, pontuacao, lg, bruto.get("lingua_declarada"), p.minimo_texto)
    if any(a["nivel"] == "erro" for a in avisos):
        raise ErroLivro("; ".join(a["mensagem"] for a in avisos if a["nivel"] == "erro"))

    # PLN
    tokens, frases, ents = indicadores.anotar(livro.paragrafos, lg)
    ind, estados = indicadores.calcular(livro.paragrafos, tokens, frases, ents, lg, p)
    avisos += qualidade.verificar_anotacao(ind["frases"] or 0, frases.palavras[frases.palavras > 0], ind["palavras"])
    freq = indicadores.frequencias(tokens)
    classes = indicadores.classes_gramaticais(tokens)
    tab_ents = indicadores.tabela_entidades(ents)
    # forma poética: em verso, a legibilidade e a heurística de diálogo não se aplicam
    if bruto.get("forma") == "verso":
        for k in ("versos", "estrofes", "versos_por_estrofe"):
            ind[k] = bruto.get(k)
        motivo = "texto em verso: as fórmulas de legibilidade foram calibradas com prosa"
        for k in ("legibilidade", "flesch_kincaid", "silabas_por_palavra"):
            estados[k] = {"estado": qualidade.NAO_APLICAVEL, "motivo": motivo}
            ind[k] = None
        estados["dialogo_pct"] = {"estado": qualidade.NAO_APLICAVEL,
                                  "motivo": "texto em verso: a deteção do diálogo assume a tipografia da prosa"}
        ind["dialogo_pct"] = None
        for k in ("legibilidade_escala", "legibilidade_leitura", "legibilidade_nivel"):
            ind[k] = None
        avisos.append(qualidade.aviso(
            "aviso", "verso", f"Texto em verso ({bruto.get('versos')} versos em {bruto.get('estrofes')} estrofes, "
            f"{bruto.get('versos_por_estrofe')} versos por estrofe). A legibilidade e o diálogo ficam «não aplicável»; "
            "os modelos linguísticos e os léxicos de sentimento foram treinados com prosa contemporânea, por isso a "
            "segmentação, a etiquetagem e o sentimento são menos fiáveis do que num romance."))
    else:
        for k in ("versos", "estrofes", "versos_por_estrofe"):
            ind[k] = None
            estados[k] = {"estado": qualidade.NAO_APLICAVEL, "motivo": "texto em prosa"}

    senti = sentimento.analisar(frases, tokens, lg, p)
    for k in [k for k, i in catalogo.INDICADORES.items() if i.grupo == "Sentimento"]:
        ind[k] = senti["indicadores"].get(k)
        if senti["estado"] != "valido":
            estados[k] = {"estado": senti["estado"], "motivo": senti["motivo"]}
    evol = indicadores.evolucao(tokens, frases, ents, livro.paragrafos, p)
    if bruto.get("forma") == "verso" and "dialogo_pct" in evol:
        evol["dialogo_pct"] = float("nan")
    segmentos = indicadores.segmentos_das_frases(tokens, p.segmentos)
    contagem = tokens[tokens.alfa].minusc.value_counts()
    extra = {
        "colocacoes": indicadores.colocacoes(tokens, p.colocacao_frequencia_minima),
        "palavras_chave": indicadores.palavras_chave(tokens, segmentos, p.palavras_chave_por_segmento),
        "tempos": indicadores.tempos_verbais(tokens),
        "heaps": indicadores.curva_heaps(tokens[tokens.alfa].minusc.tolist()),
        "zipf": indicadores.tabela_zipf(dict(contagem), p.zipf_frequencia_minima),
        "extremos": senti["extremos"],
        "frases": frases.assign(segmento=frases.frase.map(segmentos))[["frase", "segmento", "palavras", "tipo",
                                                                       "sentimento"]],
        "sentimento": {k: senti[k] for k in ("estado", "motivo", "metodo")},
    }

    # rede de personagens
    g, pers, lig, metodo = personagens.analisar(livro.paragrafos, ents, lg, dicionario_de(ficheiro),
                                                ignorar=indicadores.stopwords_extra(lg), min_mencoes=p.rede_minimo_mencoes)
    n_nos = g.number_of_nodes()
    ind["personagens_na_rede"] = n_nos
    ind["ligacoes_na_rede"] = g.number_of_edges()
    ind["densidade_da_rede"] = round(2 * g.number_of_edges() / (n_nos * (n_nos - 1)), 4) if n_nos > 1 else None
    if n_nos < 2:
        estados["densidade_da_rede"] = {"estado": qualidade.NAO_APLICAVEL, "motivo": "menos de duas personagens na rede"}
    ind["personagem_principal"] = pers.personagem.iloc[0] if len(pers) else None

    pasta = saida / "livros" / livro.id
    if pasta.exists():
        shutil.rmtree(pasta)
    (pasta / "graficos").mkdir(parents=True)
    titulo = meta.get("titulo") or livro.ficheiro.stem
    amb = ambiente(lg)
    figs = graficos.por_livro(titulo, amb["modelo"]["nome"], classes, freq, frases.palavras, evol, tab_ents, g, metodo,
                              p.frase_longa, pasta / "graficos", extra=extra, p=p, ind=ind)
    freq.to_csv(pasta / "frequencias.csv", index=False)
    classes.round(3).to_csv(pasta / "classes-gramaticais.csv", index=False)
    tab_ents.to_csv(pasta / "entidades.csv", index=False)
    evol.round(4).to_csv(pasta / "evolucao.csv", index=False)
    frases[["palavras", "profundidade", "subordinadas", "tipo", "sentimento"]].round(4).to_csv(pasta / "frases.csv",
                                                                                          index=False)
    extra["colocacoes"].round(3).to_csv(pasta / "colocacoes.csv", index=False)
    extra["palavras_chave"].round(4).to_csv(pasta / "palavras-chave.csv", index=False)
    extra["tempos"].round(3).to_csv(pasta / "tempos-verbais.csv", index=False)
    extra["extremos"].round(4).to_csv(pasta / "sentimento-frases-extremas.csv", index=False)
    formas = tokens[tokens.alfa].minusc.value_counts().head(2000).rename_axis("forma").rename("ocorrencias")
    formas.to_csv(pasta / "formas.csv")
    pers.round(4).to_csv(pasta / "personagens.csv", index=False)
    lig.to_csv(pasta / "ligacoes.csv", index=False)

    registo = {
        "id": livro.id, "ficheiro": ficheiro.name, "formato": livro.formato, "titulo": titulo,
        "autor": meta.get("autor"), "ano": meta.get("ano"),
        "lingua": lg, "lingua_nome": lingua.NOMES[lg], "modelo_spacy": amb["modelo"]["nome"],
        "confianca_lingua": {k: round(v, 4) for k, v in pontuacao.items()},
        "forma": bruto.get("forma", "prosa"), "metodo_sentimento": senti["metodo"], "metodo_personagens": metodo, "personagens_principais": pers.personagem.head(10).tolist(),
        "metadados": meta,
        "indicadores": {k: _json(round(v, 4) if isinstance(v, float) else v) for k, v in ind.items()},
        "estados": estados,
        "qualidade": avisos,
        "parametros": configuracao.como_dicionario(p),
        "ambiente": amb,
        "processamento": {
            "versao": __version__, "versao_codigo": codigo, "commit": commit,
            "codificacao": bruto.get("codificacao"), "hash_ficheiro": leitura.impressao_digital(ficheiro), "hash_dicionario": _hash_dicionario(ficheiro),
            "data": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "duracao_s": round(time.time() - inicio, 1),
        },
        "graficos": figs,
    }
    (pasta / "indicadores.json").write_text(json.dumps(registo, ensure_ascii=False, indent=2), encoding="utf-8")
    relatorio.livro(registo, freq, classes, tab_ents, evol, pers, pasta, extra=extra)
    interativo.painel_livro(registo, freq, classes, frases.palavras, evol, tab_ents, pers, g, pasta / "painel.html", offline,
                            extra=extra)
    exportar.livro(registo, {"Frequências": freq, "Classes gramaticais": classes.round(3), "Entidades": tab_ents,
                             "Personagens": pers.round(4), "Ligações": lig, "Evolução": evol.round(4),
                             "Colocações": extra["colocacoes"].round(3), "Palavras-chave": extra["palavras_chave"].round(4),
                             "Tempos verbais": extra["tempos"].round(3), "Sentimento (extremos)": extra["extremos"].round(4)},
                   pasta / f"{livro.id}.xlsx")
    return registo


def precisa(ficheiro: Path, saida: Path, codigo: str) -> bool:
    destino = saida / "livros" / leitura.slug(ficheiro.stem) / "indicadores.json"
    if not destino.exists():
        return True
    anterior = json.loads(destino.read_text(encoding="utf-8"))["processamento"]
    return (anterior.get("versao_codigo") != codigo
            or anterior.get("hash_ficheiro") != leitura.impressao_digital(ficheiro)
            or anterior.get("hash_dicionario") != _hash_dicionario(ficheiro))


def registos(saida: Path) -> list[dict]:
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted((saida / "livros").glob("*/indicadores.json"))]


def tabela_corpus(saida: Path) -> pd.DataFrame:
    linhas = [{k: r[k] for k in ("id", "ficheiro", "formato", "titulo", "autor", "ano", "lingua")}
              | r["indicadores"] | {"versao": r["processamento"]["versao"], "commit": r["processamento"]["commit"]}
              for r in registos(saida)]
    return pd.DataFrame(linhas)


def atualizar_corpus(saida: Path, codigo: str, commit: str | None, offline: bool, p=PARAMETROS) -> pd.DataFrame:
    tabela = tabela_corpus(saida)
    saida.mkdir(parents=True, exist_ok=True)
    tabela.round(4).to_csv(saida / "indicadores.csv", index=False)
    pasta_graficos = saida / "graficos"
    if pasta_graficos.exists():
        shutil.rmtree(pasta_graficos)
    resultado_delta = {}
    figs = []
    if not tabela.empty:
        exportar.corpus(tabela.round(4), saida / "indicadores.xlsx")
        base = saida / "livros"
        classes = {i: pd.read_csv(base / i / "classes-gramaticais.csv") for i in tabela.id}
        frases = {i: pd.read_csv(base / i / "frases.csv").palavras for i in tabela.id}
        evolucoes = {i: pd.read_csv(base / i / "evolucao.csv") for i in tabela.id if (base / i / "evolucao.csv").stat().st_size > 1}
        formas = {i: pd.read_csv(base / i / "formas.csv", index_col=0, keep_default_na=False).ocorrencias for i in tabela.id}
        resultado_delta = estilometria.delta(formas, dict(zip(tabela.id, tabela.lingua)), p)
        for lg, r in resultado_delta.items():
            if r["estado"] == "valido":
                r["matriz"].round(4).to_csv(saida / f"delta-{lg}.csv")
        figs = graficos.corpus(tabela, classes, frases, evolucoes, resultado_delta, pasta_graficos)
    interativo.painel_corpus(tabela, saida / "painel.html", offline)
    relatorio.corpus(tabela, figs, resultado_delta, saida, __version__, codigo)
    return tabela


def resumo(r: dict, saida: Path) -> str:
    """Resumo para o terminal."""
    i, m, e = r["indicadores"], r["metadados"], r["estados"]
    tema = __import__("livros_pln.tema", fromlist=["num"])

    def n(chave, casas=1):
        if chave in e:
            return qualidade.ROTULOS[e[chave]["estado"]]
        return tema.num(i.get(chave), casas)

    linhas = [
        "", f"  {r['titulo']}" + (f" · {r['autor']}" if r.get("autor") else "") + (f" · {r['ano']}" if r.get("ano") else ""),
        "  " + "─" * 66,
        f"  Língua              {r['lingua_nome']} ({r['modelo_spacy']})",
        f"  Fonte               {m.get('fonte', r['formato'].upper())}" + (f" · {m['identificador']}" if m.get("identificador") else ""),
        f"  Dimensão            {n('palavras', 0)} palavras · {n('frases', 0)} frases · {n('paragrafos', 0)} parágrafos",
        f"  Diversidade lexical MTLD {n('mtld')} · MATTR {n('mattr', 3)} · HD-D {n('hdd', 3)}",
        f"  Frases              mediana {n('frase_mediana', 0)} palavras (P25–P75: {n('frase_p25', 0)}–{n('frase_p75', 0)}) · "
        f"longas {n('frases_longas_pct')} %",
        f"  Sintaxe             profundidade {n('profundidade_media', 2)} · distância de dependência "
        f"{n('distancia_dependencia', 2)} · subordinadas/frase {n('subordinadas_por_frase', 2)}",
        f"  Legibilidade        {n('legibilidade')} ({i.get('legibilidade_escala') or '—'}; Flesch adaptado a {r['lingua']})",
        f"  Densidade lexical   {n('densidade_lexical_pct')} %  ·  diálogo {n('dialogo_pct')} % (estimativa)",
        f"  Personagens         {n('personagens_na_rede', 0)} na rede ({r['metodo_personagens']})",
    ]
    if r["personagens_principais"]:
        linhas.append(f"                      principais: {', '.join(r['personagens_principais'][:6])}")
    for a in r["qualidade"]:
        linhas.append(f"  ⚠ {a['mensagem']}")
    pasta = saida / "livros" / r["id"]
    linhas += ["", f"  Painel interativo  {pasta / 'painel.html'}", f"  Excel              {pasta / (r['id'] + '.xlsx')}",
               f"  Relatório          {pasta / 'README.md'}", ""]
    return "\n".join(linhas)


def cmd_analisar(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="python -m livros_pln analisar",
                                 description="Analisa um livro a partir de um ficheiro .txt/.epub ou de um link.")
    ap.add_argument("fonte", help="caminho para um .txt/.epub, link do Project Gutenberg ou link direto para .txt/.epub")
    livros, resultados = configuracao.pastas()
    ap.add_argument("--pasta", type=Path, default=livros,
                    help=f"onde guardar livros descarregados (por omissão: {livros})")
    ap.add_argument("--saida", type=Path, default=resultados, help=f"pasta dos resultados (por omissão: {resultados})")
    ap.add_argument("--nome", help="nome do ficheiro guardado, sem extensão (ex.: camoes-os-lusiadas)")
    ap.add_argument("--offline", action="store_true", help="embute o Plotly nos painéis (funcionam sem internet)")
    ap.add_argument("--abrir", action="store_true", help="abre o painel no navegador no fim")
    args = ap.parse_args(argv)
    try:
        if fontes.e_link(args.fonte):
            print(f"↓ A descarregar {args.fonte}")
        ficheiro = fontes.obter(args.fonte, args.pasta, args.nome)
    except fontes.ErroFonte as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    print(f"▶ A analisar {ficheiro.name} …")
    codigo, commit = versao_codigo(), commit_atual()
    try:
        r = processar_livro(ficheiro, args.saida, leitura.metadados_manuais(ficheiro.parent), codigo, commit, args.offline)
    except ErroLivro as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    atualizar_corpus(args.saida, codigo, commit, args.offline)
    print(resumo(r, args.saida))
    if args.abrir:
        webbrowser.open((args.saida / "livros" / r["id"] / "painel.html").resolve().as_uri())
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "analisar":
        return cmd_analisar(argv[1:])

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    livros, resultados = configuracao.pastas()
    ap.add_argument("--pasta", type=Path, default=livros, help=f"pasta dos livros (por omissão: {livros})")
    ap.add_argument("--saida", type=Path, default=resultados, help=f"pasta dos resultados (por omissão: {resultados})")
    ap.add_argument("--forcar", action="store_true", help="reprocessa todos os livros")
    ap.add_argument("--offline", action="store_true", help="embute o Plotly nos painéis (funcionam sem internet)")
    args = ap.parse_args(argv)

    ficheiros = leitura.ler_pasta(args.pasta)
    if not ficheiros:
        print(f"Nenhum livro (.txt ou .epub) em {args.pasta}/")
        return 1
    codigo, commit = versao_codigo(), commit_atual()
    manuais = leitura.metadados_manuais(args.pasta)
    print(f"livros_pln {__version__} · código {codigo} · {len(ficheiros)} livro(s)")

    ids = {leitura.slug(f.stem) for f in ficheiros}
    for antiga in (args.saida / "livros").glob("*"):  # resultados de livros retirados da pasta
        if antiga.is_dir() and antiga.name not in ids:
            shutil.rmtree(antiga)
            print(f"  − {antiga.name} (livro removido)")

    erros = 0
    for f in ficheiros:
        if not args.forcar and not precisa(f, args.saida, codigo):
            print(f"  = {f.name} (sem alterações)")
            continue
        try:
            r = processar_livro(f, args.saida, manuais, codigo, commit, args.offline)
            i = r["indicadores"]
            palavras = f"{i['palavras']:,}".replace(",", " ")
            mtld = "n.a." if i["mtld"] is None else f"{i['mtld']:.1f}"
            print(f"  ✓ {f.name}: {r['lingua_nome']}, {palavras} palavras, MTLD {mtld}, "
                  f"{i['personagens_na_rede']} personagens, {r['processamento']['duracao_s']} s"
                  + (f", {len(r['qualidade'])} aviso(s)" if r["qualidade"] else ""))
        except Exception as e:  # um livro com problemas não impede os outros
            erros += 1
            print(f"  ✗ {f.name}: {type(e).__name__}: {e}", file=sys.stderr)

    tabela = atualizar_corpus(args.saida, codigo, commit, args.offline)
    print(f"✓ {len(tabela)} livro(s) em {args.saida}/" + (f" · {erros} erro(s)" if erros else ""))
    return 1 if erros else 0
