"""Processa todos os livros de uma pasta e exporta indicadores, gráficos e relatórios.

Uso:
    python -m livros_pln                     # livros/ → resultados/
    python -m livros_pln --forcar            # reprocessa tudo, mesmo sem alterações
    python -m livros_pln --pasta outra/ --saida outros-resultados/

Um livro é reprocessado quando o ficheiro muda ou quando muda a versão do código
(impressão digital dos ficheiros .py do pacote). Os resultados de cada livro guardam
a versão e o commit que os produziram.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import __version__, graficos, indicadores, leitura, lingua, relatorio

PACOTE = Path(__file__).resolve().parent


def versao_codigo() -> str:
    h = hashlib.sha256(__version__.encode())
    # o código e a configuração (stopwords) determinam os resultados
    for f in sorted(PACOTE.glob("*.py")) + sorted((PACOTE.parent / "config").glob("*.txt")):
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


def _json(valor):
    if isinstance(valor, float) and valor != valor:  # NaN
        return None
    if hasattr(valor, "item"):
        return valor.item()
    return valor


def processar_livro(ficheiro: Path, saida: Path, manuais: dict, codigo: str, commit: str | None) -> dict:
    inicio = time.time()
    livro = leitura.ler(ficheiro)
    meta = {**livro.metadados, **manuais.get(ficheiro.name, {})}
    lg, pontuacao = lingua.detetar(livro.texto)
    if meta.get("lingua") in lingua.MODELOS:  # metadados.csv pode forçar a língua
        lg = meta["lingua"]
    tokens, ents = indicadores.anotar(livro.paragrafos, lg)
    ind = indicadores.calcular(livro.paragrafos, tokens, ents, lg)
    freq = indicadores.frequencias(tokens)
    tab_ents = indicadores.tabela_entidades(ents)
    evol = indicadores.evolucao(tokens)
    frases = indicadores.distribuicao_frases(tokens)
    pos = tokens[tokens.alfa].pos.value_counts(normalize=True) * 100

    pasta = saida / "livros" / livro.id
    if pasta.exists():
        shutil.rmtree(pasta)
    (pasta / "graficos").mkdir(parents=True)
    titulo = meta.get("titulo") or livro.ficheiro.stem
    figs = graficos.por_livro(titulo, freq, pos, frases, evol, tab_ents, pasta / "graficos")
    freq.to_csv(pasta / "frequencias.csv", index=False)
    tab_ents.to_csv(pasta / "entidades.csv", index=False)
    evol.round(4).to_csv(pasta / "evolucao.csv", index=False)

    registo = {
        "id": livro.id,
        "ficheiro": ficheiro.name,
        "formato": livro.formato,
        "titulo": titulo,
        "autor": meta.get("autor"),
        "ano": meta.get("ano") or meta.get("data"),
        "lingua": lg,
        "lingua_nome": lingua.NOMES[lg],
        "modelo_spacy": lingua.MODELOS[lg],
        "confianca_lingua": {k: round(v, 4) for k, v in pontuacao.items()},
        "metadados": meta,
        "indicadores": {k: _json(round(v, 4) if isinstance(v, float) else v) for k, v in ind.items()},
        "processamento": {
            "versao": __version__, "versao_codigo": codigo, "commit": commit,
            "hash_ficheiro": leitura.impressao_digital(ficheiro),
            "data": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "duracao_s": round(time.time() - inicio, 1),
        },
        "graficos": figs,
    }
    (pasta / "indicadores.json").write_text(json.dumps(registo, ensure_ascii=False, indent=2), encoding="utf-8")
    relatorio.livro(registo, freq, tab_ents, pasta)
    return registo


def precisa(ficheiro: Path, saida: Path, codigo: str) -> bool:
    destino = saida / "livros" / leitura.slug(ficheiro.stem) / "indicadores.json"
    if not destino.exists():
        return True
    anterior = json.loads(destino.read_text(encoding="utf-8"))["processamento"]
    return anterior.get("versao_codigo") != codigo or anterior.get("hash_ficheiro") != leitura.impressao_digital(ficheiro)


def tabela_corpus(saida: Path) -> pd.DataFrame:
    registos = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((saida / "livros").glob("*/indicadores.json"))]
    linhas = [{k: r[k] for k in ("id", "ficheiro", "formato", "titulo", "autor", "ano", "lingua")}
              | r["indicadores"] | {"versao": r["processamento"]["versao"], "commit": r["processamento"]["commit"]}
              for r in registos]
    return pd.DataFrame(linhas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pasta", type=Path, default=Path("livros"))
    ap.add_argument("--saida", type=Path, default=Path("resultados"))
    ap.add_argument("--forcar", action="store_true", help="reprocessa todos os livros")
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
            r = processar_livro(f, args.saida, manuais, codigo, commit)
            i = r["indicadores"]
            palavras = f"{i['palavras']:,}".replace(",", " ")
            print(f"  ✓ {f.name}: {r['lingua_nome']}, {palavras} palavras, "
                  f"MATTR {i['mattr_500']:.3f}, {r['processamento']['duracao_s']} s")
        except Exception as e:  # um livro com problemas não impede os outros
            erros += 1
            print(f"  ✗ {f.name}: {type(e).__name__}: {e}", file=sys.stderr)

    tabela = tabela_corpus(args.saida)
    args.saida.mkdir(parents=True, exist_ok=True)
    tabela.round(4).to_csv(args.saida / "indicadores.csv", index=False)
    figs = graficos.corpus(tabela, args.saida / "graficos")
    relatorio.corpus(tabela, figs, args.saida, __version__, codigo, commit)
    print(f"✓ {len(tabela)} livro(s) em {args.saida}/" + (f" · {erros} erro(s)" if erros else ""))
    return 1 if erros else 0
