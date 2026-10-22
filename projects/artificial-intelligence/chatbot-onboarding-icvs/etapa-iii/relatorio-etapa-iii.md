# Relatório: Desenvolvimento e Avaliação de RAG

**Projeto:** Chatbot de Apoio baseado no ICVS Onboarding Manual  
**Unidade Curricular:** Introdução à Inteligência Artificial  
**Ano letivo:** 2025/2026  
**Autores:** Grupo 10 (Ana Maciel, Eduarda Veloso, João Garção e Michel Gonçalves)

## 1. Introdução

Esta etapa concentrou-se no desenvolvimento de um sistema de Recuperação Aumentada por Geração (RAG) para responder perguntas baseadas no dataset processado. Utilizando o notebook `QA_RAG_hibrido.ipynb`, foram implementados e testados mecanismos de recuperação e geração, avaliando a precisão e naturalidade das respostas.

A motivação é validar a eficácia do RAG em contextos institucionais, preparando uma base sólida para aplicações conversacionais.

## 2. Decisões e Justificações

### 2.1. Arquitetura do RAG
- **Recuperação:** TF-IDF para seleção de parágrafos relevantes.
- **Geração:** Ollama com modelos leves para respostas contextuais.
- **Avaliação:** Comparação TF-IDF puro vs. RAG completo.

**Decisão:**  
→ RAG para combinar recuperação factual com geração natural, evitando respostas genéricas.

### 2.2. Modelo e Parâmetros
- Modelo: Llama3.2:1b ou Phi.
- Temperatura: 0.1 para consistência.
- Prompts: Estruturados para aderência ao contexto.

**Justificação:**  
→ Modelos leves para testes; prompts rigorosos reduzem alucinações.

## 3. Pipeline de Desenvolvimento

### 3.1. Implementação
- Carregamento do dataset.
- Recuperação top-k com TF-IDF.
- Geração com Ollama, incluindo evidências.

### 3.2. Testes e Avaliação
- Perguntas de exemplo (ex.: acesso a instalações, contatos).
- Resultados salvos em JSON para análise.
- Métricas: Aderência ao contexto, qualidade conversacional.

## 4. Exploração e Validação
- Testes manuais revelaram força em perguntas diretas, fraqueza em complexas.
- Validação: Respostas incluem evidências; alucinações mitigadas com ajustes.

## 5. Resultados e Conclusões

Resultou em sistema RAG funcional, com respostas precisas e JSON de avaliações.

**Conclusões:**  
RAG eficaz para QA institucional; prepara para CLI. Limitações em modelos pequenos; potencial para melhoria.</content>
<parameter name="filePath">c:\Users\gonsa\OneDrive\Microsoft Teams Chat Files\Desktop\chatbot\etapa_iii_report.md