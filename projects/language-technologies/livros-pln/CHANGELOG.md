# Alterações

## 1.0.0 · 2026-11-05

Primeira versão.

- Leitura de TXT (com metadados do Project Gutenberg) e EPUB (metadados Dublin Core); metadados manuais em `livros/metadados.csv`.
- Deteção automática de português, francês e inglês.
- Indicadores de dimensão, léxico, sintaxe, legibilidade, classes gramaticais, pontuação, entidades, frequências e evolução ao longo do livro, calculados com spaCy e pandas.
- Gráficos por livro e de comparação entre livros; relatórios em Markdown.
- Cache por livro e por versão do código.
- Workflow do GitHub Actions que testa, reprocessa e publica os resultados quando o código muda.
