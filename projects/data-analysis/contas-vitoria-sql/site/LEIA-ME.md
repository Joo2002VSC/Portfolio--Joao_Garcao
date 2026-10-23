# As contas do Vitória SC · versão web

O projeto em HTML, CSS e JavaScript, em ficheiros separados.

## Abrir no Visual Studio Code

1. No VS Code: **File → Open Folder…** e escolhe esta pasta (`site`).
2. Instala a extensão **Live Server** (o VS Code sugere-a ao abrir a pasta).
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
