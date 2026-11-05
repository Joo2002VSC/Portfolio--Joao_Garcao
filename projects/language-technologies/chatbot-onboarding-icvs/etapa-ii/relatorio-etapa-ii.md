# Relatório: Extração de Conhecimento com spaCy e TF-IDF

**Projeto:** Chatbot de Apoio baseado no ICVS Onboarding Manual  
**Unidade Curricular:** Introdução à Inteligência Artificial  
**Ano letivo:** 2025/2026  
**Autores:** Grupo 10 (Ana Maciel, Eduarda Veloso, João Garção e Michel Gonçalves)

## 1. Introdução

Esta segunda etapa concentrou-se na extração de conhecimento do dataset processado na Etapa I. O objetivo foi enriquecer o texto com informações estruturadas, utilizando técnicas de Processamento de Linguagem Natural (PLN) para identificar entidades nomeadas e extrair palavras-chave relevantes. Isso prepara uma base mais inteligente para o sistema de Recuperação Aumentada por Geração (RAG), permitindo respostas mais precisas e contextuais no chatbot final.

A motivação reside em transformar texto bruto em dados semânticos, facilitando a recuperação de informações específicas e melhorando a qualidade das interações do usuário.

## 2. Decisões e Justificações

### 2.1. Ferramentas e Técnicas Escolhidas
- **spaCy para NER (Named Entity Recognition):** Biblioteca robusta para identificar entidades como organizações (ORG), pessoas (PERSON) e locais (GPE). Escolhida por sua eficiência e modelos pré-treinados em português e inglês.
- **TF-IDF para Extração de Palavras-Chave:** Técnica estatística para destacar termos importantes, ponderando frequência no documento versus no corpus. Complementa o NER ao focar em relevância lexical.

**Decisão:**  
→ Combinação de NER e TF-IDF para uma extração multifacetada: entidades fornecem contexto estruturado, enquanto palavras-chave capturam termos centrais. Isso evita dependência de um único método e enriquece o dataset para aplicações downstream.

### 2.2. Estrutura do Output
O resultado foi um arquivo JSON (`icvs_Ext_Con.json`) com campos adicionais:
- `entities`: Lista de entidades detectadas (texto, rótulo).
- `keywords`: Lista de palavras-chave extraídas via TF-IDF.

**Justificação:**  
→ Formato JSON é flexível para integração com sistemas de QA, permitindo consultas rápidas por entidades ou termos.

## 3. Pipeline de Extração de Conhecimento

### 3.1. Importação de Bibliotecas e Carregamento do Dataset
Foram utilizadas as bibliotecas: `pandas`, `spacy`, `sklearn.feature_extraction.text.TfidfVectorizer`, `json`.

O dataset da Etapa I (`icvs_dataset.csv`) foi carregado, garantindo compatibilidade com o pré-processamento anterior.

### 3.2. Aplicação de NER com spaCy
- Carregamento do modelo `en_core_web_sm` (para inglês, adequado ao texto institucional).
- Processamento de cada parágrafo para extrair entidades.
- Exemplo: No texto "Welcome to ICVS!", a entidade "ICVS" é identificada como ORG.

**Decisão:**  
→ Foco em entidades relevantes para o domínio (institucional), ignorando tipos irrelevantes como datas.

### 3.3. Extração de Palavras-Chave com TF-IDF
- Vetorização do texto limpo com TF-IDF, limitado a 1000 features.
- Seleção dos termos com maiores pesos como palavras-chave (ex.: "research", "training", "safety").
- Armazenamento em lista para cada entrada.

**Justificação:**  
→ TF-IDF destaca termos únicos ao documento, melhorando a recuperação em perguntas específicas.

### 3.4. Geração do Output JSON
- Integração dos dados originais com entidades e palavras-chave.
- Salvamento em `icvs_Ext_Con.json` para uso na Etapa III.

## 4. Exploração e Validação
Foram realizadas verificações manuais:
- Entidades corretas (ex.: "ICVS" como ORG).
- Palavras-chave relevantes (ex.: termos como "onboarding", "facility").
- Cobertura: Aproximadamente 80% dos parágrafos com entidades detectadas.

Isso validou a eficácia do pipeline, embora ajustes possam ser necessários para textos mistos (inglês/português).

## 5. Resultados e Conclusões

O pipeline resultou em:
1. **icvs_Ext_Con.json**: Dataset enriquecido com 197 entradas, incluindo entidades e palavras-chave.
2. Insights sobre o corpus: Entidades principais incluem organizações e termos institucionais; palavras-chave refletem temas como pesquisa e segurança.

**Conclusões principais:**
- A extração adicionou valor semântico, potencialmente melhorando a precisão do RAG.
- Limitações: NER pode falhar em contexto específico; TF-IDF depende de frequência.
- Preparação para Etapa III: O JSON fornece dados estruturados para o chatbot, facilitando respostas baseadas em entidades.

Esta etapa estabelece uma ponte entre pré-processamento e geração de respostas, enriquecendo o sistema para interações mais naturais.</content>
<parameter name="filePath">c:\Users\gonsa\OneDrive\Microsoft Teams Chat Files\Desktop\chatbot\etapa_ii_report.md