# Chatbot de Onboarding ICVS (RAG)

## 🇵🇹
Chatbot institucional desenvolvido para a cadeira de **Introdução à Inteligência Artificial** (Mestrado em Inteligência Artificial, Universidade do Minho), em grupo com **Ana Maciel**, **Eduarda Veloso** e **Michel Gonçalves** (Grupo 10).

O objetivo foi criar um agente conversacional, baseado em **RAG** (*Retrieval-Augmented Generation*), capaz de responder a perguntas sobre procedimentos administrativos, estruturas internas e recursos do Instituto de Investigação em Ciências da Vida e da Saúde (ICVS), com base no manual de onboarding da instituição.

O desenvolvimento seguiu três etapas, documentadas em relatórios próprios:

- **[`etapa-i/`](./etapa-i)**: pré-processamento textual do manual institucional — limpeza, tokenização, lematização e remoção de *stopwords* (NLTK), com representação vetorial via TF-IDF, gerando um dataset estruturado de 197 entradas.
- **[`etapa-ii/`](./etapa-ii)**: extração de conhecimento — reconhecimento de entidades nomeadas (NER, com spaCy) e extração de palavras-chave (TF-IDF), enriquecendo o dataset com metadados semânticos.
- **[`etapa-iii/`](./etapa-iii)**: implementação e avaliação do sistema RAG — recuperação de contexto via TF-IDF combinada com geração de respostas por um modelo de linguagem local (Ollama, modelos Phi/Llama3.2), testado com perguntas reais.
- **[`cli/`](./cli)**: interface de linha de comando que integra o sistema RAG, permitindo interação conversacional em tempo real.

📄 [`relatorio-final.pdf`](./relatorio-final.pdf) — relatório final completo (problema, motivação, arquitetura, demonstração de resultados e discussão crítica)

*Nota: o manual institucional original (fonte dos dados) não é reproduzido aqui, por se tratar de documentação interna do ICVS.*

Trabalho em grupo.

---

## 🇬🇧
Institutional chatbot developed for the **Introduction to Artificial Intelligence** course (Master's in Artificial Intelligence, University of Minho), group work with **Ana Maciel**, **Eduarda Veloso**, and **Michel Gonçalves** (Group 10).

The goal was to build a conversational agent based on **RAG** (Retrieval-Augmented Generation), able to answer questions about administrative procedures, internal structures, and resources of the Institute for Research in Life and Health Sciences (ICVS), grounded in the institution's onboarding manual.

Development followed three stages, each documented in its own report:

- **[`etapa-i/`](./etapa-i)**: text preprocessing of the institutional manual — cleaning, tokenization, lemmatization, and stopword removal (NLTK), with vector representation via TF-IDF, producing a structured dataset of 197 entries.
- **[`etapa-ii/`](./etapa-ii)**: knowledge extraction — named entity recognition (NER, with spaCy) and keyword extraction (TF-IDF), enriching the dataset with semantic metadata.
- **[`etapa-iii/`](./etapa-iii)**: RAG system implementation and evaluation — TF-IDF context retrieval combined with response generation via a local language model (Ollama, Phi/Llama3.2 models), tested with real questions.
- **[`cli/`](./cli)**: command-line interface integrating the RAG system, enabling real-time conversational interaction.

📄 [`relatorio-final.pdf`](./relatorio-final.pdf) — full final report (problem, motivation, architecture, results demonstration, and critical discussion)

*Note: the original institutional manual (data source) is not reproduced here, as it is internal ICVS documentation.*

Group project.
