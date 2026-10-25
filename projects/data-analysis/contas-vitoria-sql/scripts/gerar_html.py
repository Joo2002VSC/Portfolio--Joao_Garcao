"""Gera uma versão HTML autónoma do projeto: html/contas-vitoria.html.

Junta num só ficheiro o README, as três análises, os gráficos, a letra
Archivo, a base de dados e o SQLite (sql.js, em scripts/vendor), com uma
consola para correr as consultas SQL no browser. Basta abrir o ficheiro com
duplo clique; só o diagrama do modelo de dados precisa de internet.

Com --publicar, grava também uma variante sem <html>/<head> e sem descarga
de CSV, pronta a publicar como página (o caminho vai como argumento).

Com --site, grava também a pasta site/ com o projeto em ficheiros separados
(index.html, css/style.css, js/app.js, imagens e letras), para abrir e editar
no Visual Studio Code.

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
    ("testes", "Testes", "testes.md"),
    ("dicionario", "Dicionário de dados", "dicionario-dados.md"),
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


def pos_html(corpo, pid, embutir=True):
    # Imagens embutidas (ficheiro único) ou com caminho relativo (site/).
    def img(m):
        caminho = RAIZ / m.group(1)
        if not caminho.exists():
            return m.group(0)
        if embutir:
            return f'src="data:image/png;base64,{b64(caminho)}"'
        return f'src="img/{caminho.name}" loading="lazy"'
    corpo = re.sub(r'src="(graficos/[^"]+\.png)"', img, corpo)

    # Ligações entre documentos passam a mudar de separador.
    def ligacao(m):
        ficheiro, ancora = m.group(1), m.group(2) or ""
        if ficheiro in PAGINA_DE:
            return f'href="@{PAGINA_DE[ficheiro]}{":" + ancora[1:] if ancora else ""}"'
        return f'href="../{ficheiro}{ancora}" target="_blank" rel="noopener"'
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


def gerar_paginas(embutir=True):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                           extension_configs={"toc": {"slugify": slug_github}})
    paginas = []
    for pid, nome, ficheiro in DOCUMENTOS:
        texto = preparar_markdown((RAIZ / ficheiro).read_text(encoding="utf-8"), pid)
        corpo = pos_html(md.reset().convert(texto), pid, embutir)
        paginas.append(f'<article class="pagina" id="p-{pid}" data-pagina="{pid}">\n{corpo}\n</article>')
    return paginas


def main(publicar=None, site=False):
    paginas = gerar_paginas()

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


    if site:
        gerar_site(abas)


def gerar_site(abas):
    """Escreve site/: o mesmo projeto em HTML, CSS e JavaScript separados."""
    import shutil
    destino = RAIZ / "site"
    if destino.exists():
        shutil.rmtree(destino)
    for pasta in ("css", "js/vendor", "img", "fontes", ".vscode"):
        (destino / pasta).mkdir(parents=True, exist_ok=True)

    modelo = (RAIZ / "scripts" / "modelo.html").read_text(encoding="utf-8")
    estilo = re.search(r"<style>\n(.*?)</style>", modelo, re.S).group(1)
    estilo = (estilo
              .replace("url(data:font/ttf;base64,{{FONTE_TITULO}})", 'url("../fontes/ArchivoExpanded-ExtraBold.ttf")')
              .replace("url(data:font/ttf;base64,{{FONTE_TEXTO}})", 'url("../fontes/Archivo-Regular.ttf")')
              .replace("url(data:font/ttf;base64,{{FONTE_NEGRITO}})", 'url("../fontes/Archivo-Bold.ttf")'))
    (destino / "css" / "style.css").write_text(
        "/* As contas do Vitória SC · estilos\n"
        "   Paleta dos documentos financeiros do clube e letra Archivo (pasta fontes/). */\n\n"
        + estilo, encoding="utf-8")

    script = re.search(r'const DB_B64 = "\{\{DB\}\}";\n(.*?)</script>', modelo, re.S).group(1)
    (destino / "js" / "app.js").write_text(
        "// As contas do Vitória SC · separadores, diagrama e consola SQL.\n"
        "// Usa as constantes de js/dados.js e a biblioteca sql.js (js/vendor/).\n"
        + script.strip() + "\n", encoding="utf-8")
    (destino / "js" / "dados.js").write_text(
        "// Gerado por scripts/gerar_html.py: não editar à mão.\n"
        "// A base de dados e o motor SQLite vão em texto (base64) para a consola\n"
        "// funcionar mesmo abrindo index.html diretamente, sem servidor.\n"
        "const CARREGAR_MERMAID = true;\n"
        f"const CONSULTAS = {json.dumps(consultas(), ensure_ascii=False, indent=1)};\n"
        f'const DB_B64 = "{b64(RAIZ / "vsc_contas.db")}";\n'
        f'const WASM_B64 = "{b64(VENDOR / "sql-wasm.wasm")}";\n', encoding="utf-8")
    shutil.copy(VENDOR / "sql-wasm.js", destino / "js" / "vendor" / "sql-wasm.js")
    shutil.copy(VENDOR / "sql.js-LICENSE", destino / "js" / "vendor" / "sql.js-LICENSE")
    for png in (RAIZ / "graficos").glob("*.png"):
        shutil.copy(png, destino / "img" / png.name)
    for f in (RAIZ / "fontes").iterdir():
        shutil.copy(f, destino / "fontes" / f.name)

    corpo = re.search(r"<body>\n(.*?)<script>", modelo, re.S).group(1)
    corpo = (corpo.replace("{{ABAS}}", abas)
                  .replace("{{PAGINAS}}", "\n".join(gerar_paginas(embutir=False)))
                  .replace("{{BOTAO_CSV}}", '<button id="csv" class="secundario">Descarregar CSV</button>'))
    corpo = corpo.replace(
        "A base de dados <code>vsc_contas.db</code> e o SQLite",
        "A base de dados <code>vsc_contas.db</code> (em <code>js/dados.js</code>) e o SQLite")
    cabeca = re.search(r"<head>\n(.*?)<style>", modelo, re.S).group(1)
    cabeca = cabeca.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    (destino / "index.html").write_text(
        "<!doctype html>\n<html lang=\"pt\">\n<head>\n" + cabeca
        + '<link rel="stylesheet" href="css/style.css">\n</head>\n<body>\n' + corpo
        + '<script src="js/vendor/sql-wasm.js"></script>\n'
        + '<script src="js/dados.js"></script>\n'
        + '<script src="js/app.js"></script>\n</body>\n</html>\n', encoding="utf-8")

    (destino / ".vscode" / "extensions.json").write_text(
        '{\n  "recommendations": ["ritwickdey.LiveServer"]\n}\n', encoding="utf-8")
    (destino / ".vscode" / "settings.json").write_text(
        '{\n  "liveServer.settings.root": "/",\n  "files.associations": { "*.html": "html" }\n}\n',
        encoding="utf-8")
    (destino / "LEIA-ME.md").write_text(LEIA_ME, encoding="utf-8")
    total = sum(f.stat().st_size for f in destino.rglob("*") if f.is_file())
    print(f"Gravada a pasta site/ ({total / 1e6:.1f} MB)")


LEIA_ME = """# As contas do Vitória SC · versão web

O projeto em HTML, CSS e JavaScript, em ficheiros separados.

## Abrir no Visual Studio Code

1. No VS Code: **File → Open Folder…** e escolhe esta pasta (`site`).
2. Instala a extensão **Live Server**: no VS Code, abre o separador Extensions (⇧⌘X), procura "Live Server" e clica em Install.
3. Abre `index.html` e clica em **Go Live**, no canto inferior direito.
   A página abre no browser e atualiza sozinha sempre que guardas um ficheiro.

Sem o Live Server também funciona: clica com o botão direito em `index.html`
→ **Reveal in Finder** e abre o ficheiro num browser.

## O que está em cada ficheiro

| Ficheiro | Conteúdo |
|:---|:---|
| `index.html` | Estrutura da página: cabeçalho, separadores, os relatórios e a consola SQL |
| `css/style.css` | Cores, tipografia, tabelas e consola (modo claro e escuro) |
| `js/app.js` | Troca de separadores, diagrama do modelo de dados e consola SQL |
| `js/dados.js` | As 55 consultas, a base de dados e o motor SQLite (gerado, não editar) |
| `js/vendor/sql-wasm.js` | sql.js: SQLite compilado para WebAssembly (licença MIT) |
| `img/` | Gráficos |
| `fontes/` | Archivo e Archivo Expanded (licença OFL) |

## Atualizar

Esta pasta é gerada a partir do projeto. Se mudares os dados, as consultas ou os
relatórios, corre na raiz do projeto:

```bash
python scripts/gerar_html.py --site
```

Mudanças feitas à mão em `css/style.css` ou `js/app.js` perdem-se quando a pasta
é gerada de novo; para as manter, copia-as para `scripts/modelo.html`.
"""


def lambda_safe(js):
    """Evita que um '</script' dentro da biblioteca feche a etiqueta."""
    return js.replace("</script", "<\\/script")


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    main(args[args.index("--publicar") + 1] if "--publicar" in args else None,
         site="--site" in args)
