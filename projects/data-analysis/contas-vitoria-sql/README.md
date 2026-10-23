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
  <a href="analise-estrategica.md">Análise estratégica</a> ·
  <a href="verificacao-fontes.md">Verificação das fontes</a> ·
  <a href="#modelo-de-dados">Modelo de dados</a> ·
  <a href="#como-usar">Como usar</a> ·
  <a href="#fontes-e-limitações">Fontes e limitações</a>
</p>

---

## Resumo

Base de dados **SQLite** com as contas do **Vitória Sport Clube** em três perspetivas: a **SAD** (futebol profissional), o **Clube** (associação-mãe) e o **Grupo consolidado**. Cobre 14 épocas, de 2012/13 a 2025/26, e cruza as contas com os resultados desportivos de cada época.

Sobre essa base, **35 consultas SQL** respondem a uma pergunta central: *as contas do Vitória são sustentáveis sem a venda de jogadores?*

**→ Lê a [análise estratégica](analise-estrategica.md)**: diagnóstico, comparação com o desempenho desportivo, enquadramento (regras da UEFA, centralização dos direitos TV, custo da dívida) e 12 recomendações com cenários.

**✓ Dados verificados.** O balanço, a dívida, os juros e o pessoal da SAD foram conferidos com os 13 Relatórios e Contas de 2012/13 a 2024/25 (incluindo os digitalizados, lidos com OCR). A [verificação das fontes](verificacao-fontes.md) documenta 40 divergências encontradas em fontes secundárias e o que foi corrigido.

> Projeto pessoal e autodidata de análise de dados. Não tem qualquer ligação oficial ao Vitória Sport Clube.

## Indicadores-chave · SAD

| Indicador | 2023/24 | 2024/25 | 2025/26 |
|:---|---:|---:|---:|
| Lugar na Liga · Europa | 5.º · pré-eliminatória | 6.º · oitavos da Liga Conferência | 9.º · sem Europa |
| Receitas (vendas e serviços / operacionais) | 12,9 M€ | **22,6 M€** | 15,1 M€ |
| Gastos com pessoal | (16,9 M€) | (20,5 M€) | — |
| Mais-valias com jogadores | 6,7 M€ | **27,5 M€** | — |
| **Resultado líquido** | **(14,7 M€)** | **7,6 M€** | **(11,1 M€)** |
| Resultado sem mais-valias | (21,4 M€) | (19,9 M€) | — |
| Capital próprio | (31,2 M€) | (24,0 M€) | (36,8 M€) |

<sub>Valores negativos entre parênteses, como nas demonstrações financeiras. 2025/26: comunicado de contas da SAD (indicadores resumidos, base reexpressa).</sub>

## Principais conclusões

**1. A SAD vive das vendas de jogadores.** Nas oito épocas com dados de transferências, o resultado sem mais-valias seria sempre negativo, entre (5,9 M€) e (25,3 M€). O recorde de 2024/25 só existe graças a 27,5 M€ de mais-valias.

![Dependência das vendas de jogadores](graficos/03_dependencia_vendas_jogadores.png)

**2. Os salários ultrapassaram as receitas durante quatro épocas.** Entre 2020/21 e 2023/24, os gastos com pessoal ficaram entre 119% e 200% das vendas e serviços.

![Receitas vs. gastos com pessoal](graficos/02_receitas_vs_pessoal_sad.png)

**3. A SAD só teve capital próprio positivo em 4 das 14 épocas** (2016/17 a 2019/20). Desde 2020/21, o passivo supera o ativo: o capital próprio chegou a (36,8 M€) a 30/06/2026, e o passivo a 85,3 M€. O rácio de endividamento de 2023/24 (1,87) foi o mais alto da história da SAD.

![Ativo vs. passivo da SAD](graficos/05_balanco_sad.png)

**4. A dívida ficou mais cara e mais curta.** A dívida financeira passou de 1,2 M€ (2019/20) para 34,6 M€ (2024/25), e os juros de 149 mil € para 5,0 M€, cerca de 34 vezes mais. A taxa de juro implícita subiu de cerca de 6% para **15%**, e os juros já pesam 22% das receitas. A 30/06/2025, 92% da dívida financeira vencia em menos de um ano, e a liquidez geral está abaixo de 0,5 desde 2021/22.

![Dívida financeira e juros](graficos/07_divida_e_juros.png)

![Endividamento e liquidez](graficos/08_endividamento_liquidez.png)

**5. Uma época europeia muda tudo.** Com fase de grupos UEFA, as receitas operacionais médias foram de 21,3 M€, contra 14,0 M€ nas restantes épocas.

![Composição das receitas](graficos/04_composicao_receitas.png)

**6. Gastar mais em salários não garantiu melhores classificações.** A correlação entre gastos com pessoal e lugar na Liga é fraca (−0,3). O 4.º lugar de 2016/17 custou 6,8 M€ em pessoal; o 7.º lugar de 2020/21 custou 20,7 M€.

![Salários vs. classificação](graficos/06_salarios_vs_classificacao.png)

**7. A estrutura cresceu mais depressa do que a equipa.** A SAD passou de 59 funcionários em 2012/13 para **229 em 2024/25**, um recorde. Os jogadores quase duplicaram (42 → 82), mas o restante pessoal (treinadores, staff e apoio) multiplicou-se por mais de 8 (17 → 147). Hoje há 1,8 não-jogadores por cada jogador, contra 0,4 em 2012/13. A remuneração média por jogador subiu de 80 mil € (2016/17) para 134 mil € (2024/25).

![Funcionários da SAD](graficos/09_funcionarios.png)

**8. O Clube e a SAD têm perfis opostos.** O Clube tem pouco passivo e património valioso (Estádio e Academia), mas prejuízos recorrentes, perto de 1 M€ por ano nas duas últimas épocas. A SAD concentra a dívida e a volatilidade.

![Resultado líquido por entidade](graficos/01_resultado_por_entidade.png)

Os resultados completos das 35 consultas estão em [`resultados.md`](resultados.md). A leitura estratégica está em [`analise-estrategica.md`](analise-estrategica.md).

## Modelo de dados

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
| Auditoria de qualidade dos dados | consultas 17 a 19 e 35 |
| Correlação de Pearson em SQL (`sqrt`) | consulta 22 |
| Cenários com `VALUES` e parâmetros | consulta 26 |
| Taxa de juro implícita com `LAG` e médias | consulta 27 |
| Rácios financeiros e classificação com `CASE` | consultas 29 e 30 |

## Como usar

A base de dados `vsc_contas.db` já vem incluída e abre diretamente no [DB Browser for SQLite](https://sqlitebrowser.org/), no DBeaver ou em qualquer cliente SQLite.

Para reconstruir tudo do zero:

```bash
python scripts/build_db.py          # cria vsc_contas.db (só biblioteca padrão)
python scripts/correr_analises.py   # corre as 35 consultas e gera resultados.md
pip install -r requirements.txt
python scripts/graficos.py          # gera os gráficos em graficos/
```

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
│   └── 04_analises.sql     35 consultas de análise
├── scripts/
│   ├── build_db.py         Constrói vsc_contas.db
│   ├── correr_analises.py  Gera resultados.md
│   └── graficos.py         Gera os gráficos
├── graficos/               Gráficos PNG
├── fontes/                 Archivo e Archivo Expanded (licença OFL)
├── resultados.md           Resultados das consultas
├── analise-estrategica.md  Diagnóstico e recomendações
├── verificacao-fontes.md   Conferência com os Relatórios e Contas
└── vsc_contas.db           Base de dados pronta a usar
```

## Fontes e limitações

Os dados vêm de duas fontes:

- **Relatórios e Contas da Vitória SC – Futebol, SAD de 2012/13 a 2024/25** ([vitoriasc.pt/documentos](https://vitoriasc.pt/documentos/)): balanço, dívida financeira, juros, número de funcionários e gastos com pessoal da SAD, verificados documento a documento (ver [verificação das fontes](verificacao-fontes.md)).
- **[VSC Contas](https://vitoriasempre.net/contas-vsc/)**, um dashboard não oficial: demonstração de resultados detalhada, composição das receitas, transferências, Clube e consolidado. Os balanços da SAD de 2014/15 a 2016/17 publicados no site estavam errados e foram substituídos pelos dos R&C.

As consultas de qualidade (17 a 19) revelam limitações que convém conhecer:

- **Cobertura desigual.** A SAD tem a demonstração de resultados completa em quase todas as épocas. O Clube só tem dados detalhados a partir de 2021/22. O consolidado começa em 2017/18.
- **Valores repetidos.** Os direitos TV têm exatamente 6 922 619 € em quatro épocas seguidas, e "Outros" repete-se em 2023/24 e 2024/25. Provavelmente são valores de preenchimento e não dados reais.
- **Números diferentes para a mesma coisa.** As mais-valias da página da SAD diferem das da página consolidada em cinco épocas. As duas versões estão guardadas, cada uma com a entidade de origem.
- **Composição das receitas.** Os totais coincidem com os rendimentos operacionais *consolidados*, por isso foram associados ao Grupo.
- **Rácio pessoal/receitas.** É uma aproximação simples. A regra de custos do plantel da UEFA usa outra base de cálculo.
- **Contas reexpressas e 2025/26.** A SAD reexpressou os valores de 2024/25 nas contas de 2025/26 (resultado de 7,4 M€ em vez de 7,6 M€). Esta base usa os valores originalmente publicados para 2024/25; os valores reexpressos estão na tabela `evento`. Para 2025/26 só existem os indicadores resumidos do comunicado de contas, cujas rubricas não coincidem todas com as dos anos anteriores.
- **Dados desportivos.** Classificações e campanhas europeias recolhidas da Wikipédia e do Maisfutebol; pontos só disponíveis para as três últimas épocas. As médias de espectadores vêm da compilação do autor.
- **Juros.** A tabela `balanco_sad_rc` guarda os juros suportados brutos, tal como nos R&C. A rubrica "juros" da demonstração de resultados (origem: VSC Contas) é, nalgumas épocas, líquida dos juros obtidos. A taxa de juro implícita inclui encargos de factoring e de antecipação de receitas, por isso fica acima da taxa nominal dos empréstimos.
- **Funcionários.** São números médios anuais. Em 2012/13 são os funcionários transferidos para a SAD em abril de 2013 (época parcial). A categoria "pessoal de apoio ao futebol profissional" só existe desde 2021/22.

## Identidade visual

Os gráficos seguem a paleta dos documentos financeiros do clube: amarelo `#F5D510`, preto `#111111` e cinzentos `#6F6D6E` e `#EBEBEB`. Os valores negativos aparecem entre parênteses. A tipografia é a [Archivo](https://fonts.google.com/specimen/Archivo), da Omnibus-Type: Archivo Expanded nos títulos e Archivo no texto. Os ficheiros estão na pasta `fontes/` (SIL Open Font License), para que os gráficos saiam iguais em qualquer computador.

---

<p align="center"><sub>Projeto de <b>João Garção</b> · Mestrado em Humanidades Digitais, Universidade do Minho</sub></p>
