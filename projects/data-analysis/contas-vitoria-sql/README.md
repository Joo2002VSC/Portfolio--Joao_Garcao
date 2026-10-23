# As contas do Vitória SC em SQL

Base de dados SQLite com as contas do **Vitória Sport Clube** — SAD, Clube e Grupo consolidado — entre **2012/13 e 2024/25**, e um conjunto de consultas SQL que respondem a perguntas sobre a sustentabilidade financeira do clube.

> Projeto pessoal de análise de dados. Não tem qualquer ligação oficial ao Vitória Sport Clube.

![Resultado líquido por entidade](graficos/01_resultado_por_entidade.png)

## Principais conclusões

- **A SAD vive das vendas de jogadores.** Em todas as oito épocas com dados de transferências, o resultado sem mais-valias seria negativo — entre −5,9 M€ e −25,3 M€. Os lucros de 2022/23 e do recorde de 2024/25 (+7,6 M€) só existem graças às vendas.
- **O pessoal pesou mais do que as receitas durante quatro épocas seguidas.** De 2020/21 a 2023/24, os gastos com pessoal ficaram entre 119% e 200% das vendas e serviços.
- **A SAD está em falência técnica desde 2020/21.** O capital próprio é negativo há cinco épocas seguidas (−24 M€ em 2024/25) e o passivo é hoje 11,5 vezes o do Clube.
- **Os juros dispararam.** Passaram de 149 mil € em 2019/20 para 5 M€ em 2024/25 — um crescimento médio de cerca de 100% ao ano. 92% da dívida financeira vence em menos de um ano.
- **Uma época europeia muda tudo.** Nas épocas com fase de grupos UEFA, as receitas operacionais médias foram de 21,3 M€, contra 14,0 M€ nas restantes.

Todos os resultados estão em [`resultados.md`](resultados.md).

## Estrutura do projeto

```
contas-vitoria-sql/
├── data/                 Dados em CSV (um ficheiro por tabela)
├── sql/
│   ├── 01_schema.sql     Criação das tabelas
│   ├── 02_dimensoes.sql  Épocas, entidades e rubricas
│   ├── 03_vistas.sql     Vistas reutilizáveis (pivot, KPIs)
│   └── 04_analises.sql   19 consultas de análise
├── scripts/
│   ├── build_db.py       Constrói vsc_contas.db
│   ├── correr_analises.py  Corre as consultas e gera resultados.md
│   └── graficos.py       Gera os gráficos em graficos/
├── graficos/             Gráficos PNG
├── resultados.md         Resultados das consultas
└── vsc_contas.db         A base de dados pronta a abrir
```

## Como usar

A base de dados `vsc_contas.db` já vem incluída: pode ser aberta diretamente no [DB Browser for SQLite](https://sqlitebrowser.org/), no DBeaver ou em qualquer cliente SQLite.

Para a reconstruir do zero:

```bash
python scripts/build_db.py         # só biblioteca padrão
python scripts/correr_analises.py  # gera resultados.md
pip install matplotlib
python scripts/graficos.py         # gera os gráficos
```

## Modelo de dados

| Tabela | Conteúdo |
|---|---|
| `epoca`, `entidade`, `rubrica` | Dimensões: 13 épocas, 3 entidades, 20 rubricas |
| `demonstracao_resultados` | Demonstração de resultados em formato longo (entidade × época × rubrica) |
| `balanco` | Ativo, passivo, capital próprio e caixa a 30 de junho |
| `cash_flow` | Fluxos operacional, de investimento e de financiamento (SAD) |
| `receitas_composicao` | Receitas operacionais por fonte (TV, UEFA, sócios…) |
| `gastos_pessoal_composicao` | Atletas, treinadores e outro pessoal |
| `transferencias` | Vendas brutas, custos e mais-valias por época |
| `operacao_jogador` | Principais vendas e aquisições de 2024/25 |
| `divida` | Dívida da SAD por credor e maturidade (30/06/2025) |
| `fonte` | Estado e documentos de origem de cada época |
| `evento` | Acontecimentos e observações relevantes |

Os gastos são guardados com sinal negativo, tal como nas demonstrações de resultados. Valores não disponíveis ficam como `NULL` (ou sem linha, na tabela longa).

## Técnicas SQL utilizadas

CTEs (incluindo uma CTE recursiva para gerar as épocas) · funções de janela (`LAG`, `RANK`, `ROW_NUMBER`, `FIRST_VALUE`, `SUM() OVER`, médias móveis) · pivot com `CASE` · self-joins · `UNION ALL` · vistas · chaves estrangeiras e restrições `CHECK` · análise de lacunas e de qualidade dos dados.

## Mais gráficos

![Dependência das vendas de jogadores](graficos/03_dependencia_vendas_jogadores.png)
![Receitas vs pessoal](graficos/02_receitas_vs_pessoal_sad.png)
![Composição das receitas](graficos/04_composicao_receitas.png)
![Balanço da SAD](graficos/05_balanco_sad.png)

## Fontes e limitações

Os dados foram recolhidos em outubro de 2026 do site **[VSC Contas](https://vitoriasempre.net/contas-vsc/)**, um dashboard não oficial que extrai os números dos Relatórios e Contas auditados publicados em [vitoriasc.pt/documentos](https://vitoriasc.pt/documentos/). Para qualquer uso sério, os valores devem ser confirmados nos documentos originais.

As próprias consultas de qualidade (17 a 19 em `resultados.md`) revelam limitações que convém conhecer:

- **Cobertura desigual.** A SAD tem a demonstração de resultados completa em quase todas as épocas; o Clube só tem dados detalhados a partir de 2021/22 (antes disso, apenas resultado, EBITDA e passivo, arredondados); o consolidado começa em 2017/18.
- **Valores repetidos.** Os direitos TV aparecem com exatamente 6 922 619 € em quatro épocas seguidas e "Outros" repete-se em 2023/24 e 2024/25 — provavelmente valores de preenchimento e não dados reais.
- **Números diferentes para a mesma coisa.** As mais-valias de transferências da página da SAD diferem das da página consolidada em cinco épocas. As duas versões estão guardadas, com a entidade de origem.
- **Composição das receitas.** Os totais coincidem com os rendimentos operacionais *consolidados* (e não com as vendas e serviços da SAD), por isso foram associados ao Grupo.
- **Rácio pessoal/receitas.** É uma aproximação simples; a regra de custos do plantel da UEFA usa outra base de cálculo.
