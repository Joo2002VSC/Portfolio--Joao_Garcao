# livros-pln

**Repositório próprio: [github.com/Joo2002VSC/livros-pln](https://github.com/Joo2002VSC/livros-pln)** · [Resultados](https://github.com/Joo2002VSC/livros-pln/blob/main/resultados/README.md)

🇵🇹 [Português](#-português) · 🇬🇧 [English](#-english)

![Comparação entre livros](https://raw.githubusercontent.com/Joo2002VSC/livros-pln/main/resultados/graficos/comparacao.png)

---

## 🇵🇹 Português

Projeto pessoal em Python que processa livros em TXT ou EPUB, em português, francês ou inglês, e devolve os seus metadados e indicadores essenciais de PLN, com gráficos e relatórios.

| | |
| --- | --- |
| **Entrada** | TXT (incluindo o cabeçalho do Project Gutenberg) e EPUB (metadados Dublin Core) |
| **Língua** | Deteção automática de português, francês e inglês; modelo spaCy de cada língua |
| **Indicadores** | Dimensão, variedade lexical (TTR, MATTR, hapax, K de Yule), densidade lexical, frases e parágrafos, diálogo, legibilidade de Flesch adaptada a cada língua, classes gramaticais, pontuação, entidades (NER), frequências e evolução ao longo do livro |
| **Dados** | spaCy → DataFrame pandas com um token por linha; exportação em CSV, JSON e Markdown |
| **Automação** | GitHub Actions: sempre que o código muda, corre os testes, reprocessa os livros e publica os resultados com um commit automático |
| **Qualidade** | Testes com pytest; cache por livro e por versão do código |

Está num repositório à parte porque os commits automáticos de resultados encheriam o histórico deste portefólio.

**Tecnologias:** Python, spaCy, pandas, matplotlib, EbookLib, BeautifulSoup, pytest, GitHub Actions

---

## 🇬🇧 English

A personal Python project that processes TXT and EPUB books in Portuguese, French or English and returns their metadata and core NLP indicators (lexical variety, sentence structure, language-specific readability, parts of speech, punctuation, named entities, word frequencies and their evolution across the book), with charts and reports built with spaCy and pandas. A GitHub Actions workflow tests the code, reprocesses the books and publishes the results whenever the code changes. It lives in its own repository so that the automatic result commits do not clutter this portfolio's history.

---

**Direitos:** todos os direitos reservados aos autores indicados neste documento, salvo indicação em contrário. Ver [LICENSE.md](../../../LICENSE.md).  
**Rights:** all rights reserved by the authors named in this document, unless stated otherwise. See [LICENSE.md](../../../LICENSE.md).
