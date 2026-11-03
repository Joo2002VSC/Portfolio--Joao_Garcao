<p align="center"><img src="img/icone.png" alt="" width="72"></p>

# As contas do Vitória SC · painel de análise financeira

🇵🇹 [Português](#-português) · 🇬🇧 [English](#-english) · 🇫🇷 [Français](#-français)

**[Abrir o painel ↗](https://joo2002vsc.github.io/Portfolio--Joao_Garcao/projects/web-development/dashboard-contas-vitoria/)**

---

## 🇵🇹 Português

Painel interativo sobre as contas do Vitória Sport Clube de 2012/13 a 2025/26, em três perspetivas: a **SAD** (futebol profissional), o **Clube** (associação) e o **Grupo consolidado**. É a camada de apresentação do projeto [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql): todos os valores resultam de consultas SQL a uma base de dados SQLite construída com os Relatórios e Contas.

### Secções

| Secção | Conteúdo |
|:---|:---|
| **Visão geral** | Quatro dimensões para a entidade e a época escolhidas: (A) situação financeira, (B) desempenho operacional, (C) evolução histórica, com variações, máximos e mínimos, e (D) conclusões automáticas (melhorias, riscos, pontos de atenção, alterações estruturais) |
| **Cinco perguntas** | As perguntas de investigação do projeto, cada uma com resposta, indicadores, gráficos e limitações |
| **SAD, Clube e Grupo** | Natureza de cada entidade, cobertura dos dados e diferença entre o resultado consolidado e a soma das entidades |
| **Rácios financeiros** | Resultados contabilísticos e sustentabilidade financeira (autonomia, solvabilidade, endividamento, liquidez), com o que mede, a fórmula, os dados e as limitações de cada rácio |
| **Receitas e transferências** · **Gastos e pessoal** · **Dívida e liquidez** · **Desporto** · **Cenários** | Análise temática |
| **Consultas SQL** | Explorador das 59 consultas do projeto e de 6 consultas complementares: pesquisa, filtro por técnica SQL (detetada no código), resultado ordenável e exportação para CSV |
| **Metodologia** | Fontes, tratamento, critérios de comparação e de consolidação, limitações, convenções de apresentação e glossário |

### Como funciona

```
contas-vitoria-sql/vsc_contas.db ─┐
contas-vitoria-sql/sql/04_analises.sql ─┼─► scripts/exportar_json.py ─► data/*.json ─► js/ (navegador)
sql/indicadores_dashboard.sql ─┘          (executa as consultas e verifica a coerência)
```

- O painel **não refaz os cálculos**: lê os resultados das consultas. Os rácios que o projeto SQL não tinha (autonomia e solvabilidade por entidade, variações com `LAG`, máximos e mínimos com `ROW_NUMBER`, diferença de consolidação) estão em [`sql/indicadores_dashboard.sql`](sql/indicadores_dashboard.sql), com divisões protegidas por `NULLIF`.
- O script de exportação **interrompe a geração** se alguma verificação falhar: por exemplo, se ativo − passivo ≠ capital próprio, ou se os rácios da consulta complementar D1 divergirem da consulta 29.
- JavaScript em módulos ES, sem *frameworks*. O Chart.js 4 está incluído no repositório.

| Ficheiro | Função |
|:---|:---|
| `js/dados.js` | Carregamento e validação dos dados; funções numéricas protegidas contra nulos e divisões por zero |
| `js/formato.js` | Convenções portuguesas: vírgula decimal, espaço nos milhares, parênteses nos valores monetários negativos; rótulos das colunas |
| `js/paineis.js` | Definição de cada visualização (pergunta, consulta, gráfico, conclusão, ficha do indicador) e das cinco perguntas |
| `js/conclusoes.js` | Conclusões automáticas da visão geral, com limiares explícitos |
| `js/graficos.js` · `js/tabelas.js` · `js/explorador.js` · `js/animacoes.js` | Gráficos, tabelas ordenáveis e exportação, explorador SQL, animações |
| `js/app.js` | Estado, filtros (guardados no endereço), navegação e visão geral |

### Acessibilidade e apresentação

- HTML semântico, navegação completa por teclado e ligação para saltar para o conteúdo.
- Cada gráfico tem uma descrição para leitores de ecrã e uma alternativa em tabela.
- Contraste verificado em modo claro e escuro.
- Respeita a opção do sistema para reduzir o movimento.
- Português europeu em toda a interface, com glossário e convenções de apresentação descritas na secção Metodologia.

### Executar localmente

```bash
python -m http.server     # na pasta do painel
# abrir http://localhost:8000
```

Para atualizar os dados depois de alterar a base: `python scripts/exportar_json.py`.

Ao publicar alterações, aumente o número de versão (`?v=4`) no `index.html`, para que os navegadores não misturem ficheiros novos com ficheiros em cache.

### Limitações

- O Clube e o Grupo consolidado têm menos épocas e rubricas do que a SAD e ainda não têm contas de 2025/26.
- Em três épocas, o resultado consolidado coincide com a soma das entidades; os ajustes de consolidação não são visíveis nos dados.
- As simulações da centralização dos direitos de TV são ilustrativas.
- A regressão entre despesas e classificação usa 13 épocas: mostra uma associação, não uma relação de causa e efeito.

---

## 🇬🇧 English

Interactive financial dashboard of Vitória Sport Clube (2012/13–2025/26) covering the SAD (professional football company), the Club and the consolidated Group. Every figure comes from SQL queries run against the SQLite database of my [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql) project: 59 project queries plus 6 dashboard queries (ratios, `LAG` variations, `ROW_NUMBER` extremes, consolidation differences), exported to JSON by a Python script that stops if a consistency check fails. The browser does not recompute the analysis.

The overview is organised into four dimensions: financial position, operating performance, historical trends and automatic conclusions. There are also sections for the five research questions, the entity comparison, financial ratios (each with what it measures, its formula, data and limitations), an SQL explorer with technique filters and CSV export, and a full methodology. Built with plain JavaScript modules and Chart.js; accessible, responsive, and written in European Portuguese.

**Run locally:** `python -m http.server`, then open `http://localhost:8000`.

---

## 🇫🇷 Français

Tableau de bord financier interactif du Vitória Sport Clube (2012/13–2025/26) : la SAD (société de football professionnel), le Club et le Groupe consolidé. Tous les chiffres proviennent de requêtes SQL exécutées sur la base SQLite de mon projet [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql) : 59 requêtes du projet et 6 requêtes propres au tableau de bord. Elles sont exportées en JSON par un script Python qui s'arrête si un contrôle de cohérence échoue.

La vue d'ensemble s'organise en quatre dimensions : situation financière, performance opérationnelle, évolution historique et conclusions automatiques. Le tableau de bord comprend aussi les cinq questions de recherche, la comparaison des entités, les ratios financiers (avec formule et limites), un explorateur SQL et une méthodologie complète. Réalisé en JavaScript (modules ES) avec Chart.js ; accessible et adapté au mobile.

**Lancer en local :** `python -m http.server`, puis ouvrir `http://localhost:8000`.

---

Projeto pessoal de João Garção, sem ligação oficial ao Vitória Sport Clube.
