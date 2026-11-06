"""Leitura de livros em TXT e EPUB e extração de metadados."""
from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
import warnings
from dataclasses import dataclass, field
from pathlib import Path

FORMATOS = {".txt", ".epub"}


@dataclass
class Livro:
    ficheiro: Path
    formato: str
    paragrafos: list[str]
    metadados: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return slug(self.ficheiro.stem)

    @property
    def texto(self) -> str:
        return "\n\n".join(self.paragrafos)


def slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def impressao_digital(ficheiro: Path) -> str:
    return hashlib.sha256(ficheiro.read_bytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------

CAMPOS_GUTENBERG = {
    "title": "titulo", "author": "autor", "release date": "data_publicacao_digital",
    "language": "lingua_declarada", "translator": "tradutor", "credits": "creditos",
    "original publication": "publicacao_original",
}


def ler_txt(ficheiro: Path) -> Livro:
    bruto = ficheiro.read_bytes()
    for codificacao in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            texto = bruto.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue
    texto = texto.replace("\r\n", "\n")
    metadados: dict = {"codificacao": codificacao}

    inicio = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG[^\n]*\*\*\*", texto, re.I)
    fim = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", texto, re.I)
    if inicio:
        metadados["fonte"] = "Project Gutenberg"
        cabecalho = texto[: inicio.start()]
        for linha in cabecalho.splitlines():
            m = re.match(r"^([A-Za-z ]+):\s*(.+)$", linha.strip())
            if m and m.group(1).strip().lower() in CAMPOS_GUTENBERG:
                metadados[CAMPOS_GUTENBERG[m.group(1).strip().lower()]] = m.group(2).strip()
        m = re.search(r"\[E(?:Book|text) #(\d+)\]", cabecalho)
        if m:
            metadados["identificador"] = f"gutenberg:{m.group(1)}"
        texto = texto[inicio.end(): fim.start() if fim else len(texto)]
    else:
        # cópias sem cabeçalho (ex.: corpus NLTK): «[Título by Autor Ano]» na primeira linha
        m = re.match(r"\s*\[(.+?) by (.+?)(?: (\d{4}))?\]", texto)
        if m:
            metadados.update({"titulo": m.group(1), "autor": m.group(2)})
            if m.group(3):
                metadados["ano"] = m.group(3)
            texto = texto[m.end():]

    paragrafos = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", texto)]
    # convenções tipográficas do texto simples: «_itálico_» e «--» como travessão (Project Gutenberg)
    paragrafos = [re.sub(r"(?<!-)--(?!-)", "—", p.replace("_", "")) for p in paragrafos if p]
    return Livro(ficheiro, "txt", paragrafos, metadados)


# ---------------------------------------------------------------------------
# EPUB
# ---------------------------------------------------------------------------

def ler_epub(ficheiro: Path) -> Livro:
    from bs4 import BeautifulSoup
    import ebooklib
    from ebooklib import epub

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        livro = epub.read_epub(str(ficheiro), options={"ignore_ncx": True})

    def dc(campo):
        valores = [v for v, _ in livro.get_metadata("DC", campo)]
        return "; ".join(str(v) for v in valores if v) or None

    metadados = {k: v for k, v in {
        "titulo": dc("title"), "autor": dc("creator"), "data": dc("date"), "lingua_declarada": dc("language"),
        "editora": dc("publisher"), "assuntos": dc("subject"), "identificador": dc("identifier"),
        "descricao": dc("description"), "direitos": dc("rights"), "fonte": "EPUB",
    }.items() if v}

    paragrafos = []
    for item_id, _ in livro.spine:
        item = livro.get_item_with_id(item_id)
        if item is None or item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
        sopa = BeautifulSoup(item.get_content(), "html.parser")
        for etiqueta in sopa(["script", "style", "nav"]):
            etiqueta.decompose()
        for bloco in sopa.find_all(["p", "h1", "h2", "h3", "h4", "blockquote", "li"]):
            if bloco.find(["p", "li"]):  # evita duplicar blocos aninhados
                continue
            for br in bloco.find_all("br"):
                br.replace_with(" ")
            txt = re.sub(r"\s+", " ", bloco.get_text()).strip()
            if txt:
                paragrafos.append(txt)
    return Livro(ficheiro, "epub", paragrafos, metadados)


# ---------------------------------------------------------------------------
# Metadados manuais e leitura de uma pasta
# ---------------------------------------------------------------------------

def metadados_manuais(pasta: Path) -> dict[str, dict]:
    """Lê livros/metadados.csv (opcional), que completa ou corrige os metadados extraídos."""
    ficheiro = pasta / "metadados.csv"
    if not ficheiro.exists():
        return {}
    with ficheiro.open(encoding="utf-8") as f:
        return {linha["ficheiro"]: {k: v for k, v in linha.items() if k != "ficheiro" and v}
                for linha in csv.DictReader(f)}


def ler(ficheiro: Path) -> Livro:
    sufixo = ficheiro.suffix.lower()
    if sufixo == ".txt":
        return ler_txt(ficheiro)
    if sufixo == ".epub":
        return ler_epub(ficheiro)
    raise ValueError(f"Formato não suportado: {ficheiro.name}")


def ler_pasta(pasta: Path) -> list[Path]:
    return sorted(p for p in pasta.iterdir() if p.suffix.lower() in FORMATOS and not p.name.startswith("."))
