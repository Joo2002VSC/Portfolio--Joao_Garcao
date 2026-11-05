# Livros

Pasta dos livros a processar: ficheiros `.txt` (UTF-8, Windows-1252 ou Latin-1) ou `.epub`, em português, francês ou inglês.

- O nome do ficheiro dá o identificador do livro nos resultados (`autor-titulo.txt` → `resultados/livros/autor-titulo/`).
- `metadados.csv` completa ou corrige os metadados extraídos do ficheiro. Colunas: `ficheiro`, `titulo`, `autor`, `ano`, `lingua` (`pt`, `fr` ou `en`, para forçar a língua). Só é preciso preencher o que falta.
- Retirar um livro desta pasta apaga os seus resultados no processamento seguinte.

Livros de exemplo (domínio público):

| Ficheiro | Fonte |
| --- | --- |
| `eca-de-queiros-os-maias.txt` | Project Gutenberg, eBook n.º 40409 |
| `carroll-alice.txt` | Project Gutenberg, através do corpus NLTK |
