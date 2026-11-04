<p align="center"><img src="img/icone.png" alt="" width="72"></p>

# As Contas da Vitória SC SAD · painel de análise financeira

🇵🇹 [Português](#-português) · 🇬🇧 [English](#-english) · 🇫🇷 [Français](#-français)

**[Abrir o painel ↗](https://joo2002vsc.github.io/Portfolio--Joao_Garcao/projects/web-development/dashboard-contas-vitoria/)**

---

## 🇵🇹 Português

Painel interativo sobre as contas da **Vitória Sport Clube – Futebol, SAD** de 2012/13 a 2025/26. É a camada de apresentação do projeto [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql): todos os valores resultam de consultas SQL a uma base de dados SQLite construída com os Relatórios e Contas da SAD.

### Secções

| Secção | Conteúdo |
|:---|:---|
| **Início** | Estrutura acionista (gráficos circulares, antes e depois da operação com a V-Sports); síntese financeira da época em destaque (8 cartões: rendimentos e gastos operacionais, resultado operacional e líquido, passivo, capitais próprios, gastos com pessoal, juros dos financiamentos), leitura da época (evolução face à época anterior, riscos, alertas, alterações estruturais) e selos que distinguem contas publicadas, reexpressas e sujeitas a aprovação, quatro gráficos de evolução e pontos de entrada para as perguntas e as áreas de análise |
| **Receitas** · **Gastos** · **Rentabilidade** · **Endividamento** | Análise por área financeira: composição das vendas (incluindo os direitos de TV) e dos gastos, margens, estrutura financeira, dívida, encargos financeiros e liquidez; cada rácio com o que mede, a fórmula, os dados e as limitações |
| **Futebol** | Evolução da classificação na Liga, gastos e resultados desportivos |
| **Comparação** | Contas de 2024/25 do Vitória, do Braga, do Famalicão e do Gil Vicente, cruzadas com a classificação na Liga: gastos com pessoal por ponto, receitas sem transferências face aos salários, dependência da venda de jogadores e estrutura financeira |
| **Evolução Previsível da Sociedade** | Orçamento de 2026/27 face ao fecho de 2025/26, venda de jogadores prevista face ao histórico, plano de negócios 2026–2031 e incertezas (Relatório e Contas 2025/26); simulações da centralização dos direitos de TV |
| **Soluções** | Ponto de equilíbrio (quanto teria de render a venda de jogadores) e sete propostas para a sustentabilidade financeira da SAD, cada uma com diagnóstico calculado a partir das consultas, medidas, indicadores a acompanhar e prioridade |
| **Consultas SQL** | Explorador das 48 consultas do projeto relativas à SAD e de 6 consultas complementares, agrupadas por tema: objetivo, código com realce de sintaxe e numeração de linhas, técnicas SQL detetadas, resultado ordenável e exportação para CSV |
| **Metodologia e fontes** | Fontes, data de exportação, tratamento, critérios de comparação, limitações, convenções de apresentação e glossário |

### Como funciona

```
contas-vitoria-sql/vsc_contas.db ─┐
contas-vitoria-sql/sql/04_analises.sql ─┼─► scripts/exportar_json.py ─► data/*.json ─► js/ (navegador)
sql/indicadores_dashboard.sql ─┘          (executa as consultas e verifica a coerência)
```

- O painel **não refaz os cálculos**: lê os resultados das consultas. Os indicadores que o projeto SQL não tinha (autonomia e solvabilidade, resultado operacional sem mais-valias, variações com `LAG`, máximos e mínimos com `ROW_NUMBER`) estão em [`sql/indicadores_dashboard.sql`](sql/indicadores_dashboard.sql), com divisões protegidas por `NULLIF`.
- O script de exportação seleciona apenas as consultas sobre as contas da SAD (a lista de exclusões está em `scripts/exportar_json.py`) e **interrompe a geração** se alguma verificação falhar: por exemplo, se ativo − passivo ≠ capitais próprios, ou se os rácios da consulta complementar D1 divergirem da consulta 29.
- JavaScript em módulos ES, sem *frameworks*. O Chart.js 4 está incluído no repositório.

| Ficheiro | Função |
|:---|:---|
| `js/dados.js` | Carregamento e validação dos dados; funções numéricas protegidas contra nulos e divisões por zero |
| `js/formato.js` | Convenções portuguesas: vírgula decimal, espaço nos milhares, parênteses nos valores monetários negativos; rótulos das colunas |
| `js/paineis.js` | Definição de cada visualização (pergunta, consulta, gráfico, conclusão, ficha do indicador) e dados do orçamento e da estrutura acionista (Relatório e Contas) |
| `js/conclusoes.js` | Conclusões automáticas do início, com limiares explícitos |
| `js/graficos.js` · `js/tabelas.js` · `js/explorador.js` · `js/animacoes.js` | Gráficos, tabelas ordenáveis e exportação, explorador SQL, animações |
| `js/app.js` | Estado, filtros (guardados no endereço), navegação e início |

### Acessibilidade e apresentação

- HTML semântico, navegação completa por teclado e ligação para saltar para o conteúdo.
- Cada gráfico tem uma descrição para leitores de ecrã e uma alternativa em tabela.
- Paleta do projeto SQL (preto, amarelo e cinzentos), com verde e vermelho reservados para evolução favorável e desfavorável. A cor nunca é a única indicação.
- Tipografia: Inter (texto, títulos e números, com algarismos tabulares nos indicadores e tabelas) e IBM Plex Mono (código SQL e identificadores das consultas), alojadas na pasta `fontes/` com licença OFL; escala de tamanhos e pesos centralizada em variáveis CSS.
- Segurança: política de segurança de conteúdo (CSP) que só permite recursos do próprio site, com o mapa de importação autorizado por hash; ligações externas com `rel="noopener noreferrer"`; política de referência restrita; dados inseridos no HTML sempre escapados ou como texto.
- Contraste verificado em modo claro e escuro.
- Respeita a opção do sistema para reduzir o movimento.
- Português europeu em toda a interface, com glossário e convenções de apresentação descritas na secção Metodologia.

### Executar localmente

```bash
python -m http.server     # na pasta do painel
# abrir http://localhost:8000
```

Para atualizar os dados depois de alterar a base: `python scripts/exportar_json.py`.

Ao publicar alterações, aumente o número de versão (`?v=22`) com `python3 scripts/versao.py 23` (por exemplo): o script muda a versão no `index.html` e recalcula o hash da política de segurança (CSP), sem o qual o painel não arranca. Atualize também o `?v=` das imagens em `js/app.js`.

### Limitações

- Algumas séries começam mais tarde: transferências desde 2017/18; a demonstração de resultados de 2012/13 só tem o resultado líquido.
- A composição das receitas e dos fornecimentos e serviços externos só está disponível para 2024/25 e 2025/26.
- As simulações da centralização dos direitos de TV são ilustrativas.
- A regressão entre despesas e classificação usa 13 épocas: mostra uma associação, não uma relação de causa e efeito.

---

## 🇬🇧 English

Interactive financial dashboard of Vitória Sport Clube – Futebol, SAD (the club's professional football company), 2012/13–2025/26. Every figure comes from SQL queries run against the SQLite database of my [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql) project: 48 project queries on the SAD plus 6 dashboard queries (ratios, margins, `LAG` variations, `ROW_NUMBER` extremes). A Python script exports them to JSON and stops if a consistency check fails; the browser does not recompute the analysis.

The overview opens with eight KPI cards for the selected season, an automatic reading of the season and four trend charts. Further sections cover the five research questions, revenue, costs, profitability and debt (each ratio with what it measures, its formula, data and limitations), an SQL explorer with syntax highlighting, technique filters and CSV export, and a full methodology. Colours carry fixed meaning: green for favourable, red for unfavourable or risk, amber for alerts, grey for neutral information. Built with plain JavaScript modules and Chart.js; accessible, responsive, and written in European Portuguese.

**Run locally:** `python -m http.server`, then open `http://localhost:8000`.

---

## 🇫🇷 Français

Tableau de bord financier interactif de la Vitória Sport Clube – Futebol, SAD (société de football professionnel du club), 2012/13–2025/26. Tous les chiffres proviennent de requêtes SQL exécutées sur la base SQLite de mon projet [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql) : 48 requêtes du projet sur la SAD et 6 requêtes propres au tableau de bord. Elles sont exportées en JSON par un script Python qui s'arrête si un contrôle de cohérence échoue.

La vue d'ensemble présente huit indicateurs clés pour la saison choisie, une lecture automatique de la saison et quatre graphiques d'évolution. Le tableau de bord comprend aussi les cinq questions de recherche, les recettes, les charges, la rentabilité et l'endettement (chaque ratio avec sa formule et ses limites), un explorateur SQL avec coloration syntaxique et une méthodologie complète. Réalisé en JavaScript (modules ES) avec Chart.js ; accessible et adapté au mobile.

**Lancer en local :** `python -m http.server`, puis ouvrir `http://localhost:8000`.

---

Projeto pessoal de João Garção, sem ligação oficial ao Vitória Sport Clube.
