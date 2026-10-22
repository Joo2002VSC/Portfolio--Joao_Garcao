**Relatório: Pré-Processamento e Representação de Texto**

**Projeto:** Chatbot de Apoio baseado no ICVS Onboarding Manual\
**Unidade Curricular:** Introdução à Inteligência Artificial\
**Ano letivo:** 2025/2026\
**Autores:** Grupo 10 (Ana Maciel, Eduarda Veloso, João Garção e Michel
Gonçalves)

**1. Introdução**

O objetivo desta primeira etapa foi desenvolver um pipeline de
pré-processamento textual aplicado ao *ICVS Onboarding Manual*, um
documento institucional utilizado para orientar novos estudantes,
investigadores e colaboradores do Instituto de Investigação em Ciências
da Vida e da Saúde (ICVS).

A motivação do projeto assenta na criação de um chatbot informativo
capaz de responder a questões comuns sobre a integração na instituição,
como procedimentos administrativos, estruturas internas, normas de
funcionamento, apoio aos estudantes e recursos disponíveis.

Assim, esta fase focou-se na limpeza, normalização e representação
vetorial do texto, preparando uma base sólida para extração de
conhecimento e desenvolvimento do futuro agente conversacional.

**2. Decisões e Justificações**

**2.1. Fonte e Estrutura do Dataset**

O documento original foi fornecido em formato .docx e convertido para
.txt através da biblioteca **python-docx**. Esta conversão permitiu
extrair apenas o conteúdo textual, eliminando formatação irrelevante.

De seguida, foi criado um script que segmentou o texto em parágrafos e
identificou automaticamente as secções do documento (ex.: *Welcome
Message*, *Introduction*, *Research Groups*, *Administrative
Procedures*).\
Para isso, utilizámos regras simples de deteção de headings (maiúsculas,
títulos curtos, padrões linguísticos).

**Decisão:**\
→ Cada parágrafo foi associado à sua secção correspondente, criando um
dataset estruturado com 197 entradas.\
Este formato:

-   mantém contexto sem ser demasiado extenso,

-   facilita futuras operações de similaridade e TF-IDF,

-   é ideal para um chatbot baseado em recuperação textual
    (*retrieval-based*).

**3. Pipeline de Pré-Processamento**

**3.1. Importação e Limpeza de Dados**

Foram utilizadas as bibliotecas:\
pandas, re, nltk, scikit-learn, wordcloud, matplotlib.

O texto foi uniformizado para **minúsculas**, com remoção de
**pontuação, números e múltiplos espaços**, mantendo apenas caracteres
alfabéticos.\
Essa limpeza assegura que os vetores gerados representem apenas
informação linguística relevante.

*def clean_text(text):*

*text = text.lower()*

*text = re.sub(r\'\[\^a-z\\s\]\', \'\', text)*

*text = re.sub(r\'\\s+\', \' \', text).strip()*

*return text*

**3.2. Tokenização e Lematização**

Para normalizar o vocabulário, aplicou-se **tokenização** e
**lematização** com nltk.WordNetLemmatizer.\
Cada parágrafo foi decomposto em tokens e convertido para a forma base
(ex.: "students" → "student")\
A função implementada tokeniza, lematiza e ignora tokens inválidos ou
demasiado curtos, assegurando consistência no dataset.

*Decisão:* A lematização foi escolhida em vez de stemming para preservar
significado semântico, essencial num texto institucional --- onde
pequenas diferenças morfológicas podem alterar o sentido.

**3.3. Remoção de Stopwords**

Foram removidas stopwords da língua inglesa (ex.: *the, and, with*).\
Esta etapa filtra palavras que aparecem frequentemente mas não
contribuem para análise semântica.

Após esta filtragem, surgiram tokens mais significativos como:\
*research, laboratory, safety, student, procedure, group, equipment,
support*.

**Justificação:**\
→ A remoção de stopwords melhora a qualidade das features e reduz
dimensionalidade.

**3.4. Representação Vetorial (Bag of Words e TF-IDF)**

Foram utilizadas duas formas de representação textual:

-   **Bag of Words (BoW):** converte o texto em vetores de contagem de
    palavras.\
    Útil para análises de frequência e visualizações iniciais.

-   **TF-IDF (Term Frequency--Inverse Document Frequency):** atribui
    pesos às palavras conforme sua relevância no corpus.\
    Essencial para calcular similaridades e responder perguntas mais
    tarde.

Ambos os modelos foram limitados a **1000 features** para equilibrar
desempenho e interpretabilidade.

*Decisão:* O TF-IDF será a representação principal para o sistema de
recuperação de informação, dado que ajuda o chatbot a selecionar os
parágrafos mais relevantes para cada pergunta.

**4. Exploração Visual**

Foram geradas visualizações através de **wordcloud** e gráficos de
frequência.

As palavras mais recorrentes incluíram:\
*icvs, research, group, student, support, laboratory, training, safety*.

Estas distribuições confirmam a natureza institucional do documento e
validam a eficácia do processo de limpeza. A wordcloud mostrou clusters
semânticos coerentes, refletindo as secções principais do manual.

**5. Resultados e Conclusões**

O pipeline resultou nos seguintes ficheiros processados:

1.  **dataset_processado.csv** --- texto limpo, tokenizado, lematizado e
    sem stopwords

2.  **icvs_bow.csv** --- matriz Bag-of-Words

3.  **icvs_tfidf.csv** --- matriz TF-IDF com 1000 features

**Conclusões principais:**

-   O corpus é rico e bem distribuído entre temas relevantes para o
    onboarding.

-   A granularidade por parágrafos mostrou-se adequada, preservando
    contexto sem redundância.

-   A limpeza e normalização prepararam eficazmente o texto para as
    fases seguintes (NER, knowledge graph e chatbot).

-   O uso de TF-IDF permite recuperar com precisão o conteúdo mais
    relevante em resposta a perguntas do utilizador.

O dataset final encontra-se pronto para avançar para as etapas de
extração de conhecimento e criação do sistema de QA.
