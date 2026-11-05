# Observatório BLCS

Dashboard de perfil e utilização da Biblioteca Lúcio Craveiro da Silva (BLCS), 2020–2026, desenvolvida no âmbito do Trabalho de Projeto do Mestrado em Humanidades Digitais da Universidade do Minho.

🇵🇹 [Português](#-português) · 🇬🇧 [English](#-english)

**[Abrir a dashboard ↗](https://joo2002vsc.github.io/Portfolio--Joao_Garcao/projects/digital-humanities/observatorio-blcs/)** · **[Relatório de projeto (PDF)](./Relatorio_de_Projeto_MHD_Joao_Garcao.pdf)**

---

## 🇵🇹 Português

### Contexto e objetivo

A BLCS produz dados administrativos e estatísticos sobre leitores, circulação, inscrições e frequência presencial, mas essa informação está dispersa por ficheiros de anos, estruturas e granularidades diferentes. O projeto teve como objetivo conceber uma dashboard interativa que integre e visualize indicadores selecionados para o período 2020–2026 (2026 parcial, até julho) e validá-la com profissionais da Biblioteca.

- **Relatório:** *Análise de Dados e Intervenção Digital: O Caso da Biblioteca Lúcio Craveiro da Silva* (outubro de 2026)
- **Orientação:** Professora Doutora Sílvia Araújo

### Conteúdo da dashboard

| Secção | O que mostra |
| --- | --- |
| Visão Geral | Evolução de entradas e empréstimos, utentes ativos por categoria, qualidade dos dados |
| Leitores | Novas inscrições, contas ativas, peso de cada categoria, comparação entre anos e com a Rede Nacional e Braga |
| Circulação | Sazonalidade, rácios operacionais, empréstimos por estação, período letivo, dia da semana e hora |
| Coleções e Procura | Áreas temáticas, títulos mais requisitados, tipo de coleção, concentração da procura |
| Sobre a Biblioteca | Apresentação da BLCS, atividades, marcos, espaços e coleções |

### Metodologia

O trabalho segue a *Design Science Research Methodology* (Peffers et al., 2007): auditoria e harmonização dos dados, análise exploratória, desenvolvimento da dashboard e validação formativa com cinco profissionais da BLCS. A metodologia completa, os resultados e as limitações estão nos capítulos 4 a 6 do relatório.

### Dados

- 18 ficheiros cedidos pela BLCS, exportados do Koha e dos Mapas de Entradas (Excel), tratados sempre em cópia.
- Os dados institucionais **não estão incluídos** neste repositório; a dashboard contém os indicadores processados, embebidos em JSON.

### Tecnologias

- Dashboard: página HTML única e autocontida (HTML, CSS e JavaScript), com gráficos em SVG e sem bibliotecas externas de visualização.
- Tratamento de dados: Python (pandas, openpyxl, xlrd).
- Testes: Playwright com Chromium; acessibilidade com Lighthouse e axe-core.

### Estrutura

```text
observatorio-blcs/
├── index.html                                  dashboard
├── Relatorio_de_Projeto_MHD_Joao_Garcao.pdf    relatório académico
└── README.md
```

Os scripts de tratamento de dados não estão incluídos neste repositório.

### Execução

Não requer instalação: basta abrir `index.html` num navegador ou usar a versão publicada.

---

## 🇬🇧 English

Interactive dashboard on the profile and use of the Lúcio Craveiro da Silva Library (BLCS), University of Minho, 2020–2026: readers, circulation, collections and demand. It was developed for the project work of the Master's in Digital Humanities (University of Minho), supervised by Prof. Sílvia Araújo, following the Design Science Research Methodology, with formative validation by five library professionals.

The dashboard is a single self-contained HTML page (HTML, CSS and JavaScript, SVG charts, no external visualisation libraries). Data were processed in Python (pandas, openpyxl, xlrd). The institutional source files are not included in this repository. Full methodology, results and limitations are in the [project report (PDF, in Portuguese)](./Relatorio_de_Projeto_MHD_Joao_Garcao.pdf).

The copyright and licensing terms below apply (in Portuguese): the dashboard and its source code are © João Garção, all rights reserved; the academic report is licensed under CC BY 4.0; BLCS data and materials remain subject to their own terms.

---

## Direitos de autor e propriedade intelectual

© 2026 João Garção. Todos os direitos reservados.

O desenvolvimento, a estrutura, o código-fonte, a organização visual e as funcionalidades da dashboard Observatório BLCS constituem uma criação intelectual desenvolvida por João Garção no âmbito do projeto académico de Mestrado em Humanidades Digitais da Universidade do Minho.

Salvo indicação expressa em contrário, os direitos de autor relativos aos elementos originais desenvolvidos neste projeto encontram-se reservados ao respetivo autor.

A disponibilização pública deste repositório destina-se à demonstração, consulta e documentação do projeto. Não constitui, por si só, uma concessão de licença para reprodução, redistribuição, modificação ou exploração comercial do código-fonte.

O relatório académico associado a este projeto é disponibilizado sob licença Creative Commons Atribuição 4.0 Internacional (CC BY 4.0). Esta reserva de direitos aplica-se ao código-fonte e à dashboard, não ao relatório.

Os dados institucionais, documentos, designações, logótipos e outros materiais pertencentes à Biblioteca Lúcio Craveiro da Silva ou a terceiros permanecem sujeitos aos respetivos direitos e condições de utilização.

A utilização de componentes, bibliotecas, fontes ou outros recursos de terceiros encontra-se sujeita às respetivas licenças e condições de utilização.

Para pedidos de autorização relativos à utilização, adaptação ou redistribuição dos elementos originais deste projeto, deverá ser obtido consentimento prévio do respetivo titular dos direitos.

**Contacto:** joaogarcao2002@gmail.com
