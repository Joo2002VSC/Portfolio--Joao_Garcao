<p align="center">
  <img src="graficos/00_capa.png" alt="As contas do Vitória SC — análise financeira em SQL" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/SQLite-3-111111?style=flat-square&logo=sqlite&logoColor=F5D510" alt="SQLite">
  <img src="https://img.shields.io/badge/Python-3-111111?style=flat-square&logo=python&logoColor=F5D510" alt="Python">
  <img src="https://img.shields.io/badge/Matplotlib-gráficos-111111?style=flat-square&labelColor=111111&color=F5D510" alt="Matplotlib">
  <img src="https://img.shields.io/badge/épocas-2012%2F13%20–%202025%2F26-111111?style=flat-square&labelColor=111111&color=F5D510" alt="Épocas">
</p>

<p align="center">
  <a href="#resumo">Resumo</a> ·
  <a href="#principais-conclusões">Conclusões</a> ·
  <a href="#relatórios">Relatórios</a> ·
  <a href="#modelo-de-dados">Modelo de dados</a> ·
  <a href="#como-usar">Como usar</a> ·
  <a href="#fontes-e-limitações">Fontes e limitações</a>
</p>

> **Projeto relacionado:** a [dashboard interativa](../../web-development/dashboard-contas-vitoria) é a camada de apresentação desta base de dados: os valores que mostra resultam destas consultas SQL, exportados pelo script `exportar_json.py` da própria dashboard. [Abrir a dashboard ↗](https://joo2002vsc.github.io/Portfolio--Joao_Garcao/projects/web-development/dashboard-contas-vitoria/)

---

<a id="resumo"></a>
<img src="graficos/cabecalhos/01_resumo.png" alt="Resumo" width="100%">

Base de dados **SQLite** com as contas do **Vitória Sport Clube** em três perspetivas: a **SAD** (futebol profissional), o **Clube** (associação-mãe) e o **Grupo consolidado**. Cobre 14 épocas, de 2012/13 a 2025/26, e cruza as contas com os resultados desportivos de cada época.

Sobre essa base, **59 consultas SQL** respondem a uma pergunta central: *as contas do Vitória são sustentáveis sem a venda de jogadores?*

**Perguntas de investigação**

| # | Pergunta | Resposta curta | Onde |
|:---:|:---|:---|:---|
| 1 | A atividade corrente cobre os custos recorrentes? | Não. A margem corrente sem vendas foi negativa em todas as épocas; em média faltaram 22,8 M€ por época (2023/24–2025/26). | Conclusões 1–2, consultas 2, 42, 51 |
| 2 | Quanto pesam as vendas de jogadores e a Europa? | As vendas superaram sempre as receitas da operação (2,07 € por cada euro em 2025/26). A fase de grupos europeia sobe as receitas médias de 14,0 para 21,3 M€. | Conclusões 5 e 10, consultas 6, 54 |
| 3 | A dívida é sustentável e a que custo? | É cara e curta: taxa implícita de 14,9% (12,5 p.p. acima da Euribor) e 94% a vencer em menos de um ano (30/06/2026). | Conclusões 3, 4 e 9, consultas 27–30, 52 |
| 4 | Gastar mais traz melhores classificações? | Não se consegue demonstrar: R² = 0,02 em 13 épocas e o intervalo de confiança do efeito inclui o zero. | Conclusão 6, consultas 22, 53 |
| 5 | Que combinação reduz a dependência das vendas? | Centralização dos direitos TV e juros ao nível do mercado cobririam cerca de 37% do défice. O resto exige cortar custos ou manter vendas. | Conclusão 11, consultas 48, 55 |

**✓ Dados verificados.** O balanço, a dívida, os juros e o pessoal da SAD foram conferidos com os 14 Relatórios e Contas de 2012/13 a 2025/26 (incluindo os digitalizados, lidos com OCR). A [verificação das fontes](verificacao-fontes.md) documenta 40 divergências encontradas em fontes secundárias e o que foi corrigido.

> Projeto pessoal e autodidata de análise de dados. Não tem qualquer ligação oficial ao Vitória Sport Clube.

<a id="indicadores-chave"></a>
<img src="graficos/cabecalhos/02_indicadores.png" alt="Indicadores-chave da SAD" width="100%">

| Indicador | 2023/24 | 2024/25 | 2025/26 |
|:---|---:|---:|---:|
| Lugar na Liga · Europa | 5.º · pré-eliminatória | 6.º · oitavos da Liga Conferência | 9.º · sem Europa |
| Receitas (vendas e serviços) | 12,9 M€ | **22,6 M€** | 14,9 M€ |
| Gastos com pessoal | (16,9 M€) | (20,5 M€) | **(21,7 M€)** |
| Mais-valias com jogadores | 6,7 M€ | **27,5 M€** | 16,1 M€ |
| **Resultado líquido** | **(14,7 M€)** | **7,6 M€** | **(11,1 M€)** |
| Resultado sem mais-valias | (21,4 M€) | (19,9 M€) | **(27,1 M€)** |
| Dívida financeira (30/06) | 34,0 M€ | 34,6 M€ | **40,8 M€** |
| Capital próprio (30/06) | (31,2 M€) | (24,0 M€) | **(36,8 M€)** |
| Funcionários (média) | 200 | 229 | **302** |

<sub>Valores negativos entre parênteses, como nas demonstrações financeiras. Cada época com os valores do seu próprio Relatório e Contas; 2024/25 foi depois reexpressa (resultado de 7,36 M€, capital próprio de (25,8 M€)), ver a tabela `reexpressao`.</sub>

<a id="principais-conclusões"></a>
<img src="graficos/cabecalhos/03_conclusoes.png" alt="Principais conclusões" width="100%">

**1. A SAD vive das vendas de jogadores.** Nas nove épocas com dados de transferências, o resultado sem mais-valias seria sempre negativo, entre (5,9 M€) e (27,1 M€). O pior valor é o de 2025/26: mesmo com 16,1 M€ de mais-valias, a SAD perdeu 11,1 M€. O recorde de 2024/25 só existiu graças a 27,5 M€ de mais-valias.

![Dependência das vendas de jogadores](graficos/03_dependencia_vendas_jogadores.png)

**2. Os salários ultrapassaram as receitas em cinco das últimas seis épocas.** Entre 2020/21 e 2023/24, os gastos com pessoal ficaram entre 119% e 200% das vendas e serviços. Em 2025/26, sem Europa, voltaram a 146%, com um recorde de 21,7 M€ em gastos com pessoal.

![Receitas vs. gastos com pessoal](graficos/02_receitas_vs_pessoal_sad.png)

**3. A SAD só teve capital próprio positivo em 4 das 14 épocas** (2016/17 a 2019/20). Desde 2020/21, o passivo supera o ativo: o capital próprio chegou a (36,8 M€) a 30/06/2026, e o passivo a 85,3 M€. O passivo corrente excede o ativo corrente em 52,5 M€. O rácio de endividamento de 2023/24 (1,87) foi o mais alto da história da SAD; em 2025/26 foi de 1,76.

![Ativo vs. passivo da SAD](graficos/05_balanco_sad.png)

**4. A dívida ficou mais cara e mais curta.** A dívida financeira passou de 1,2 M€ (2019/20) para 40,8 M€ (30/06/2026), e os juros dos financiamentos de 149 mil € para 5,6 M€, cerca de 38 vezes mais. A taxa de juro implícita subiu de cerca de 6% para **15%**, e os juros já pesam 38% das receitas. A 30/06/2026, 94% da dívida financeira vencia em menos de um ano; o empréstimo principal (MSD, 12,5%) vence a 31/12/2026. A liquidez geral está abaixo de 0,5 desde 2021/22 (0,27 em 2025/26).

![Dívida financeira e juros](graficos/07_divida_e_juros.png)

![Endividamento e liquidez](graficos/08_endividamento_liquidez.png)

**5. Uma época europeia muda tudo.** Com fase de grupos UEFA, as receitas operacionais médias foram de 21,3 M€, contra 14,0 M€ nas restantes épocas.

![Composição das receitas](graficos/04_composicao_receitas.png)

**6. Gastar mais não garantiu melhores classificações.** Numa regressão linear entre as despesas da SAD (pessoal, FSE e amortizações) e o lugar na Liga, em 13 épocas, cada 10 M€ a mais valem, em média, só 0,3 lugares, e as despesas explicam apenas 2% das diferenças de classificação (R² = 0,02). O intervalo de confiança a 95% do declive inclui o zero: é uma associação fraca, não uma relação de causa e efeito. O 4.º lugar de 2016/17 custou 13,3 M€; o 9.º lugar de 2025/26 custou 37,7 M€, a despesa mais alta de sempre.

![Despesas vs. classificação](graficos/16_despesas_vs_classificacao.png)

**7. A estrutura cresceu mais depressa do que a equipa.** A SAD passou de 59 funcionários em 2012/13 para **302 em 2025/26**, um recorde (mais 73 num só ano). Os jogadores quase triplicaram (42 → 118), mas o restante pessoal (treinadores, staff e apoio) multiplicou-se por mais de 10 (17 → 184). Há 1,6 não-jogadores por cada jogador, contra 0,4 em 2012/13. A remuneração média por jogador subiu de 80 mil € (2016/17) para 134 mil € (2024/25) e desceu para 96 mil € em 2025/26, porque o número de jogadores aumentou muito mais do que a massa salarial.

![Funcionários da SAD](graficos/09_funcionarios.png)

**8. O Clube e a SAD têm perfis opostos.** O Clube tem pouco passivo e património valioso (Estádio e Academia), mas prejuízos recorrentes, perto de 1 M€ por ano nas duas últimas épocas. A SAD concentra a dívida e a volatilidade.

![Resultado líquido por entidade](graficos/01_resultado_por_entidade.png)

**9. O Vitória paga juros muito acima do mercado.** Em 2025/26, a taxa implícita da dívida foi de 14,9% (o próprio relatório fala em "cerca de 15%"), contra 2,4% da Euribor a 12 meses e 3,2% das obrigações do Estado português: um spread de 12,5 pontos percentuais. Em 2019/20, com juros negativos na zona euro, a SAD pagou 9,6%, 21 vezes a taxa do Estado. À taxa média do crédito às empresas em Portugal, os juros seriam 3,5 a 3,9 M€ mais baixos por ano.

![Taxas de juro](graficos/15_taxas_de_juro.png)

**10. A SAD vende sempre mais em jogadores do que fatura na operação.** Em todas as épocas desde 2017/18, as vendas brutas de jogadores superaram as receitas de bilheteira, TV, patrocínios e sócios. Em 2024/25 foram 2,19 € de vendas por cada euro de receita, e em 2025/26 foram 2,07 €. A média de três épocas subiu de 1,09 € (2017/18) para 1,80 € (2025/26).

![Vendas vs. receitas](graficos/17_vendas_vs_receitas.png)

**11. A centralização dos direitos TV ajuda muito, mas não equilibra as contas sozinha.** O défice antes de vendas foi de 22,8 M€ por época (média 2023/24–2025/26). Num cenário central (contrato de 250 M€, 6.º lugar), a centralização traz mais 4,8 M€, cerca de um quinto do défice. Somada a juros ao nível do mercado, as mais-valias necessárias para o equilíbrio desceriam de cerca de 23 M€ para 14 M€ por época, abaixo da média das três últimas épocas (16,8 M€).

![Centralização e equilíbrio](graficos/18_centralizacao_equilibrio.png)

**13. As vendas de jogadores nunca pagaram os gastos.** Em nove épocas, as mais-valias cobriram entre 20% e 72% dos gastos operacionais; em 2025/26 cobriram 40%, e ficaram por cobrir 24,2 M€, mais do que todas as receitas da operação (14,9 M€). Os gastos operacionais duplicaram desde 2017/18, para um máximo de 40,3 M€. O relatório em PDF [Rendimentos, gastos e transferências](relatorio/rendimentos-gastos-transferencias.pdf) detalha a evolução de cada rubrica.

![Gastos operacionais, receitas de transferências e saldo](relatorio/graficos/01_gastos_transferencias_saldo.png)

O [painel de indicadores](analise-tecnica.md#18-painel-de-indicadores-financeiros) junta a margem corrente (negativa em todas as épocas), a rendibilidade do ativo, a dívida face às receitas e o cash flow operacional.

**12. As contas de 2025/26 mudaram a leitura do passado.** O Relatório e Contas de 2025/26 corrigiu sete erros de 2024/25: custo amortizado não aplicado, uma provisão FIFA, comissões de uma venda, juros não especializados, inventários, imparidades e direitos económicos que já não eram ativos. O capital próprio de 30/06/2025 baixou 1,7 M€. A demonstração dos fluxos de caixa foi refeita: o fluxo operacional de 2024/25 passou de +0,9 M€ para **(18,9 M€)**, porque 36,5 M€ de recebimentos de clientes tinham ido diretamente para os financiadores, para amortizar créditos antecipados. Na nova apresentação, a operação consumiu 19 M€ de caixa em cada uma das duas últimas épocas, cobertos com nova dívida.

Os resultados completos das 59 consultas estão em [`resultados.md`](resultados.md).

<a id="relatórios"></a>
<img src="graficos/cabecalhos/04_relatorios.png" alt="Relatórios" width="100%">

| Relatório | O que contém |
|:---|:---|
| **[Análise estratégica](analise-estrategica.md)** | Diagnóstico, finanças vs. desempenho desportivo, enquadramento económico e 12 recomendações com cenários |
| **[Análise técnica](analise-tecnica.md)** | 17 conceitos aprofundados: custo amortizado, dívida líquida/EBITDA, fundo de maneio, factoring, passes, reservas ocultas, artigo 35.º do CSC, alavancagem operacional, partes relacionadas, regras da UEFA, multiclube, Lei 39/2023, intermediários, direitos de terceiros, solidariedade, centralização dos direitos TV e eficiência desportiva. Uma terceira parte junta o painel de indicadores, a comparação com as taxas de juro de mercado, a regressão entre despesas e classificação, o peso das vendas e a centralização como via para equilibrar as contas |
| **[Verificação das fontes](verificacao-fontes.md)** | Conferência de cada número com os Relatórios e Contas e as 40 divergências encontradas em fontes secundárias |
| **[Rendimentos, gastos e transferências](relatorio/rendimentos-gastos-transferencias.pdf)** (PDF, 7 páginas) | Gastos operacionais face às receitas de transferências e saldo, evolução das rubricas de rendimentos e de gastos desde 2013/14 e detalhe das notas do R&C 2025/26 |
| **[Testes](testes.md)** | Resultado dos testes automáticos de integridade, coerência contabilística e reconciliação |
| **[Dicionário de dados](dicionario-dados.md)** | As 31 tabelas e vistas, coluna a coluna |

| | |
|:---:|:---:|
| ![Reservas ocultas](graficos/10_reservas_ocultas.png) | ![Rácio de custos do plantel](graficos/12_racio_custos_plantel_uefa.png) |
| ![Centralização por lugar](graficos/13_centralizacao_por_lugar.png) | ![Custo por ponto](graficos/14_custo_por_ponto.png) |
| ![Painel de indicadores](graficos/19_painel_indicadores.png) | ![Salários vs. classificação](graficos/06_salarios_vs_classificacao.png) |

<a id="modelo-de-dados"></a>
<img src="graficos/cabecalhos/05_modelo-de-dados.png" alt="Modelo de dados" width="100%">

```mermaid
erDiagram
    EPOCA ||--o{ DEMONSTRACAO_RESULTADOS : ""
    ENTIDADE ||--o{ DEMONSTRACAO_RESULTADOS : ""
    RUBRICA ||--o{ DEMONSTRACAO_RESULTADOS : ""
    EPOCA ||--o{ BALANCO : ""
    ENTIDADE ||--o{ BALANCO : ""
    EPOCA ||--o{ CASH_FLOW : ""
    EPOCA ||--o{ RECEITAS_COMPOSICAO : ""
    EPOCA ||--o{ GASTOS_PESSOAL_COMPOSICAO : ""
    EPOCA ||--o{ TRANSFERENCIAS : ""
    EPOCA ||--o{ OPERACAO_JOGADOR : ""
    EPOCA ||--o{ EVENTO : ""
    EPOCA ||--o{ FONTE : ""
    EPOCA ||--|| DESEMPENHO_DESPORTIVO : ""
    EPOCA ||--|| BALANCO_SAD_RC : ""
    EPOCA ||--|| PESSOAL_SAD : ""
    EPOCA ||--o{ DIVERGENCIA : ""

    DEMONSTRACAO_RESULTADOS {
        text entidade_id PK
        text epoca_id PK
        text rubrica_id PK
        int valor
    }
    BALANCO {
        text entidade_id PK
        text epoca_id PK
        int ativo_total
        int passivo_total
        int capital_proprio
        int caixa
    }
    TRANSFERENCIAS {
        text entidade_id PK
        text epoca_id PK
        int vendas_brutas
        int custo_vendas
        int mais_valias_liquidas
    }
```

| Tabela | Conteúdo |
|:---|:---|
| `epoca` · `entidade` · `rubrica` | Dimensões: 14 épocas, 3 entidades, 20 rubricas |
| `desempenho_desportivo` | Lugar na Liga, pontos, média de espectadores, campanha europeia e troféus |
| `balanco_sad_rc` | Balanço detalhado da SAD, dívida financeira e juros, tal como publicados nos R&C |
| `pessoal_sad` | Nº médio de funcionários por categoria e decomposição dos gastos com pessoal |
| `divergencia` | Diferenças entre fontes secundárias e os R&C (auditoria) |
| `balanco_rubrica` | Balanço da SAD rubrica a rubrica (clientes, fornecedores, outras contas a pagar…) |
| `passes_jogadores` | Aquisições, amortizações, abates e valor contabilístico do plantel |
| `financiamento_detalhe` | Dívida financeira por instrumento (empréstimos, factoring, Apollo, locações) |
| `partes_relacionadas` | Fluxos e saldos entre o Clube, a SAD e a V Sports |
| `auditoria` | Opinião do auditor, ênfases e incertezas materiais por época |
| `reexpressao` | Valores originais e reexpressos de 2024/25 (balanço, resultado, juros e fluxos de caixa) |
| `treinador` | Treinadores principais e interinos desde 2015 |
| `detalhe_rubrica` | Detalhe das notas 15, 17, 19 e 20 do R&C 2025/26 (vendas e serviços, FSE, outros rendimentos e outros gastos), 2024/25 e 2025/26 |
| `taxa_referencia` · `bce_taxa` | Euribor a 12 meses, obrigações do Estado a 10 anos, crédito a empresas em Portugal e taxas diretoras do BCE |
| `demonstracao_resultados` | Demonstração de resultados em formato longo (entidade × época × rubrica) |
| `balanco` | Ativo, passivo, capital próprio e caixa a 30 de junho (SAD: valores dos R&C) |
| `cash_flow` | Fluxos operacional, de investimento e de financiamento (SAD) |
| `receitas_composicao` | Receitas operacionais por fonte (TV, UEFA, sócios…) |
| `gastos_pessoal_composicao` | Atletas, treinadores e outro pessoal |
| `transferencias` | Vendas brutas, custos e mais-valias por época |
| `operacao_jogador` | Principais vendas e aquisições de 2024/25 |
| `divida` | Dívida da SAD por credor e maturidade (30/06/2025) |
| `fonte` · `evento` | Proveniência dos dados e acontecimentos de cada época |
| `v_dr` · `v_kpis` · `v_resultado_por_entidade` | Vistas: pivot da DR, indicadores e comparação entre entidades |
| `v_taxas_epoca` | Vista: taxas de referência e taxa implícita do Vitória por época (julho a junho) |

Os gastos são guardados com sinal negativo, tal como nas demonstrações financeiras. Valores não disponíveis ficam como `NULL`.

### Técnicas SQL

| Técnica | Onde |
|:---|:---|
| CTE recursiva | geração das épocas em `02_dimensoes.sql` |
| `LAG`, `RANK`, `ROW_NUMBER`, `FIRST_VALUE` | consultas 1, 3, 13 e 16 |
| `SUM() OVER (PARTITION BY …)` e médias móveis | consultas 5, 7 e 12 |
| Pivot com `CASE` | vistas `v_dr` e `v_resultado_por_entidade` |
| Self-join e `UNION ALL` | consultas 11, 14 e 19 |
| Restrições `CHECK` e chaves estrangeiras | `01_schema.sql` |
| Auditoria de qualidade dos dados | consultas 17 a 19 e 35, `scripts/testes.py` |
| Bisseção com CTE recursiva (taxa de crescimento sem `ln`/`exp`) | consulta 9 |
| Correlação de Pearson em SQL (`sqrt`) | consulta 22 |
| Cenários com `VALUES` e parâmetros | consulta 26 |
| Taxa de juro implícita com `LAG` e médias | consulta 27 |
| Rácios financeiros e classificação com `CASE` | consultas 29, 30 e 37 |
| Médias móveis de 3 anos (`ROWS BETWEEN 2 PRECEDING`) | consulta 45 (rácio UEFA) |
| Prazos médios e fundo de maneio | consulta 38 |
| Simulação de repartição com CTE recursiva (1.º a 18.º lugar) | consulta 48 |
| Agregação condicional (`SUM(CASE …)`, `COUNT(DISTINCT)`) | consultas 44 e 50 |
| Média ponderada por dias com `LEAD` e `julianday` (taxa do BCE por época) | vista `v_taxas_epoca` |
| Regressão linear por mínimos quadrados, R², erro-padrão, intervalo de confiança e resíduos em SQL | consulta 53 |
| Cenários cruzados (`VALUES` × `VALUES`) | consulta 55 |

<a id="como-usar"></a>
<img src="graficos/cabecalhos/06_como-usar.png" alt="Como usar" width="100%">

**Versão HTML.** O ficheiro [`html/contas-vitoria.html`](html/contas-vitoria.html) junta o README, as três análises, os gráficos e uma consola SQL que corre a base de dados no browser. Descarrega-o e abre-o num browser (Chrome, Safari, Firefox ou Edge). Funciona sem internet: o SQLite também vai embutido. Só o diagrama do modelo de dados precisa de ligação.

**Versão web para editar no VS Code.** A pasta [`site/`](site/) tem o mesmo conteúdo em ficheiros separados: `index.html`, `css/style.css` e `js/app.js`, com os gráficos em `img/` e as letras em `fontes/`. Abre a pasta no Visual Studio Code e usa a extensão Live Server (*Go Live*); as instruções estão em [`site/LEIA-ME.md`](site/LEIA-ME.md).

A base de dados `vsc_contas.db` já vem incluída e abre diretamente no [DB Browser for SQLite](https://sqlitebrowser.org/), no DBeaver ou em qualquer cliente SQLite.

**Requisitos.** Python 3.10 ou mais recente (testado com 3.13) e SQLite 3.35 ou mais recente (testado com 3.45, o que vem com o Python). O dialeto é **SQLite**: as consultas usam CTE recursivas, funções de janela e `sqrt()`, e foram escritas para correr também no sql.js do browser (por isso não usam `ln()` nem `pow()`).

Para reconstruir e validar tudo com um só comando:

```bash
pip install -r requirements.txt
python scripts/construir.py            # base de dados, consultas, testes, dicionário, gráficos e HTML
python scripts/construir.py --rapido   # só base de dados, consultas e testes (sem dependências externas)
```

O comando pára no primeiro erro. Os passos também podem correr um a um:

```bash
python scripts/build_db.py          # cria vsc_contas.db (só biblioteca padrão)
python scripts/correr_analises.py   # corre as 59 consultas e gera resultados.md
python scripts/testes.py            # testes de qualidade e reconciliação → testes.md
python scripts/dicionario.py        # dicionário de dados → dicionario-dados.md
python scripts/graficos.py          # gera os gráficos em graficos/
python scripts/cabecalhos.py        # gera as faixas de título do README
python scripts/gerar_html.py --site # gera html/contas-vitoria.html e a pasta site/
python scripts/relatorio_pdf.py     # gera o relatório PDF (requer: pip install playwright; playwright install chromium)
```

**Qualidade e reconciliação.** [`testes.md`](testes.md) mostra o resultado dos testes: integridade (chaves e épocas), coerência contabilística (ativo = passivo + capital próprio, subtotais, movimentos do plantel), reconciliação de 17 números citados nos relatórios com a base de dados, e execução das 59 consultas. Os avisos explicam os casos conhecidos (valores repetidos na fonte, diferenças de arredondamento). O [dicionário de dados](dicionario-dados.md) descreve as 31 tabelas e vistas, coluna a coluna, com unidades, sinais e proveniência.

**Integração contínua.** O ficheiro [`ci/contas-vitoria-sql.yml`](ci/contas-vitoria-sql.yml) é uma GitHub Action que reconstrói a base e corre os testes sempre que algo muda nesta pasta. Para a ativar, copia-o para `.github/workflows/` na raiz do repositório.

**Resolução de problemas**

| Sintoma | Causa e solução |
|:---|:---|
| `ModuleNotFoundError: matplotlib` ou `markdown` | Falta instalar as dependências: `pip install -r requirements.txt`. A base de dados, as consultas e os testes não precisam delas. |
| `no such function: sqrt` | SQLite antigo, sem funções matemáticas (anterior a 3.35). Atualiza o Python ou usa a versão HTML. |
| Os gráficos saem com outra letra | A pasta `fontes/` tem de estar ao lado de `scripts/`. |
| A consola SQL do `site/` não abre | Abre a pasta com o Live Server do VS Code, ou o `index.html` diretamente num browser recente. |

Exemplo: o resultado da SAD com e sem vendas de jogadores.

```sql
SELECT epoca_id,
       resultado_liquido,
       mais_valias_liquidas,
       resultado_liquido - mais_valias_liquidas AS rl_sem_mais_valias
FROM v_kpis
WHERE entidade_id = 'SAD' AND mais_valias_liquidas IS NOT NULL
ORDER BY epoca_id;
```

### Estrutura

```
contas-vitoria-sql/
├── data/                   Dados em CSV (um ficheiro por tabela)
├── sql/
│   ├── 01_schema.sql       Tabelas, chaves e restrições
│   ├── 02_dimensoes.sql    Épocas, entidades e rubricas
│   ├── 03_vistas.sql       Vistas reutilizáveis
│   └── 04_analises.sql     59 consultas de análise
├── scripts/
│   ├── construir.py        Reconstrói e valida tudo com um comando
│   ├── build_db.py         Constrói vsc_contas.db
│   ├── correr_analises.py  Gera resultados.md
│   ├── testes.py           Testes de qualidade e reconciliação → testes.md
│   ├── dicionario.py       Gera dicionario-dados.md
│   ├── graficos.py         Gera os gráficos
│   ├── cabecalhos.py       Gera as faixas de título do README
│   ├── gerar_html.py       Gera a versão HTML
│   ├── relatorio_pdf.py    Gera o relatório PDF (com modelo_relatorio.html)
│   ├── modelo.html         Modelo da versão HTML
│   └── vendor/             sql.js (SQLite em WebAssembly, licença MIT)
├── graficos/               Gráficos PNG (e cabecalhos/ com as faixas)
├── ci/                     GitHub Action com os testes (copiar para .github/workflows/)
├── relatorio/              Relatório PDF "Rendimentos, gastos e transferências", fonte HTML e gráficos
├── html/                   Versão HTML autónoma, com consola SQL
├── site/                   Versão web em HTML, CSS e JavaScript separados
├── fontes/                 Archivo e Archivo Expanded (licença OFL)
├── resultados.md           Resultados das consultas
├── testes.md               Relatório dos testes
├── dicionario-dados.md     Tabelas, colunas, unidades e proveniência
├── analise-estrategica.md  Diagnóstico e recomendações
├── analise-tecnica.md      17 conceitos, indicadores, juros e cenários
├── verificacao-fontes.md   Conferência com os Relatórios e Contas
└── vsc_contas.db           Base de dados pronta a usar
```

<a id="fontes-e-limitações"></a>
<img src="graficos/cabecalhos/07_fontes-e-limitacoes.png" alt="Fontes e limitações" width="100%">

Os dados financeiros vêm de duas fontes:

- **Relatórios e Contas da Vitória SC – Futebol, SAD de 2012/13 a 2025/26** ([vitoriasc.pt/documentos](https://vitoriasc.pt/documentos/)): balanço, dívida financeira, juros, número de funcionários e gastos com pessoal da SAD, verificados documento a documento (ver [verificação das fontes](verificacao-fontes.md)).
- **[VSC Contas](https://vitoriasempre.net/contas-vsc/)**, um dashboard não oficial: demonstração de resultados detalhada, composição das receitas, transferências, Clube e consolidado. Os balanços da SAD de 2014/15 a 2016/17 publicados no site estavam errados e foram substituídos pelos dos R&C.

As consultas de qualidade (17 a 19) revelam limitações que convém conhecer:

- **Cobertura desigual.** A SAD tem a demonstração de resultados completa em quase todas as épocas. O Clube só tem dados detalhados a partir de 2021/22. O consolidado começa em 2017/18.
- **Valores repetidos.** Os direitos TV têm exatamente 6 922 619 € em quatro épocas seguidas. A nota 15 do R&C 2025/26 confirma esse valor em 2024/25 e 2025/26: é o valor fixo do contrato, não um valor de preenchimento. "Outros" repete-se em 2023/24 e 2024/25, o que continua por confirmar.
- **Números diferentes para a mesma coisa.** As mais-valias da página da SAD diferem das da página consolidada em cinco épocas. As duas versões estão guardadas, cada uma com a entidade de origem.
- **Composição das receitas.** Os totais coincidem com os rendimentos operacionais *consolidados*, por isso foram associados ao Grupo.
- **Rácio de custos do plantel.** A consulta 45 segue a fórmula da UEFA, mas sem as comissões de agentes (não há dados separados), por isso subestima o rácio.
- **Simulações.** A centralização dos direitos TV (consulta 48) usa um mérito linear e ignora as audiências; o valor de mercado do plantel (Transfermarkt) só existe para 2026; os treinadores vêm da Wikipédia. São ordens de grandeza, não previsões.
- **Contas reexpressas.** O R&C 2025/26 reexpressou 2024/25 (resultado de 7,36 M€ em vez de 7,61 M€; capital próprio de (25,8 M€) em vez de (24,0 M€)) e reclassificou os fluxos de caixa. Esta base usa, para cada época, os valores do seu próprio relatório, para que as séries sejam comparáveis com o que foi publicado na altura. Os valores reexpressos estão na tabela `reexpressao` (consulta 36). Por isso, o valor do plantel no fim de 2024/25 (10,4 M€) não coincide com o valor inicial de 2025/26 (9,6 M€, reexpresso).
- **2025/26.** O R&C 2025/26 foi aprovado pelo Conselho de Administração a 26/10/2026 e ainda está sujeito a aprovação da Assembleia Geral. Os juros suportados (7,08 M€) passaram a incluir o efeito financeiro do custo amortizado; para a taxa implícita usam-se só os juros dos financiamentos (5,61 M€, nota 4.7), comparáveis com as épocas anteriores. Ainda não há contas do Clube nem do Grupo consolidado para 2025/26, nem a composição consolidada das receitas.
- **Dados desportivos.** Classificações e campanhas europeias recolhidas da Wikipédia e do Maisfutebol; pontos só disponíveis para as três últimas épocas. As médias de espectadores vêm da compilação do autor.
- **Juros.** A tabela `balanco_sad_rc` guarda os juros suportados brutos, tal como nos R&C. A rubrica "juros" da demonstração de resultados (origem: VSC Contas) é, nalgumas épocas, líquida dos juros obtidos. A taxa de juro implícita inclui encargos de factoring e de antecipação de receitas, por isso fica acima da taxa nominal dos empréstimos.
- **Taxas de referência.** BCE (taxas diretoras), euribor-rates.eu (Euribor a 12 meses, primeiro dia útil de cada mês), OCDE via FRED (obrigações do Estado português a 10 anos) e Banco de Portugal (crédito novo a empresas, só os meses que foi possível recolher). A taxa implícita do Vitória não é diretamente comparável a uma taxa nominal, porque inclui comissões de factoring e antecipação.
- **Funcionários.** São números médios anuais. Em 2012/13 são os funcionários transferidos para a SAD em abril de 2013 (época parcial). A categoria "pessoal de apoio ao futebol profissional" só existe desde 2021/22.

<a id="identidade-visual"></a>
<img src="graficos/cabecalhos/08_identidade-visual.png" alt="Identidade visual" width="100%">

Os gráficos seguem a paleta dos documentos financeiros do clube: amarelo `#F5D510`, preto `#111111` e cinzentos `#6F6D6E` e `#EBEBEB`. Os valores negativos aparecem entre parênteses. Como o Markdown do GitHub não permite escolher tipos de letra, os títulos das secções deste README são imagens geradas por `scripts/cabecalhos.py`. O relatório PDF usa o emblema do Vitória Sport Clube, propriedade do clube, apenas para identificar o clube analisado. A tipografia é a [Archivo](https://fonts.google.com/specimen/Archivo), da Omnibus-Type: Archivo Expanded nos títulos e Archivo no texto. Os ficheiros estão na pasta `fontes/` (SIL Open Font License), para que os gráficos saiam iguais em qualquer computador.

---

<p align="center"><sub>Projeto de <b>João Garção</b> · Mestrado em Humanidades Digitais, Universidade do Minho</sub></p>

---

**Direitos:** todos os direitos reservados aos autores indicados neste documento, salvo indicação em contrário. Ver [LICENSE.md](../../../LICENSE.md).  
**Rights:** all rights reserved by the authors named in this document, unless stated otherwise. See [LICENSE.md](../../../LICENSE.md).
