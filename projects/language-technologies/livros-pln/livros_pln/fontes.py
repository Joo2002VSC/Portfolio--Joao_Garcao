"""Obtenção de livros a partir de um ficheiro local ou de um link.

Links aceites:
  * páginas e ficheiros do Project Gutenberg, em qualquer espelho
    (https://www.gutenberg.org/ebooks/40409, .../cache/epub/40409/pg40409.txt, .../files/40409/...);
    é descarregada a versão em texto (UTF-8) e, se não existir, a versão EPUB;
  * ligações diretas para ficheiros .txt ou .epub.
O ficheiro descarregado é guardado na pasta indicada (por omissão, livros/).
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from . import __version__

LIMITE_BYTES = 60 * 1024 * 1024
CABECALHOS = {"User-Agent": f"livros-pln/{__version__} (+https://github.com/Joo2002VSC/livros-pln)"}


class ErroFonte(Exception):
    pass


def e_link(fonte: str) -> bool:
    return urlparse(str(fonte)).scheme in ("http", "https")


def id_gutenberg(url: str) -> str | None:
    p = urlparse(url)
    if "gutenberg" not in p.netloc:
        return None
    m = re.search(r"/(?:ebooks|epub|files)/(\d+)", p.path) or re.search(r"/pg(\d+)", p.path)
    return m.group(1) if m else None


def candidatos(url: str) -> list[tuple[str, str]]:
    """Lista (url, nome de ficheiro) a tentar, por ordem de preferência."""
    gid = id_gutenberg(url)
    if gid:
        base = f"https://www.gutenberg.org/cache/epub/{gid}"
        return [(f"{base}/pg{gid}.txt", f"gutenberg-{gid}.txt"),
                (f"https://www.gutenberg.org/ebooks/{gid}.txt.utf-8", f"gutenberg-{gid}.txt"),
                (f"{base}/pg{gid}.epub", f"gutenberg-{gid}.epub"),
                (f"https://www.gutenberg.org/ebooks/{gid}.epub.noimages", f"gutenberg-{gid}.epub")]
    nome = Path(unquote(urlparse(url).path)).name
    sufixo = Path(nome).suffix.lower()
    if sufixo not in (".txt", ".epub"):
        raise ErroFonte(f"O link tem de apontar para um ficheiro .txt ou .epub, ou para um livro do Project "
                        f"Gutenberg: {url}")
    return [(url, nome)]


def _parece_html(conteudo: bytes) -> bool:
    inicio = conteudo[:600].lstrip().lower()
    return inicio.startswith((b"<!doctype html", b"<html"))


def descarregar(url: str, pasta: Path, sessao=None, nome_final: str | None = None) -> Path:
    import requests

    sessao = sessao or requests.Session()
    erros = []
    for alvo, nome in candidatos(url):
        try:
            r = sessao.get(alvo, headers=CABECALHOS, timeout=60, stream=True)
            if r.status_code != 200:
                erros.append(f"{alvo}: HTTP {r.status_code}")
                continue
            conteudo = b""
            for bloco in r.iter_content(1 << 16):
                conteudo += bloco
                if len(conteudo) > LIMITE_BYTES:
                    raise ErroFonte(f"Ficheiro maior do que {LIMITE_BYTES // 2**20} MB: {alvo}")
            if nome.endswith(".txt") and _parece_html(conteudo):
                erros.append(f"{alvo}: devolveu uma página HTML e não o texto")
                continue
            if nome.endswith(".epub") and not conteudo.startswith(b"PK"):
                erros.append(f"{alvo}: não é um EPUB válido")
                continue
            pasta.mkdir(parents=True, exist_ok=True)
            destino = pasta / (f"{slug_nome(nome_final)}{Path(nome).suffix}" if nome_final else nome)
            destino.write_bytes(conteudo)
            return destino
        except requests.RequestException as e:
            erros.append(f"{alvo}: {type(e).__name__}")
    raise ErroFonte("Não foi possível descarregar o livro:\n  " + "\n  ".join(erros))


def slug_nome(nome: str) -> str:
    from .leitura import slug
    s = slug(Path(nome).stem if Path(nome).suffix.lower() in (".txt", ".epub") else nome)
    if not s:
        raise ErroFonte(f"Nome de ficheiro inválido: {nome!r}")
    return s


def obter(fonte: str, pasta: Path, nome: str | None = None) -> Path:
    """Devolve o caminho local do livro, descarregando-o se `fonte` for um link (com o nome `nome`, se indicado)."""
    if e_link(fonte):
        return descarregar(fonte, pasta, nome_final=nome)
    caminho = Path(fonte).expanduser()
    if not caminho.exists():
        raise ErroFonte(f"Ficheiro não encontrado: {caminho}")
    if caminho.suffix.lower() not in (".txt", ".epub"):
        raise ErroFonte(f"Formato não suportado (só .txt e .epub): {caminho.name}")
    return caminho
