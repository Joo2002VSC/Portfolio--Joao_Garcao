# Relatório: Desenvolvimento do Chatbot CLI

**Projeto:** Chatbot de Apoio baseado no ICVS Onboarding Manual  
**Unidade Curricular:** Introdução à Inteligência Artificial  
**Ano letivo:** 2025/2026  
**Autores:** Grupo 10 (Ana Maciel, Eduarda Veloso, João Garção e Michel Gonçalves)

## 1. Introdução

Esta fase focou na criação de um chatbot interativo via linha de comando (CLI), integrando o sistema RAG desenvolvido na Etapa III. O objetivo foi transformar o protótipo em uma ferramenta prática e demonstrável, permitindo interações conversacionais em tempo real para consultas institucionais.

A motivação é fornecer uma interface acessível para usuários finais, validando a aplicabilidade do RAG em cenários reais de suporte.

## 2. Decisões e Justificações

### 2.1. Estrutura Modular
- Módulos: `retrieval.py` (recuperação), `RAG.py` (geração), `config.py` (configurações).
- Script principal: `fim.py` para loop interativo.

**Decisão:**  
→ Separação de responsabilidades facilita depuração e reutilização.

### 2.2. Modelo e Otimizações
- Modelo: Phi para eficiência e menor propensão a alucinações.
- Prompts: Conversacionais, com regras contra invenções.
- Dataset: CSV básico para confiabilidade.

**Justificação:**  
→ Foco em estabilidade para demo; ajustes baseados em testes de alucinações.

## 3. Pipeline de Desenvolvimento

### 3.1. Integração de Componentes
- Importação de módulos no `fim.py`.
- Loop para entrada de perguntas e saída de respostas.
- Tratamento de erros (ex.: perguntas vazias, falhas de modelo).

### 3.2. Testes e Refinamentos
- Execução com perguntas variadas.
- Ajustes: Prompts para naturalidade; reversão de integrações problemáticas.

## 4. Exploração e Validação
- Testes interativos: Respostas diretas e conversacionais.
- Validação: Aderência ao contexto; redução de erros.

## 5. Resultados e Conclusões

Resultou em CLI funcional, com chatbot responsivo.

**Conclusões:**  
CLI demonstra viabilidade do sistema; pronto para apresentação. Limitações em complexidade; expansível.