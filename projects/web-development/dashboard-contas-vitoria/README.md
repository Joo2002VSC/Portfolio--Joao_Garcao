# Dashboard · As contas do Vitória SC

🇵🇹 [Português](#-português) · 🇬🇧 [English](#-english) · 🇫🇷 [Français](#-français)

**[Ver o dashboard ↗](https://joo2002vsc.github.io/Portfolio--Joao_Garcao/projects/web-development/dashboard-contas-vitoria/)**

---

## 🇵🇹 Português

Dashboard interativo, em JavaScript, com as contas do Vitória Sport Clube entre 2012/13 e 2025/26: SAD, Clube e contas consolidadas. É a camada visual do meu projeto de análise em SQL, [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql): os dados saem da base SQLite, passam para JSON e chegam ao browser.

### O que se pode explorar

- **Indicadores da época**: receitas, gastos com pessoal, resultado líquido (com e sem mais-valias), passivo e capital próprio, com a variação face à época anterior e o desempenho em campo.
- **Resultado líquido por entidade**: SAD, Clube e Consolidado lado a lado.
- **Venda de jogadores**: quanto do resultado depende das mais-valias com transferências.
- **Receitas e gastos com pessoal**, com o peso dos salários nas receitas.
- **Balanço**: ativo, passivo e capital próprio a 30 de junho.
- **Composição das receitas** do grupo (TV, UEFA, patrocínios, sócios…).
- **Gastos vs. classificação**: os gastos com pessoal da SAD contra o lugar na Liga.

**Filtros:** entidade, intervalo de épocas e época em destaque. Cada gráfico tem um botão **Ver tabela** com os números exatos. Há modo claro e escuro.

### Como funciona

```
vsc_contas.db  ──►  scripts/exportar_json.py  ──►  data/contas.json  ──►  js/app.js + Chart.js
 (SQLite, vista v_kpis)        (Python)                                     (browser)
```

| Ficheiro | Conteúdo |
|:---|:---|
| `index.html` | Estrutura da página: filtros, indicadores e cartões dos gráficos |
| `css/style.css` | Identidade visual (preto, amarelo, letra Archivo), modo escuro, layout responsivo |
| `js/app.js` | Estado dos filtros, indicadores, definição de cada gráfico e vista em tabela |
| `js/formato.js` | Formatação de números em português (M€, mil €, percentagens) |
| `js/vendor/chart.umd.min.js` | [Chart.js](https://www.chartjs.org/) 4 (licença MIT), incluído no repositório |
| `scripts/exportar_json.py` | Lê a base SQLite e gera `data/contas.json` |
| `data/contas.json` | Os dados que o dashboard usa |

**Escolhas técnicas**
- JavaScript puro, sem frameworks nem passo de compilação: o código lê-se diretamente.
- Cada gráfico é uma função que devolve a configuração do Chart.js e a tabela equivalente, a partir do estado dos filtros.
- As cores das séries foram validadas para daltonismo, em modo claro e escuro, e a identidade de cada série nunca depende só da cor (legenda e tabela).
- Épocas sem dados ficam em branco, em vez de serem interpoladas.

### Abrir localmente

O dashboard lê um ficheiro JSON, por isso precisa de um servidor (o browser bloqueia a leitura a partir do disco):

```bash
# na pasta do dashboard
python -m http.server
# abrir http://localhost:8000
```

Ou, no VS Code, abrir a pasta e usar a extensão **Live Server**.

### Atualizar os dados

Se a base de dados do projeto SQL mudar:

```bash
python scripts/exportar_json.py
# ou indicando outro caminho
python scripts/exportar_json.py --db caminho/para/vsc_contas.db
```

### Fonte e limitações

Relatórios e Contas do Vitória SC, organizados no projeto [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql), onde estão as fontes, a verificação e as limitações. Cada época usa os valores do seu próprio relatório. Nem todas as entidades têm dados para todas as épocas (o Clube, por exemplo, não tem dados de transferências).

---

## 🇬🇧 English

Interactive JavaScript dashboard of Vitória Sport Clube's accounts from 2012/13 to 2025/26: the SAD (the professional football company), the Club and the consolidated group. It is the visual layer of my SQL analysis project, [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql): data flows from SQLite to JSON to the browser.

**What you can explore:** season KPIs with year-on-year change; net result by entity; how much the result depends on player sales; revenue vs. staff costs; balance sheet; revenue mix; staff costs vs. league position. Filters for entity, season range and highlighted season; every chart has a **table view**; light and dark mode.

**Built with** plain HTML, CSS and JavaScript plus Chart.js 4, no framework or build step. A small Python script (`scripts/exportar_json.py`) exports the SQLite views to `data/contas.json`. Series colours were checked for colour-blind safety in both themes.

**Run locally:** `python -m http.server` in this folder, then open `http://localhost:8000`.

---

## 🇫🇷 Français

Tableau de bord interactif en JavaScript sur les comptes du Vitória Sport Clube de 2012/13 à 2025/26 : la SAD (société de football professionnel), le Club et les comptes consolidés. C'est la couche visuelle de mon projet d'analyse SQL, [`contas-vitoria-sql`](../../data-analysis/contas-vitoria-sql) : les données passent de SQLite à JSON, puis au navigateur.

**À explorer :** indicateurs de la saison avec variation annuelle ; résultat net par entité ; dépendance aux ventes de joueurs ; recettes et frais de personnel ; bilan ; composition des recettes ; frais de personnel et classement en championnat. Filtres par entité, intervalle de saisons et saison mise en avant ; chaque graphique a une **vue en tableau** ; modes clair et sombre.

**Réalisé avec** HTML, CSS et JavaScript, plus Chart.js 4, sans framework ni compilation. Un petit script Python (`scripts/exportar_json.py`) exporte les vues SQLite vers `data/contas.json`. Les couleurs des séries ont été vérifiées pour le daltonisme dans les deux thèmes.

**Lancer en local :** `python -m http.server` dans ce dossier, puis ouvrir `http://localhost:8000`.

---

Feito por João Garção · projeto autodidata, fora do currículo.
