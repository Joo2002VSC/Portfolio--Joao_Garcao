# Projeto Definitivo

## 🇵🇹
Versão final do trabalho de AVD, em grupo com **Joana Azevedo** e **Mariana Gomes**: pipeline completo de análise textual e estatística em Python, aplicado a um corpus de três entrevistas (uma por membro do grupo).

- **Extração linguística:** lemas ([`extract_lemmas.py`](./extract_lemmas.py)), sintagmas nominais ([`noun_chunks.py`](./noun_chunks.py), [`extract_noun_chunks.py`](./extract_noun_chunks.py)), colocações ([`collocations.py`](./collocations.py))
- **Análise:** sentimento ([`sentiment_analysis.py`](./sentiment_analysis.py)), riqueza lexical / *type-token ratio* ([`analyze_ttr.py`](./analyze_ttr.py))
- **Visualização:** geração de gráficos ([`generate_graphs.py`](./generate_graphs.py)), com os resultados em [`graficos/`](./graficos)
- **Dados:** corpus das três entrevistas em [`datasets/`](./datasets) e resultados das colocações em [`resultados/`](./resultados)
- **Apresentação final:** [`apresentacao-avd.pptx`](./apresentacao-avd.pptx)

O pipeline é orquestrado por um [`makefile.mk`](./makefile.mk).

Trabalho em grupo.

---

## 🇬🇧
Final version of the AVD project, group work with **Joana Azevedo** and **Mariana Gomes**: full Python pipeline for textual and statistical analysis, applied to a corpus of three interviews (one per group member).

- **Linguistic extraction:** lemmas ([`extract_lemmas.py`](./extract_lemmas.py)), noun chunks ([`noun_chunks.py`](./noun_chunks.py), [`extract_noun_chunks.py`](./extract_noun_chunks.py)), collocations ([`collocations.py`](./collocations.py))
- **Analysis:** sentiment ([`sentiment_analysis.py`](./sentiment_analysis.py)), lexical richness / type-token ratio ([`analyze_ttr.py`](./analyze_ttr.py))
- **Visualization:** chart generation ([`generate_graphs.py`](./generate_graphs.py)), with results in [`graficos/`](./graficos)
- **Data:** the three-interview corpus in [`datasets/`](./datasets) and collocation results in [`resultados/`](./resultados)
- **Final presentation:** [`apresentacao-avd.pptx`](./apresentacao-avd.pptx)

The pipeline is orchestrated by a [`makefile.mk`](./makefile.mk).

Group project.
