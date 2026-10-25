# Dicionário de dados

Gerado por `scripts/dicionario.py` a partir de `vsc_contas.db` e dos comentários do esquema.

## Convenções

| Tema | Regra |
|:---|:---|
| Dialeto | SQLite 3 (testado com 3.45). As consultas só usam funções que também existem no sql.js do browser. |
| Unidades | Valores monetários em **euros inteiros** (arredondados ao euro na carga). Taxas de juro em **percentagem** (2,5 = 2,5%). |
| Sinais | Gastos com sinal **negativo**, como nas demonstrações de resultados. Em `v_kpis`, `gastos_pessoal` e `juros` passam a positivos. |
| Épocas | Texto `AAAA/AA` (por exemplo `2024/25`). O exercício fecha a 30 de junho do segundo ano. |
| Entidades | `SAD` (Vitória SC – Futebol, SAD), `CLUBE` (associação) e `CONSOLIDADO` (Grupo). |
| Em falta | `NULL` = dado não disponível na fonte. Nunca se usa 0 para "desconhecido". |
| Proveniência | Coluna `documento` (relatório e nota de origem) nas tabelas verificadas nos R&C; tabela `fonte` para as restantes; `divergencia` regista os valores das fontes secundárias que foram substituídos. |

## Índice

[`auditoria`](#auditoria) · [`balanco`](#balanco) · [`balanco_rubrica`](#balanco_rubrica) · [`balanco_sad_rc`](#balanco_sad_rc) · [`bce_taxa`](#bce_taxa) · [`cash_flow`](#cash_flow) · [`demonstracao_resultados`](#demonstracao_resultados) · [`desempenho_desportivo`](#desempenho_desportivo) · [`divergencia`](#divergencia) · [`divida`](#divida) · [`entidade`](#entidade) · [`epoca`](#epoca) · [`evento`](#evento) · [`financiamento_detalhe`](#financiamento_detalhe) · [`fonte`](#fonte) · [`gastos_pessoal_composicao`](#gastos_pessoal_composicao) · [`operacao_jogador`](#operacao_jogador) · [`partes_relacionadas`](#partes_relacionadas) · [`passes_jogadores`](#passes_jogadores) · [`pessoal_sad`](#pessoal_sad) · [`receitas_composicao`](#receitas_composicao) · [`reexpressao`](#reexpressao) · [`rubrica`](#rubrica) · [`taxa_referencia`](#taxa_referencia) · [`transferencias`](#transferencias) · [`treinador`](#treinador) · [`v_dr`](#v_dr) · [`v_kpis`](#v_kpis) · [`v_resultado_por_entidade`](#v_resultado_por_entidade) · [`v_taxas_epoca`](#v_taxas_epoca)

## `auditoria`

*Tabela · 13 linhas · épocas 2012/13 a 2024/25*

Parecer do auditor (certificação legal de contas) e artigo 35.º do CSC

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `parecer_auditor` | TEXT |  |  | Tipo de opinião e ênfases da certificação legal de contas |
| `artigo_35_no_relatorio` | INTEGER |  |  | 1 se o relatório refere o artigo 35.º do CSC |
| `nota` | TEXT |  |  | Observação sobre o valor ou a época |

## `balanco`

*Tabela · 34 linhas · épocas 2012/13 a 2025/26*

Balanço a 30/06 de cada época (NULL = não disponível)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT | PK · FK → `entidade.entidade_id` |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `ativo_total` | INTEGER |  | 11 | Ativo total a 30/06 (€) |
| `passivo_total` | INTEGER |  |  | Passivo total a 30/06 (€) |
| `capital_proprio` | INTEGER |  | 11 | no Clube: fundos patrimoniais |
| `caixa` | INTEGER |  | 19 | Caixa e depósitos bancários a 30/06 (€) |

## `balanco_rubrica`

*Tabela · 159 linhas · épocas 2016/17 a 2024/25*

Balanço da SAD por rubrica (formato longo), 2016/17 a 2024/25

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `lado` | TEXT | PK |  | `ativo` ou `passivo` |
| `prazo` | TEXT | PK |  | `corrente` ou `nao_corrente` |
| `rubrica` | TEXT | PK |  | Rubrica do balanço ou da transação |
| `valor` | INTEGER |  |  | Valor em euros |

## `balanco_sad_rc`

*Tabela · 13 linhas · épocas 2012/13 a 2024/25*

Balanço detalhado da SAD tal como publicado nos Relatórios e Contas, com dívida financeira e juros (verificado documento a documento)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `ativo_nao_corrente` | INTEGER |  |  | Ativo não corrente (€) |
| `ativo_corrente` | INTEGER |  |  | Ativo corrente (€) |
| `ativo_total` | INTEGER |  |  | Ativo total a 30/06 (€) |
| `passivo_nao_corrente` | INTEGER |  |  | Passivo não corrente (€) |
| `passivo_corrente` | INTEGER |  |  | Passivo corrente, a menos de um ano (€) |
| `passivo_total` | INTEGER |  |  | Passivo total a 30/06 (€) |
| `capital_proprio` | INTEGER |  |  | Capital próprio = ativo − passivo (€); no Clube, fundos patrimoniais |
| `caixa` | INTEGER |  |  | Caixa e depósitos bancários a 30/06 (€) |
| `financiamentos_nc` | INTEGER |  | 4 | financiamentos obtidos não correntes |
| `financiamentos_c` | INTEGER |  | 4 | financiamentos obtidos correntes |
| `juros_suportados` | INTEGER |  | 1 | valor bruto, positivo |
| `juros_obtidos` | INTEGER |  | 7 | Juros obtidos (€) |
| `documento` | TEXT |  |  | Documento e nota de origem (Relatório e Contas) |

## `bce_taxa`

*Tabela · 25 linhas*

Alterações das taxas diretoras do BCE (em vigor a partir de data_efeito).

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `data_efeito` | TEXT | PK |  | Data a partir da qual a taxa vigora |
| `facilidade_deposito` | REAL |  |  | Taxa da facilidade permanente de depósito do BCE (%) |
| `refinanciamento` | REAL |  |  | Taxa das operações principais de refinanciamento do BCE (%) |

## `cash_flow`

*Tabela · 12 linhas · épocas 2013/14 a 2024/25*

Fluxos de caixa (só SAD)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT | PK · FK → `entidade.entidade_id` |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `operacional` | INTEGER |  |  | Fluxo de caixa das atividades operacionais (€) |
| `investimento` | INTEGER |  |  | Fluxo de caixa das atividades de investimento (€) |
| `financiamento` | INTEGER |  |  | Fluxo de caixa das atividades de financiamento (€) |

## `demonstracao_resultados`

*Tabela · 293 linhas · épocas 2012/13 a 2025/26*

Demonstração de resultados em formato longo (uma linha por rubrica)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT | PK · FK → `entidade.entidade_id` |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `rubrica_id` | TEXT | PK · FK → `rubrica.rubrica_id` |  | Identificador da rubrica da demonstração de resultados |
| `valor` | INTEGER |  |  | Valor em euros |

## `desempenho_desportivo`

*Tabela · 14 linhas · épocas 2012/13 a 2025/26*

Desempenho desportivo da equipa principal em cada época

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `posicao_liga` | INTEGER |  |  | Lugar final na I Liga |
| `pontos` | INTEGER |  |  | Pontos na I Liga |
| `media_espectadores` | INTEGER |  | 1 | média em casa na Liga (0 = COVID) |
| `competicao_europeia` | TEXT |  | 7 | NULL = sem Europa |
| `fase_europeia` | TEXT |  | 7 | Fase mais avançada atingida na Europa |
| `trofeu` | TEXT |  | 12 | Troféu conquistado na época |
| `nota` | TEXT |  | 12 | Observação sobre o valor ou a época |

## `divergencia`

*Tabela · 40 linhas · épocas 2014/15 a 2023/24*

Divergências encontradas entre fontes secundárias e os Relatórios e Contas

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `divergencia_id` | INTEGER | PK |  | Identificador |
| `fonte` | TEXT |  |  | Origem do valor |
| `epoca_id` | TEXT | FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `indicador` | TEXT |  |  | Nome do indicador |
| `valor_fonte` | REAL |  |  | Valor na fonte secundária |
| `valor_rc` | REAL |  |  | Valor nos Relatórios e Contas |
| `diferenca` | REAL |  |  | valor_fonte − valor_rc |
| `nota` | TEXT |  | 4 | Observação sobre o valor ou a época |

## `divida`

*Tabela · 6 linhas*

Dívida da SAD por credor e maturidade

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `data_ref` | TEXT | PK |  | 'AAAA-MM-DD' |
| `credor` | TEXT | PK |  | Entidade credora |
| `tipo` | TEXT |  |  | Tipo de registo |
| `total` | INTEGER |  |  | Montante total em dívida (€) |
| `menos_1_ano` | INTEGER |  | 2 | Parte que vence em menos de um ano (€) |
| `entre_1_3_anos` | INTEGER |  | 2 | Parte que vence entre um e três anos (€) |
| `mais_3_anos` | INTEGER |  | 2 | Parte que vence a mais de três anos (€) |
| `nota` | TEXT |  |  | Observação sobre o valor ou a época |

## `entidade`

*Tabela · 3 linhas*

As três "vistas" do Vitória: SAD, Clube e Grupo consolidado

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT | PK |  | 'SAD' | 'CLUBE' | 'CONSOLIDADO' |
| `nome` | TEXT |  |  | Nome legível |
| `descricao` | TEXT |  |  | Texto descritivo |

## `epoca`

*Tabela · 14 linhas · épocas 2012/13 a 2025/26*

Época desportiva (o exercício fecha a 30 de junho do ano_fim)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK |  | '2024/25' |
| `ano_inicio` | INTEGER |  |  | Ano em que a época começa (1 de julho) |
| `ano_fim` | INTEGER |  |  | Ano em que a época termina (30 de junho) |

## `evento`

*Tabela · 51 linhas · épocas 2013/14 a 2025/26*

Acontecimentos e observações relevantes de cada época

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `evento_id` | INTEGER | PK |  | Identificador |
| `entidade_id` | TEXT | FK → `entidade.entidade_id` |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT | FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `tipo` | TEXT |  |  | Tipo de registo |
| `descricao` | TEXT |  |  | Texto descritivo |
| `valor` | INTEGER |  | 23 | Valor em euros |

## `financiamento_detalhe`

*Tabela · 8 linhas*

Dívida financeira por instrumento e maturidade

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `data_ref` | TEXT | PK |  | Data de referência (AAAA-MM-DD) |
| `instrumento` | TEXT | PK |  | Empréstimos, factoring, Apollo ou locações financeiras |
| `total` | INTEGER |  |  | Montante total em dívida (€) |
| `menos_1_ano` | INTEGER |  |  | Parte que vence em menos de um ano (€) |
| `entre_1_3_anos` | INTEGER |  |  | Parte que vence entre um e três anos (€) |
| `documento` | TEXT |  |  | Documento e nota de origem (Relatório e Contas) |

## `fonte`

*Tabela · 34 linhas · épocas 2012/13 a 2025/26*

Proveniência e estado dos dados de cada página/época

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT | PK · FK → `entidade.entidade_id` |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `estado` | TEXT |  |  | Estado dos dados nesta fonte |
| `documentos` | TEXT |  |  | Documentos de origem |

## `gastos_pessoal_composicao`

*Tabela · 24 linhas · épocas 2017/18 a 2024/25*

Composição dos gastos com pessoal (valores consolidados)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT | PK · FK → `entidade.entidade_id` |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `categoria` | TEXT | PK |  | Categoria da receita ou do gasto |
| `valor` | INTEGER |  |  | Valor em euros |

## `operacao_jogador`

*Tabela · 11 linhas · épocas 2024/25 a 2024/25*

Principais vendas e aquisições individuais

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `operacao_id` | INTEGER | PK |  | Identificador da operação |
| `epoca_id` | TEXT | FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `jogador` | TEXT |  |  | Nome do jogador |
| `tipo` | TEXT |  |  | Tipo de registo |
| `clube` | TEXT |  | 7 | clube de destino (vendas) |

## `partes_relacionadas`

*Tabela · 26 linhas · épocas 2020/21 a 2024/25*

Transações e saldos entre a SAD e o Clube (partes relacionadas)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `rubrica` | TEXT | PK |  | Rubrica do balanço ou da transação |
| `sentido` | TEXT |  |  | `receita da SAD`, `gasto da SAD` ou `saldo` |
| `valor` | INTEGER |  |  | Valor em euros |
| `documento` | TEXT |  |  | Documento e nota de origem (Relatório e Contas) |

## `passes_jogadores`

*Tabela · 8 linhas · épocas 2017/18 a 2024/25*

Movimentos dos passes de jogadores (ativos intangíveis), nota 7 dos R&C

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `valor_liquido_inicio` | INTEGER |  |  | Valor contabilístico do plantel no início da época (€) |
| `aquisicoes` | INTEGER |  |  | Passes adquiridos na época (€) |
| `amortizacoes` | INTEGER |  |  | Amortizações dos passes na época (€) |
| `valor_bruto_alienado` | INTEGER |  |  | Custo de aquisição dos passes vendidos (€) |
| `amort_acumuladas_alienadas` | INTEGER |  |  | Amortizações acumuladas dos passes vendidos (€) |
| `rescisoes_bruto` | INTEGER |  |  | Custo de aquisição dos contratos rescindidos (€) |
| `rescisoes_amort_acumuladas` | INTEGER |  |  | Amortizações acumuladas dos contratos rescindidos (€) |
| `valor_liquido_fim` | INTEGER |  |  | Valor contabilístico do plantel no fim da época (€) |
| `documento` | TEXT |  |  | Documento e nota de origem (Relatório e Contas) |

## `pessoal_sad`

*Tabela · 13 linhas · épocas 2012/13 a 2024/25*

Número médio de funcionários e gastos com pessoal da SAD (nota "Benefícios dos empregados")

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `funcionarios` | INTEGER |  |  | Número médio de funcionários da SAD |
| `jogadores` | INTEGER |  |  | Número médio de jogadores |
| `treinadores_profissional` | INTEGER |  |  | Treinadores e staff técnico do futebol profissional |
| `treinadores_formacao` | INTEGER |  |  | Treinadores da formação |
| `apoio_futebol_profissional` | INTEGER |  | 9 | categoria autónoma desde 2021/22 |
| `outro_pessoal` | INTEGER |  |  | Restante pessoal (administrativo e outros) |
| `rem_administracao` | INTEGER |  | 4 | Remunerações dos órgãos sociais (€) |
| `rem_pessoal_administrativo` | INTEGER |  | 4 | Remunerações do pessoal administrativo (€) |
| `rem_treinadores` | INTEGER |  | 4 | Remunerações dos treinadores (€) |
| `rem_jogadores` | INTEGER |  | 4 | Remunerações dos jogadores (€) |
| `rem_apoio_futebol` | INTEGER |  | 11 | Remunerações do pessoal de apoio ao futebol (€) |
| `encargos_remuneracoes` | INTEGER |  |  | Encargos sociais sobre remunerações (€) |
| `seguro_acidentes` | INTEGER |  |  | Seguros de acidentes de trabalho (€) |
| `outros_gastos` | INTEGER |  |  | Outros gastos com pessoal (€) |
| `total_gastos_pessoal` | INTEGER |  |  | Total de gastos com pessoal (€) |
| `documento` | TEXT |  |  | Documento e nota de origem (Relatório e Contas) |

## `receitas_composicao`

*Tabela · 63 linhas · épocas 2018/19 a 2024/25*

Composição das receitas operacionais (os totais coincidem com os rendimentos operacionais consolidados, por isso ficam no CONSOLIDADO)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT | PK · FK → `entidade.entidade_id` |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `categoria` | TEXT | PK |  | Categoria da receita ou do gasto |
| `valor` | INTEGER |  |  | Valor em euros |

## `reexpressao`

*Tabela · 8 linhas · épocas 2024/25 a 2024/25*

Valores de 2024/25 reexpressos nas contas de 2025/26 (custo amortizado)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `indicador` | TEXT | PK |  | Nome do indicador |
| `valor_original` | INTEGER |  |  | Valor publicado no R&C da própria época |
| `valor_reexpresso` | INTEGER |  |  | Valor reexpresso no ano seguinte |
| `documento` | TEXT |  |  | Documento e nota de origem (Relatório e Contas) |

## `rubrica`

*Tabela · 20 linhas*

Linhas da demonstração de resultados

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `rubrica_id` | TEXT | PK |  | Identificador da rubrica da demonstração de resultados |
| `nome` | TEXT |  |  | Nome legível |
| `natureza` | TEXT |  |  | `rendimento`, `gasto` ou `resultado` |
| `ordem` | INTEGER |  |  | Ordem de apresentação na demonstração de resultados |

## `taxa_referencia`

*Tabela · 253 linhas*

Taxas de juro de referência (mercado e crédito), em percentagem.

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `data` | TEXT | PK |  | AAAA-MM-DD (mês da observação) |
| `indicador` | TEXT | PK |  | Nome do indicador |
| `taxa_pct` | REAL |  |  | Taxa em percentagem |
| `fonte` | TEXT |  |  | Origem do valor |

## `transferencias`

*Tabela · 16 linhas · épocas 2017/18 a 2024/25*

Transferências de jogadores (resumo por época)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT | PK · FK → `entidade.entidade_id` |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT | PK · FK → `epoca.epoca_id` |  | Época desportiva, `AAAA/AA` |
| `vendas_brutas` | INTEGER |  | 8 | Valor bruto das vendas de passes de jogadores (€) |
| `custo_vendas` | INTEGER |  | 12 | intermediários, terceiros, solidariedade |
| `mais_valias_liquidas` | INTEGER |  |  | Preço de venda − valor contabilístico − custos da venda (€) |

## `treinador`

*Tabela · 20 linhas*

Treinadores principais e interinos (fonte: Wikipédia)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `treinador_id` | INTEGER | PK |  | Identificador |
| `periodo` | TEXT |  |  | Período no cargo (texto) |
| `nome` | TEXT |  |  | Nome legível |
| `tipo` | TEXT |  |  | Tipo de registo |

## `v_dr`

*Vista · 33 linhas · épocas 2012/13 a 2025/26*

Demonstração de resultados em formato largo (pivot com CASE)

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT |  |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT |  |  | Época desportiva, `AAAA/AA` |
| `vendas_servicos` | — |  | 16 | Vendas e prestações de serviços: receitas da operação (€) |
| `rendimentos_operacionais` | — |  | 25 | Rendimentos operacionais sem operações com jogadores (€; 2025/26) |
| `outros_rendimentos` | — |  | 20 | Outros rendimentos, incluindo mais-valias com jogadores (€) |
| `fse` | — |  | 9 | Fornecimentos e serviços externos (€, negativo) |
| `gastos_pessoal` | — |  | 9 | Gastos com pessoal (€; negativo em `v_dr`, positivo em `v_kpis`) |
| `depreciacoes` | — |  | 9 | Depreciações e amortizações, incluindo passes (€, negativo) |
| `ebitda` | — |  | 23 | Resultado antes de juros, impostos, depreciações e amortizações (€) |
| `ebitda_sem_transferencias` | — |  | 28 | EBITDA sem operações com jogadores (€) |
| `resultado_operacional` | — |  | 19 | Resultado operacional (€) |
| `juros` | — |  | 9 | Juros (€; nalgumas épocas líquidos dos juros obtidos, ver `balanco_sad_rc`) |
| `resultado_liquido` | — |  |  | Resultado líquido do período (€) |

## `v_kpis`

*Vista · 33 linhas · épocas 2012/13 a 2025/26*

Indicadores principais por entidade e época

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `entidade_id` | TEXT |  |  | `SAD`, `CLUBE` ou `CONSOLIDADO` |
| `epoca_id` | TEXT |  |  | Época desportiva, `AAAA/AA` |
| `vendas_servicos` | — |  | 16 | Vendas e prestações de serviços: receitas da operação (€) |
| `gastos_pessoal` | — |  | 9 | Gastos com pessoal (€; negativo em `v_dr`, positivo em `v_kpis`) |
| `resultado_liquido` | — |  |  | Resultado líquido do período (€) |
| `mais_valias_liquidas` | INTEGER |  | 17 | Preço de venda − valor contabilístico − custos da venda (€) |
| `rl_sem_mais_valias` | — |  | 17 | Resultado líquido − mais-valias com jogadores (€) |
| `pct_pessoal_receitas` | — |  | 16 | Gastos com pessoal em % das vendas e serviços |
| `juros` | — |  | 9 | Juros (€; nalgumas épocas líquidos dos juros obtidos, ver `balanco_sad_rc`) |
| `ativo_total` | INTEGER |  | 10 | Ativo total a 30/06 (€) |
| `passivo_total` | INTEGER |  |  | Passivo total a 30/06 (€) |
| `capital_proprio` | INTEGER |  | 10 | Capital próprio = ativo − passivo (€); no Clube, fundos patrimoniais |
| `caixa` | INTEGER |  | 18 | Caixa e depósitos bancários a 30/06 (€) |

## `v_resultado_por_entidade`

*Vista · 14 linhas · épocas 2012/13 a 2025/26*

Resultado líquido das três entidades lado a lado

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | TEXT |  |  | Época desportiva, `AAAA/AA` |
| `rl_sad` | — |  |  | Resultado líquido da SAD (€) |
| `rl_clube` | — |  | 3 | Resultado líquido do Clube (€) |
| `rl_consolidado` | — |  | 6 | Resultado líquido do Grupo (€) |

## `v_taxas_epoca`

*Vista · 10 linhas · épocas 2016/17 a 2025/26*

Taxas de juro por época (julho a junho): referências de mercado e taxa implícita da dívida da SAD. A taxa do BCE é ponderada pelos dias em vigor.

| Coluna | Tipo | Chave | Em falta | Descrição |
|:---|:---|:---|---:|:---|
| `epoca_id` | — |  |  | Época desportiva, `AAAA/AA` |
| `bce_deposito` | — |  |  | Taxa de depósito do BCE, média da época ponderada pelos dias (%) |
| `euribor_12m` | — |  |  | Euribor a 12 meses, média da época (%) |
| `ot_portugal_10a` | — |  |  | Obrigações do Estado português a 10 anos, média da época (%) |
| `credito_empresas_pt` | — |  | 5 | Crédito novo a empresas em Portugal, média dos meses disponíveis (%) |
| `vitoria_implicita` | — |  | 2 | Juros suportados ÷ dívida financeira média da SAD (%) |
| `meses_euribor` | — |  |  | Número de observações mensais da Euribor na época |
