# Dashboard · As contas do Vitória SC

🇵🇹 [Português](#-português) · 🇬🇧 [English](#-english) · 🇫🇷 [Français](#-français)

**[Abrir o dashboard ↗](https://joo2002vsc.github.io/Portfolio--Joao_Garcao/projects/web-development/dashboard-contas-vitoria/)**

---

## 🇵🇹 Português

Dashboard interativo sobre as contas do Vitória Sport Clube entre 2012/13 e 2025/26: a SAD, o Clube e o Grupo consolidado. É a camada visual do meu projeto de análise em SQL, [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql). Todos os indicadores saem das **59 consultas SQL** desse projeto: o dashboard não refaz cálculos, mostra os resultados das consultas.

### O que tem

| Secção | Perguntas a que responde | Consultas |
|:---|:---|:---|
| **Visão geral** | Indicadores da época em destaque (SAD, Clube ou Grupo), as cinco perguntas de investigação do projeto, resultado por entidade e dependência das vendas | 2, 6, 10, 27, 28, 31, 52–55 |
| **Receitas e transferências** | De onde vêm os rendimentos; peso da TV, da Europa e da venda de jogadores; mais-valias, múltiplo de venda, intermediários, passes, solidariedade | 5, 12, 21, 40, 41, 46, 47, 54, 57 |
| **Custos e pessoal** | Gastos por rubrica, gastos face a receitas e vendas, salários face a receitas, custos fixos, rácio da UEFA, funcionários e remunerações | 3, 31–33, 42, 45, 56, 58 |
| **Balanço e dívida** | Capital próprio, endividamento e liquidez, dívida financeira e instrumentos, juros face ao mercado, fluxos de caixa, fundo de maneio, artigo 35.º, reexpressão de 2024/25 | 7, 11, 15, 27–30, 36–39, 43, 51, 52 |
| **Desporto** | Regressão entre despesas e classificação (R², intervalo de confiança), custo por ponto, espectadores, treinadores | 20, 34, 49, 50, 53 |
| **Cenários** | Ponto de equilíbrio e centralização dos direitos TV (simulações ilustrativas) | 25, 26, 48, 55 |
| **Consultas SQL** | Explorador das 59 consultas: pesquisa, código com realce, resultado ordenável e exportação para CSV | 1–59 |

Cada gráfico tem:
- um **título em forma de pergunta**;
- uma **conclusão calculada a partir dos dados filtrados**;
- um botão **Ver tabela** com os valores exatos;
- a **ligação à consulta SQL** de onde vem.

**Filtros:** intervalo de épocas, época em destaque (assinalada em todos os gráficos) e botão para repor os filtros. Os filtros ficam no endereço da página, por isso uma vista filtrada pode ser partilhada.

### Como funciona

```
contas-vitoria-sql/                     dashboard-contas-vitoria/
  vsc_contas.db  ─┐
  sql/04_analises.sql ─┼─► scripts/exportar_json.py ─► data/consultas.json ─┐
  vista v_kpis  ──┘        (corre as 59 consultas      data/contas.json    ─┴─► js/ (browser)
                            e verifica a coerência)
```

| Ficheiro | Responsabilidade |
|:---|:---|
| `scripts/exportar_json.py` | Lê `04_analises.sql`, corre cada consulta na base SQLite e grava título, secção, conceitos SQL, código e resultado. Pára se uma verificação falhar (ex.: ativo − passivo ≠ capital próprio) |
| `js/dados.js` | Carrega e valida os JSON; acesso às consultas; funções numéricas seguras (nulos, divisões por zero) |
| `js/formato.js` | Números em português europeu (parênteses nos negativos, M€, %, p.p.) e metadados das colunas |
| `js/paineis.js` | Definição de cada visualização: pergunta, consulta, gráfico e conclusão |
| `js/graficos.js` | Cores do tema, opções comuns e plugins do Chart.js (época em destaque, linhas de referência) |
| `js/tabelas.js` | Tabelas ordenáveis e acessíveis; exportação CSV (separador `;`, para o Excel em português) |
| `js/explorador.js` | Explorador das consultas SQL |
| `js/animacoes.js` | Animações de entrada, transições entre filtros e contagem dos indicadores |
| `js/app.js` | Estado, navegação entre secções, filtros e indicadores |

**Escolhas técnicas**
- **JavaScript sem frameworks** (módulos ES) e Chart.js 4, incluído no repositório. Não há passo de compilação.
- **Uma só escala por gráfico.** Quando duas medidas têm unidades diferentes, ficam em gráficos separados ou passam para o tooltip.
- **A cor tem significado.** Preto, cinzento e amarelo, como no projeto SQL. O amarelo assinala o que ultrapassa um limite, por exemplo salários acima de 100% das receitas ou o rácio da UEFA acima de 70%. A identidade das séries nunca depende só da cor: há legenda, conclusão e tabela.
- **Acessibilidade (WCAG 2.2 AA):**
  - HTML semântico e ligação para saltar para o conteúdo;
  - navegação completa por teclado;
  - gráficos com descrição e alternativa em tabela;
  - contraste verificado em modo claro e escuro;
  - respeito pela opção `prefers-reduced-motion`.
- **Desempenho:** cada gráfico só é desenhado quando aparece no ecrã. Ao mudar um filtro, os gráficos atualizam-se em vez de se redesenharem.

### Abrir localmente

O dashboard lê ficheiros JSON, por isso precisa de um servidor:

```bash
python -m http.server     # na pasta do dashboard
# abrir http://localhost:8000
```

### Atualizar os dados

```bash
python scripts/exportar_json.py
```

### Limitações conhecidas

- **Cobertura das entidades.** O Clube e o Grupo consolidado têm menos épocas e menos rubricas do que a SAD, e ainda não têm contas de 2025/26. Vários indicadores só existem para a SAD.
- **Consulta 14 do projeto SQL.** O título diz 30/06/2025, mas o resultado mistura linhas de 30/06/2025 e de 30/06/2026. O dashboard usa a consulta 39 e assinala o problema no explorador.
- **Rácio da UEFA (consulta 45).** É uma aproximação ao regulamento. Nas duas primeiras épocas, a média das mais-valias usa menos de três épocas.
- **Cenários de centralização.** São ilustrativos, porque o modelo de repartição dos direitos TV ainda não está definido.
- **Regressão desporto/despesas.** Usa 13 épocas: é uma associação, não uma relação de causa e efeito.

---

## 🇬🇧 English

Interactive dashboard of Vitória Sport Clube's accounts (2012/13–2025/26): the SAD (professional football company), the Club and the consolidated group. Every figure comes from the **59 SQL queries** of my [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql) project. A Python script runs them against the SQLite database, checks consistency and exports the results to JSON; the browser only presents them.

Seven sections: overview, revenue and transfers, costs and staff, balance sheet and debt, sport, scenarios, and an **SQL explorer** (search, highlighted code, sortable results, CSV export). Each chart asks a question, shows a conclusion computed from the filtered data, has a table view and links back to its query. Built with plain JavaScript modules and Chart.js, accessible (keyboard, screen readers, reduced motion) and responsive.

**Run locally:** `python -m http.server` in this folder, then open `http://localhost:8000`.

---

## 🇫🇷 Français

Tableau de bord interactif sur les comptes du Vitória Sport Clube (2012/13–2025/26) : la SAD (société de football professionnel), le Club et le groupe consolidé. Tous les indicateurs proviennent des **59 requêtes SQL** de mon projet [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql). Un script Python les exécute sur la base SQLite, vérifie la cohérence et exporte les résultats en JSON ; le navigateur ne fait que les présenter.

Sept sections : vue d'ensemble, recettes et transferts, coûts et personnel, bilan et dette, sport, scénarios et un **explorateur SQL** (recherche, code en couleur, résultats triables, export CSV). Chaque graphique pose une question, affiche une conclusion calculée sur les données filtrées, propose une vue en tableau et renvoie à sa requête. Réalisé en JavaScript (modules ES) avec Chart.js, accessible et adapté au mobile.

**Lancer en local :** `python -m http.server` dans ce dossier, puis ouvrir `http://localhost:8000`.

---

Feito por João Garção · projeto autodidata, fora do currículo.
