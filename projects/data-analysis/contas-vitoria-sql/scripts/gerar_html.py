"""Gera uma versão HTML autónoma do projeto: html/contas-vitoria.html.

Junta num só ficheiro o README, as três análises, os gráficos, a letra
Archivo, a base de dados e o SQLite (sql.js, em scripts/vendor), com uma
consola para correr as consultas SQL no browser. Basta abrir o ficheiro com
duplo clique; só o diagrama do modelo de dados precisa de internet.

Com --publicar, grava também uma variante sem <html>/<head> e sem descarga
de CSV, pronta a publicar como página (o caminho vai como argumento).

Uso (a partir da raiz do projeto, depois de build_db.py e graficos.py):
    pip install markdown
    python scripts/gerar_html.py
"""
import base64
import html
import json
import re
import unicodedata
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "html" / "contas-vitoria.html"
VENDOR = RAIZ / "scripts" / "vendor"

DOCUMENTOS = [
    ("projeto", "Projeto", "README.md"),
    ("estrategica", "Análise estratégica", "analise-estrategica.md"),
    ("tecnica", "Análise técnica", "analise-tecnica.md"),
    ("verificacao", "Verificação das fontes", "verificacao-fontes.md"),
    ("resultados", "Resultados", "resultados.md"),
]
PAGINA_DE = {ficheiro: pid for pid, _, ficheiro in DOCUMENTOS}


def b64(caminho):
    return base64.b64encode(caminho.read_bytes()).decode()


def slug_github(texto, separador="-"):
    """Imita os identificadores que o GitHub dá aos títulos."""
    texto = re.sub(r"<[^>]+>", "", texto).strip().lower()
    texto = "".join(c for c in texto
                    if c in " -_" or unicodedata.category(c)[0] in "LN")
    return texto.replace(" ", "-")


def preparar_markdown(texto, pid):
    # Faixas-imagem do README voltam a ser títulos: no HTML a letra é real.
    texto = re.sub(
        r'<a id="[^"]*"></a>\n<img src="graficos/cabecalhos/[^"]+" alt="([^"]+)"[^>]*>',
        lambda m: "## " + m.group(1), texto)
    # A capa repete o título do cabeçalho do site.
    texto = re.sub(r'<p align="center">\s*<img src="graficos/00_capa.png"[^>]*>\s*</p>\s*',
                   "", texto)
    # Emblemas do GitHub (shields.io) não fazem falta no HTML.
    texto = re.sub(r'<p align="center">\s*<img src="https://img.shields.io.*?</p>\s*', "", texto, flags=re.S)
    # O mermaid passa a ser renderizado no browser.
    texto = re.sub(r"```mermaid\n(.*?)```",
                   lambda m: f'<pre class="mermaid">{html.escape(m.group(1))}</pre>',
                   texto, flags=re.S)
    return texto


def pos_html(corpo, pid):
    # Imagens embutidas.
    def img(m):
        caminho = RAIZ / m.group(1)
        if caminho.exists():
            return f'src="data:image/png;base64,{b64(caminho)}"'
        return m.group(0)
    corpo = re.sub(r'src="(graficos/[^"]+\.png)"', img, corpo)

    # Ligações entre documentos passam a mudar de separador.
    def ligacao(m):
        ficheiro, ancora = m.group(1), m.group(2) or ""
        if ficheiro in PAGINA_DE:
            return f'href="@{PAGINA_DE[ficheiro]}{":" + ancora[1:] if ancora else ""}"'
        return f'href="{ficheiro}{ancora}" target="_blank" rel="noopener"'
    corpo = re.sub(r'href="([^"#:]+\.(?:md|sql|db|py|csv))(#[^"]*)?"', ligacao, corpo)

    # Âncoras internas ficam prefixadas com o separador.
    corpo = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{pid}:{m.group(1)}"', corpo)
    corpo = corpo.replace('href="@', 'href="#')
    corpo = re.sub(r'id="([^"]+)"', lambda m: f'id="{pid}:{m.group(1)}"', corpo)
    corpo = corpo.replace('href="http', 'target="_blank" rel="noopener" href="http')
    corpo = re.sub(r"<table>", '<div class="tabela"><table>', corpo)
    corpo = corpo.replace("</table>", "</table></div>")
    return corpo


def consultas():
    texto = (RAIZ / "sql" / "04_analises.sql").read_text(encoding="utf-8")
    lista = []
    for bloco in re.split(r"^-- @q ", texto, flags=re.M)[1:]:
        titulo, _, corpo = bloco.partition("\n")
        lista.append({"titulo": titulo.strip(), "sql": corpo.strip()})
    return lista


def main(publicar=None):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                           extension_configs={"toc": {"slugify": slug_github}})
    paginas = []
    for pid, nome, ficheiro in DOCUMENTOS:
        texto = preparar_markdown((RAIZ / ficheiro).read_text(encoding="utf-8"), pid)
        corpo = pos_html(md.reset().convert(texto), pid)
        paginas.append(f'<article class="pagina" id="p-{pid}" data-pagina="{pid}">{corpo}</article>')

    abas = "".join(f'<a href="#{pid}" data-aba="{pid}">{nome}</a>' for pid, nome, _ in DOCUMENTOS)
    abas += '<a href="#sql" data-aba="sql">Consola SQL</a>'

    modelo = (RAIZ / "scripts" / "modelo.html").read_text(encoding="utf-8")
    saida = (modelo
             .replace("{{FONTE_TITULO}}", b64(RAIZ / "fontes" / "ArchivoExpanded-ExtraBold.ttf"))
             .replace("{{FONTE_TEXTO}}", b64(RAIZ / "fontes" / "Archivo-Regular.ttf"))
             .replace("{{FONTE_NEGRITO}}", b64(RAIZ / "fontes" / "Archivo-Bold.ttf"))
             .replace("{{ABAS}}", abas)
             .replace("{{PAGINAS}}", "\n".join(paginas))
             .replace("{{DB}}", b64(RAIZ / "vsc_contas.db"))
             .replace("{{CONSULTAS}}", json.dumps(consultas(), ensure_ascii=False).replace("</", "<\\/")))
    sqljs = (VENDOR / "sql-wasm.js").read_text(encoding="utf-8")
    saida = (saida.replace("{{WASM}}", b64(VENDOR / "sql-wasm.wasm"))
                  .replace("{{SQLJS}}", lambda_safe(sqljs)))
    ficheiro = (saida.replace("{{MERMAID}}", "true")
                     .replace("{{BOTAO_CSV}}", '<button id="csv" class="secundario">Descarregar CSV</button>'))
    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_text(ficheiro, encoding="utf-8")
    print(f"Gravado {SAIDA.relative_to(RAIZ)} ({SAIDA.stat().st_size / 1e6:.1f} MB)")

    if publicar:
        pagina = saida.replace("{{MERMAID}}", "false").replace("{{BOTAO_CSV}}", "")
        cabeca = re.search(r"<head>(.*?)</head>", pagina, re.S).group(1)
        corpo = re.search(r"<body>(.*?)</body>", pagina, re.S).group(1)
        cabeca = re.sub(r'<meta (charset|name="viewport")[^>]*>\n?', "", cabeca)
        Path(publicar).write_text(cabeca.strip() + "\n" + corpo.strip() + "\n", encoding="utf-8")
        print(f"Gravada a variante para publicar em {publicar}")


def lambda_safe(js):
    """Evita que um '</script' dentro da biblioteca feche a etiqueta."""
    return js.replace("</script", "<\\/script")


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    main(args[args.index("--publicar") + 1] if "--publicar" in args else None)
