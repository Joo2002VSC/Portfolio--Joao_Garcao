<p align="center">
  <img src="graficos/00_capa.png" alt="As contas do Vitória SC" width="100%">
</p>

# Análise estratégica: finanças, desporto e enquadramento económico

*Como pode o Vitória SC melhorar a sua prestação financeira?*

> Análise independente de João Garção, baseada nos dados deste projeto (consultas 20 a 26 em [`resultados.md`](resultados.md)) e em fontes públicas citadas no fim. As recomendações são opinião do autor. Não têm ligação ao clube nem a qualquer candidatura ou órgão social. Os conceitos técnicos (dívida líquida/EBITDA, factoring, artigo 35.º, regras da UEFA, centralização…) são aprofundados na [análise técnica](analise-tecnica.md).

---

## Sumário executivo

- **O problema é estrutural, não conjuntural.** Em 2025/26 a SAD gastou 33,1 M€ em custos operacionais para 15,1 M€ de rendimentos operacionais: um resultado operacional de **(18,0 M€)** antes de vender jogadores. Sem as depreciações, o EBITDA sem operações com jogadores foi de (17,2 M€).
- **As vendas de jogadores tapam o buraco, mas não chegam.** Para fechar 2025/26 sem prejuízo, a SAD precisava de ganhar **23,7 M€ líquidos com jogadores** num só ano. Só esteve perto disso uma vez (2024/25, com o recorde de 49,5 M€ em vendas brutas).
- **A Europa é a variável que mais mexe nas contas.** A diferença entre 2024/25 e 2025/26 explica-se quase toda pelas receitas UEFA: 9,4 M€ contra 1,2 M€. O resultado passou de +7,4 M€ para (11,1 M€).
- **Gastar mais em salários não comprou classificações.** A correlação entre gastos com pessoal e lugar na Liga é fraca (−0,3). As duas épocas mais caras (2020/21 e 2024/25) acabaram em 7.º e 6.º lugar. O 4.º lugar de 2016/17 custou um terço disso.
- **A dívida é cara e de curto prazo.** A taxa de juro implícita subiu de cerca de 6% para **15%** e os juros já pesam 22% das receitas. 92% da dívida financeira vencia a menos de um ano (30/06/2025). O capital próprio da SAD chegou a **(36,8 M€)**. O auditor sinaliza incerteza material sobre a continuidade.
- **A estrutura cresceu mais depressa do que a equipa.** De 59 funcionários (2012/13) para **229** (2024/25). Os jogadores quase duplicaram, mas o restante pessoal multiplicou-se por mais de 8.
- **Nenhuma medida isolada resolve.** Só a combinação de corte de custos, refinanciamento, receitas comerciais e uma política de vendas planeada torna o modelo sustentável. A Europa deve ser tratada como um bónus, não como base do orçamento.

---

## 1. Diagnóstico: um modelo de negócio deficitário por natureza

A SAD tem duas "contas" diferentes dentro das suas contas:

| Componente (2025/26) | Valor |
|:---|---:|
| Rendimentos operacionais (sem jogadores) | 15,10 M€ |
| Gastos operacionais (sem jogadores, incluindo depreciações) | (33,10 M€) |
| **Resultado operacional sem operações com jogadores** | **(18,00 M€)** |
| Resultado com direitos de atletas | 12,59 M€ |
| Resultados financeiros | (5,60 M€) |
| Imposto sobre o rendimento | (0,05 M€) |
| **Resultado líquido** | **(11,06 M€)** |
| *Para referência:* EBITDA sem operações com jogadores (comunicado) | (17,21 M€) |

<sub>Fonte: comunicado de contas da SAD a 30/06/2026. As linhas somam o resultado líquido: 15,10 − 33,10 + 12,59 − 5,60 − 0,05 = −11,06. O EBITDA publicado exclui as depreciações e amortizações de ativos que não são passes de jogadores, que estão incluídas nos 33,10 M€ de gastos. A diferença, de cerca de 0,79 M€, é deduzida (o comunicado não a discrimina). O teste `rec_2025_26` em `scripts/testes.py` verifica esta soma.</sub>

Isto quer dizer que **a atividade normal do clube (jogar futebol, vender bilhetes, televisão, patrocínios) dá prejuízo todos os anos**. A diferença tem de vir da venda de jogadores. É o modelo de "clube vendedor", comum em Portugal, mas com uma margem de segurança muito pequena:

- Nas oito épocas com dados, **o resultado sem mais-valias foi sempre negativo**, entre (5,9 M€) e (25,3 M€) (consulta 2).
- Os gastos com pessoal ficaram acima das receitas de 2020/21 a 2023/24, num máximo de 200% (consulta 3).
- O passivo da SAD passou de 23,5 M€ em 2019/20 para **85,3 M€** em 2025/26.

![Dependência das vendas](graficos/03_dependencia_vendas_jogadores.png)

## 2. Finanças vs. desempenho desportivo

### 2.1 A Europa paga as contas, mas só quando se chega à fase de grupos

| Tipo de época (SAD) | Épocas | Receita média | Resultado médio |
|:---|:---:|---:|---:|
| Fase de grupos ou mais | 2013/14, 2017/18, 2019/20, 2024/25 | 14,6 M€ | 1,5 M€ |
| Só pré-eliminatórias | 2015/16, 2022/23, 2023/24 | 10,8 M€ | (4,2 M€) |
| Sem Europa | 2014/15, 2016/17, 2018/19, 2020/21, 2021/22 | 10,3 M€ | (3,3 M€) |

<sub>Consulta 21. 2025/26 fica de fora porque os dados disponíveis não separam as vendas e serviços.</sub>

Cair nas pré-eliminatórias **não melhora as contas**: os custos sobem (viagens, prémios, plantel mais largo) e as receitas ficam iguais às de uma época sem Europa. O salto só acontece na fase de grupos ou de liga. Em 2024/25, com a Liga Conferência, as receitas de competições (UEFA e nacionais) chegaram a 9,7 M€, 42% das receitas operacionais.

**Implicação:** orçamentar a contar com a Europa é arriscado, porque o acesso depende de pré-eliminatórias de resultado incerto. 2023/24 é o exemplo: eliminação na 2.ª pré-eliminatória e prejuízo de (14,7 M€).

### 2.2 Mais salários não trouxeram melhores classificações

![Salários vs. classificação](graficos/06_salarios_vs_classificacao.png)

- **Correlação de −0,3** entre gastos com pessoal e lugar na Liga (consulta 22). Há uma ligeira tendência, mas fraca.
- O **4.º lugar de 2016/17** custou 6,8 M€ em pessoal. O **7.º lugar de 2020/21** custou 20,7 M€.
- Entre 2018/19 e 2024/25, o gasto com pessoal quase duplicou (11,6 → 20,5 M€) e o Vitória ficou sempre entre o 5.º e o 7.º lugar.
- Em 2025/26, o clube ganhou a Taça da Liga mas acabou a Liga em **9.º, com 42 pontos**, e falhou a Europa.

**Implicação:** o problema não é só quanto se gasta, mas **como** se gasta. Contratar caro, ter muitos jogadores emprestados e com cláusulas, e trocar de treinador a meio da época (três treinadores em 2024/25) reduz a eficiência de cada euro.

### 2.3 Vender é necessário, mas está a render menos do que podia

- Em 2024/25, de 49,5 M€ em vendas brutas, ficaram no clube 27,5 M€ (**56%**). 17,3 M€ foram para intermediários, terceiros e mecanismo de solidariedade (consulta 12).
- A SAD devia **21,2 M€ a intermediários** a 30/06/2025, três vezes mais do que a clubes vendedores.
- O Presidente reconheceu no R&C 2024/25 a "obrigação de vender importantes ativos em janeiro". Vender por necessidade de tesouraria baixa o preço.

### 2.4 A estrutura cresceu mais depressa do que a equipa

![Funcionários da SAD](graficos/09_funcionarios.png)

| Época | Funcionários | Jogadores | Não-jogadores por jogador | Remuneração média por jogador | Lugar |
|:---|---:|---:|---:|---:|:---:|
| 2016/17 | 95 | 56 | 0,7 | 80 446 € | 4.º |
| 2019/20 | 175 | 105 | 0,7 | 99 740 € | 7.º |
| 2020/21 | 210 | 110 | 0,9 | 126 015 € | 7.º |
| 2024/25 | **229** | 82 | **1,8** | **134 494 €** | 6.º |

<sub>Consultas 31 a 33. Nº médio de funcionários e gastos com pessoal das notas "Benefícios dos empregados" dos R&C.</sub>

- O pico de jogadores (110 em 2020/21) coincidiu com o pico de gastos com pessoal e com o pior período financeiro. Desde então, o plantel encolheu para 79–82 jogadores, mas o restante pessoal continuou a crescer: de 100 para 147 pessoas.
- Parte deste crescimento é investimento com retorno esperado (departamentos médico, de nutrição e de *performance*, reorganizados em 2023/24, segundo o R&C). Mas uma estrutura de 147 não-jogadores é um custo fixo que não desce quando a Europa falha.
- A remuneração média por jogador subiu 67% entre 2016/17 e 2024/25, sem melhoria na classificação média.

## 3. Enquadramento de política económica e desportiva

### 3.1 Regras financeiras da UEFA

Desde 2025/26, a UEFA limita os **custos com o plantel a 70% das receitas** (salários, transferências e comissões) para os clubes nas suas provas. A regra substitui o antigo *fair play* financeiro. Os pagamentos em atraso a clubes, trabalhadores e Estado são verificados três vezes por época.

| Época | Rácio aproximado (com vendas) | Sem vendas |
|:---|---:|---:|
| 2021/22 | 113% | 229% |
| 2022/23 | 60% | 166% |
| 2023/24 | 97% | 147% |
| 2024/25 | **43%** | 96% |

<sub>Consulta 24. Aproximação: (salários de atletas e treinadores + amortizações) / (receitas + mais-valias). A UEFA usa definições próprias.</sub>

O Vitória só cumpre o limite **nos anos em que vende muito**. Uma época europeia sem grandes vendas pode deixá-lo acima dos 70%, com sanções progressivas.

A UEFA também condiciona a **propriedade multiclube**. Em 2023, a ligação da V Sports ao Aston Villa obrigou a reduzir a sua participação na SAD de 46% para 29% e a substituir um empréstimo de 11,4 M€ a juro zero por dívida a 11% fixos (BDT & MSD). Uma regra desportiva teve assim um custo financeiro direto: 11% sobre 11,4 M€ são cerca de 1,25 M€ de juros por ano.

### 3.2 Centralização dos direitos televisivos (2028/29)

A partir de 2028/29, os direitos de TV da Liga passam a ser vendidos em conjunto. Pela proposta em discussão, 90% do valor vai para a I Liga e é repartido assim:

| Critério | Peso |
|:---|---:|
| Mérito desportivo (classificação, histórico, ranking UEFA) | 44,2% |
| Parte igual entre os 18 clubes | 33,2% |
| Audiências e assistências nos estádios | 17,6% |
| Condições de transmissão e infraestruturas | 4% |

Com um contrato de 250 M€, a **parte igual** seria de cerca de **4,2 M€ por clube**, 60% do que o Vitória recebe hoje (6,9 M€) (consulta 26). O resto depende de **ficar bem classificado e encher o estádio**.

**Implicação:** com a centralização, a classificação e a assistência passam a ter um valor em euros direto e previsível. Uma época no meio da tabela (como 2025/26) passa a custar dinheiro, e o arranque de 2026/27 em 15.º lugar após 8 jornadas mostra o risco. Por outro lado, o Vitória tem uma das maiores assistências fora dos três grandes (17 388 de média em 2023/24), o que é um trunfo neste modelo.

### 3.3 Custo do dinheiro e fiscalidade

![Dívida financeira e juros](graficos/07_divida_e_juros.png)

| Época | Dívida financeira | Juros suportados | Taxa implícita | Juros / receitas | Liquidez geral |
|:---|---:|---:|---:|---:|---:|
| 2019/20 | 1,2 M€ | 0,1 M€ | 10% | 1% | 0,77 |
| 2020/21 | 20,8 M€ | 0,7 M€ | 6% | 7% | 0,68 |
| 2022/23 | 23,8 M€ | 2,0 M€ | 9% | 15% | 0,46 |
| 2023/24 | 34,0 M€ | 3,7 M€ | 13% | 29% | 0,34 |
| 2024/25 | 34,6 M€ | 5,0 M€ | **15%** | 22% | 0,40 |

<sub>Consultas 27 a 29, com dados dos R&C. A taxa implícita (juros ÷ dívida média do ano) inclui encargos de factoring e de antecipação de receitas.</sub>

- **Juros:** o principal empréstimo (26,3 M€) paga **11% fixos**, cerca de 2,9 M€ por ano, num período em que o BCE desceu as taxas de referência a partir de 2024. Somando factoring e antecipação de receitas de vendas, o custo efetivo chega aos 15%. O R&C atribui a subida "essencialmente" à antecipação de receitas e aos empréstimos da Apollo e da MSD. Os resultados financeiros totais chegaram a (5,6 M€) em 2025/26.
- **Liquidez:** desde 2021/22, o ativo corrente cobre menos de metade do passivo corrente (liquidez geral entre 0,25 e 0,46). A 30/06/2024, a caixa cobria 0,15% das dívidas de curto prazo.
- **Cobertura:** o EBITDA foi negativo em 2020/21, 2021/22 e 2023/24, ou seja, a operação nem sequer pagou os juros. Em 2024/25 cobriu-os 3,7 vezes, mas só graças às vendas de jogadores (consulta 30).
- **Fisco:** quatro passes de jogadores estavam penhorados à Autoridade Tributária, há 855 mil € de reembolso de IVA por receber e processos de 2014–2016 ainda abertos (provisão de 1,5 M€).

### 3.4 Comparação: o SC Braga

Em 2024/25, a SAD do SC Braga também teve prejuízo, (11,0 M€). A diferença está no balanço: **capital próprio positivo de 69 M€** e autonomia financeira de 41%, contra **(36,8 M€)** na SAD do Vitória um ano depois. Um prejuízo pontual é gerível com um balanço sólido. Com capital próprio negativo, cada prejuízo aumenta diretamente a dívida.

## 4. Recomendações

### Curto prazo (0–12 meses): estancar

1. **Orçamentar sem Europa.** As receitas UEFA entram como prémio e destinam-se a reduzir dívida ou reforçar a caixa, nunca a pagar salários fixos.
2. **Refinanciar a dívida de curto prazo.** Trocar os 26,3 M€ a 11% por dívida de médio/longo prazo. Cada ponto percentual a menos poupa cerca de 0,26 M€ por ano. A 6%, a poupança seria de **1,3 M€ por ano**. O Conselho Fiscal já recomendou substituir dívida de curto prazo por médio e longo prazo.
3. **Reserva mínima de caixa.** A SAD chegou a ter 78 mil € em caixa (30/06/2024) e 505 mil € a 30/06/2026. Uma reserva protegida evita vendas forçadas em janeiro.
4. **Resolver as pendências fiscais.** Recuperar o IVA, negociar os processos antigos e libertar os passes penhorados, para recuperar liquidez e liberdade na gestão do plantel.

### Médio prazo (1–3 anos): ajustar o modelo

5. **Teto para os custos do plantel e revisão da estrutura.** Reduzir os gastos com pessoal para um máximo de **100% das receitas recorrentes em dois anos e 85% em quatro**, e cumprir os 70% da UEFA sem depender de vendas. Isto inclui rever os 147 postos não-jogadores, mantendo os que provam retorno (*performance*, *scouting*, formação).
6. **Plantel mais curto e menos dependente de terceiros.** Menos jogadores emprestados e em co-propriedade, mais jogadores 100% do clube. Se as mais-valias tivessem sido 70% das vendas brutas, e não 56%, a SAD teria ganho **mais 7,1 M€** em 2024/25 (menos comissões e menos percentagens cedidas a terceiros).
7. **Vender no momento certo.** Um calendário de vendas planeado (no verão, com 2–3 ativos preparados por época) em vez de vendas de emergência a meio da época.
8. **Estabilidade técnica.** Um modelo de jogo e um perfil de treinador definidos pela estrutura, para que as contratações sirvam o projeto e não cada treinador.
9. **Receitas comerciais e de dia de jogo.** Bilhética, sócios e camarotes renderam cerca de **9 € por espectador e jogo** em 2024/25 (aproximação). Há margem em *hospitality*, eventos no estádio, *merchandising* e patrocínios, sobretudo a pensar no critério de assistências da centralização.

### Longo prazo (3+ anos): reconstruir o balanço

10. **Recapitalizar a SAD.** A entrada prevista de 3,8 M€ no acordo com a V Sports cobre cerca de 10% do capital próprio negativo. É preciso um plano de capital mais amplo: conversão de dívida em capital, novos investidores (dentro das regras multiclube da UEFA) ou outras soluções, como o empréstimo obrigacionista proposto numa das candidaturas de 2026. Cada opção tem custos de controlo e de juros que os sócios devem avaliar.
11. **Formação como fonte de valor.** Jogadores formados no clube têm custo de aquisição zero e ficam 100% do clube na venda, o que melhora a retenção e o rácio da UEFA. Os minutos jogados por atletas que passaram pela formação caíram de cerca de 29 mil (2015/16) para 13 mil (2024/25), segundo a compilação do autor.
12. **Preparar a centralização.** Com mérito e audiências a valer mais de 60% da distribuição, a estabilidade no top 6 e o estádio cheio tornam-se objetivos financeiros, não só desportivos.

## 5. Cenários: quanto é preciso ganhar com jogadores?

Partindo de 2025/26, quanto teria de render a venda de jogadores (resultado com direitos de atletas) para a SAD fechar o ano **sem prejuízo**?

| Cenário | Pressupostos | Resultado com jogadores necessário |
|:---|:---|---:|
| **A. Tudo igual** | Estrutura de 2025/26 | **23,7 M€ / ano** |
| **B. Plano de ajustamento** | Custos operacionais −15% (−5,0 M€), receitas comerciais +10% (+1,5 M€), refinanciamento a 6% (−1,3 M€) | **15,9 M€ / ano** |
| **C. Ajustamento + Europa** | B + fase de liga europeia (+8,3 M€ de receitas UEFA, ~2 M€ de custos extra) | **9,6 M€ / ano** |

<sub>Cálculo ilustrativo do autor sobre os valores do comunicado de contas de 2025/26 (consulta 25).</sub>

Para comparação: o resultado com jogadores foi de **12,6 M€ em 2025/26** e de **22,9 M€ em 2024/25** (reexpresso). As mais-valias médias da SAD entre 2017/18 e 2024/25 foram de **14,4 M€**.

**Leitura:** com a estrutura atual (A), é preciso uma época recorde de vendas **todos os anos**, o que não é realista. O plano de ajustamento (B) aproxima o alvo da média histórica. Só com ajustamento e Europa (C) o clube fica com margem para não vender por necessidade.

---

## Fontes

**Dados financeiros**
- Relatórios e Contas da Vitória SC – Futebol, SAD, 2012/13 a 2024/25 (balanço, juros, dívida e pessoal; ver [verificação das fontes](verificacao-fontes.md))
- [VSC Contas: dashboard de transparência financeira](https://vitoriasempre.net/contas-vsc/) e a sua [análise crítica](https://vitoriasempre.net/contas-vsc/analise-critica.php)
- [Relatórios e Contas do Vitória SC](https://vitoriasc.pt/documentos/)
- Comunicado de contas da SAD a 30/06/2026 (demonstração de resultados e balanço simplificados)
- [dnoticias.pt: SAD do Vitória apresenta prejuízo de 11 milhões em 2025/26](https://www.dnoticias.pt/2026/10/16/509248-sad-do-vitoria-de-guimaraes-apresenta-prejuizo-de-11-milhoes-de-euros-em-202526/)
- [A Bola: SC Braga SAD com resultado líquido negativo de quase 11 M€](https://www.abola.pt/noticias/sc-braga-sad-com-resultado-liquido-negativo-de-quase-euro11-m-2025101315343450369)

**Desempenho desportivo**
- [Wikipédia: Vitória S.C.](https://en.wikipedia.org/wiki/Vit%C3%B3ria_S.C.) e [época 2023/24](https://en.wikipedia.org/wiki/2023%E2%80%9324_Vit%C3%B3ria_S.C._season)
- [Maisfutebol: estatísticas do Vitória SC](https://maisfutebol.iol.pt/vitoria-guimaraes/estatisticas/1585)
- [Soccerway: balanço da Liga 2024/25 do Vitória SC](https://pt.soccerway.com/noticias/futebol-liga-portugal-betclic-balanco-da-liga-vitoria-sc-falha-quarto-acesso-europeu-seguido-em-epoca-instavel/rmG8F1Ls)
- [Wikipédia: final da Taça da Liga 2026](https://en.wikipedia.org/wiki/2026_Ta%C3%A7a_da_Liga_final)

**Enquadramento regulatório e institucional**
- [UEFA: explicação do novo regulamento de sustentabilidade financeira](https://es.uefa.com/news-media/news/0274-14da0ce4535d-fa5b130ae9b6-1000--explainer-uefa-s-new-financial-sustainability-regulations)
- [A Bola: critérios da proposta de centralização dos direitos televisivos](https://www.abola.pt/noticias/os-criterios-da-proposta-de-centralizacao-dos-direitos-televisivos-em-portugal-2026042115383323343)
- [Governo: centralização dos direitos televisivos](https://portugal.gov.pt/gc22/comunicacao/comunicados/centralizacao-dos-direitos-televisivos)
- [Flashscore: acordo com a V Sports prevê entrada de 3,8 M€ na SAD](https://www.flashscore.pt/noticias/acordo-com-v-sports-preve-entrada-de-3-8-me-na-sad-do-vitoria-sc/6Zv0gKsn/)
- [A Bola: orçamento do Clube para 2026/27](https://www.abola.pt/noticias/vitoria-de-guimaraes-apresenta-orcamento-e-rui-rodrigues-deixa-mensagem-2026071614153617207)
- [dnoticias.pt: proposta de empréstimo obrigacionista (candidatura de Viriato Sampaio)](https://www.dnoticias.pt/2026/5/27/493433-viriato-sampaio-propoe-emprestimo-obrigacionista-e-valorizacao-do-estadio-do-vitoria/)
