# 📖 O Meu Blog Literário

Blog pessoal onde registo e comento os livros que leio — uma recensão por mês, autores e obras favoritas, a lista completa de leituras e uma página de estatísticas.

🔗 **Site:** https://joo2002vsc.github.io/Portfolio--Joao_Garcao/projects/web-development/blog-literario/

Projeto pessoal e autodidata (não foi feito para nenhuma cadeira), em **HTML, CSS e JavaScript** sem frameworks, publicado com **GitHub Pages**.

## Páginas

- **Início** — destaques e recensões mensais de 2026 (janeiro a dezembro)
- **Todas as leituras** — a lista completa dos livros lidos
- **Em números** — estatísticas de leitura
- **Autores** e **Obras** favoritas
- **Sobre** o blog

## Em Números (análise SQL)

A página **Em Números** e a lista **Todas as Leituras** são geradas a partir da exportação do Goodreads (`assets/goodreads_library_export.csv`) com consultas **SQLite**. O código da análise está em [`data-analysis/leituras-sql`](https://github.com/Joo2002VSC/Portfolio--Joao_Garcao/tree/main/projects/data-analysis/leituras-sql).

## Estrutura

```
├── index.html, janeiro.html … dezembro.html   # páginas
├── leituras.html, estatisticas.html, autores.html, obras.html, sobre.html
├── style.css, leituras.css, estatisticas.css
├── script.js
├── estatisticas.js  # gráficos da página Em Números
├── assets/          # capas, fotos de autores, logótipo
│   ├── goodreads_library_export.csv
│   └── dados/       # estatisticas.js e leituras.js (gerados por SQL)
└── analise-sql/     # análise SQL (no Portfolio: data-analysis/leituras-sql)
```
