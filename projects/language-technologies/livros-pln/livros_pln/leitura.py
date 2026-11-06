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
                # «Release date: August 4, 2012 [eBook #40409]»: o número fica no identificador, não na data
                metadados[CAMPOS_GUTENBERG[m.group(1).strip().lower()]] = re.sub(r"\s*\[e(?:book|text) #\d+\]", "",
                                                                                m.group(2).strip(), flags=re.I)
        m = re.search(r"\[e(?:book|text) #(\d+)\]", cabecalho, re.I)
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

    blocos = re.split(r"\n\s*\n", texto)
    metadados.update(forma_do_texto(blocos))
    if metadados["forma"] == "verso":   # os números das estrofes não fazem parte do texto
        blocos = [_sem_numeros(b) for b in blocos]
    paragrafos = [re.sub(r"\s+", " ", p).strip() for p in blocos]
    # convenções tipográficas do texto simples: «_itálico_» e «--» como travessão (Project Gutenberg)
    paragrafos = [re.sub(r"(?<!-)--(?!-)", "—", p.replace("_", "")) for p in paragrafos if p]
    return Livro(ficheiro, "txt", paragrafos, metadados)


_NUMERO = re.compile(r"^\s*(\d{1,4}|[IVXLC]{1,7})[.)]?\s*$")


def _sem_numeros(bloco: str) -> str:
    """Retira as linhas que só têm um número (árabe ou romano), como a numeração das estrofes."""
    return "\n".join(l for l in bloco.splitlines() if not _NUMERO.match(l))


def forma_do_texto(blocos: list[str], maximo_verso: int = 55) -> dict:
    """Distingue prosa de verso pela extensão das linhas dentro dos blocos com 4 ou mais linhas.

    No Project Gutenberg, a prosa vem quebrada em linhas de cerca de 70 caracteres; os versos são linhas curtas
    (um decassílabo tem cerca de 35 a 45 caracteres). Considera-se verso quando os blocos com linhas de extensão
    média até `maximo_verso` caracteres têm mais de metade das palavras do texto."""
    palavras_total, palavras_verso, versos, por_estrofe = 0, 0, 0, []
    for b in blocos:
        linhas = [l.strip() for l in _sem_numeros(b).splitlines() if l.strip()]
        n = sum(len(l.split()) for l in linhas)
        palavras_total += n
        if len(linhas) >= 4 and sum(map(len, linhas)) / len(linhas) <= maximo_verso:
            palavras_verso += n
            versos += len(linhas)
            por_estrofe.append(len(linhas))
    if palavras_total and palavras_verso / palavras_total > 0.5:
        por_estrofe.sort()
        return {"forma": "verso", "versos": versos, "estrofes": len(por_estrofe),
                "versos_por_estrofe": por_estrofe[len(por_estrofe) // 2]}
    return {"forma": "prosa"}


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
    """Lê livros/metadados.csv (opcional), que completa ou corrige os metadados extraídos.

    Colunas aceites: ficheiro, titulo, autor, ano, lingua (força a língua: pt, fr ou en) e fonte."""
    ficheiro = pasta / "metadados.csv"
    if not ficheiro.exists():
        return {}
    with ficheiro.open(encoding="utf-8") as f:
        return {linha["ficheiro"]: {("fonte_manual" if k == "fonte" else k): v for k, v in linha.items()
                                    if k != "ficheiro" and v}
                for linha in csv.DictReader(f)}


CAMPOS_PRINCIPAIS = ("titulo", "autor", "ano", "idioma", "fonte")


def _ano(*valores) -> str | None:
    for v in valores:
        m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", str(v or ""))
        if m:
            return m.group(1)
    return None


def principais(bruto: dict, idioma: str) -> dict:
    """Reduz os metadados aos principais: título, autor, ano, idioma e fonte.

    - ano: o de metadados.csv; senão, o da publicação original indicada no cabeçalho do Project Gutenberg; senão,
      a data do EPUB. A data de publicação digital do Project Gutenberg não conta (não é o ano do livro).
    - idioma: a língua detetada no texto (ou forçada em metadados.csv).
    - fonte: a indicada em metadados.csv; senão, Project Gutenberg (com o número do livro), a editora do EPUB ou o
      formato do ficheiro."""
    fonte = bruto.get("fonte_manual")
    if not fonte:
        if bruto.get("fonte") == "Project Gutenberg":
            gid = str(bruto.get("identificador", "")).removeprefix("gutenberg:")
            fonte = f"Project Gutenberg, n.º\u00a0{gid}" if gid.isdigit() else "Project Gutenberg"
        elif bruto.get("editora"):
            fonte = bruto["editora"]
        else:
            fonte = bruto.get("fonte") or bruto.get("formato")
    autor = bruto.get("autor")
    if autor and ";" in autor:
        autor = "; ".join(dict.fromkeys(a.strip() for a in autor.split(";")))
    return {
        "titulo": bruto.get("titulo"),
        "autor": autor,
        "ano": _ano(bruto.get("ano"), bruto.get("publicacao_original"), bruto.get("data")),
        "idioma": idioma,
        "fonte": fonte,
    }


def ler(ficheiro: Path) -> Livro:
    sufixo = ficheiro.suffix.lower()
    if sufixo == ".txt":
        return ler_txt(ficheiro)
    if sufixo == ".epub":
        return ler_epub(ficheiro)
    raise ValueError(f"Formato não suportado: {ficheiro.name}")


def ler_pasta(pasta: Path) -> list[Path]:
    return sorted(p for p in pasta.iterdir() if p.suffix.lower() in FORMATOS and not p.name.startswith("."))
