# Metodologia do CJR

Este documento descreve o modelo implementado em `simulador/modelo.py` e `web/js/modelo.js` (os dois motores seguem o mesmo algoritmo) e a forma como cada indicador é calculado.

> Os resultados são simulações ilustrativas, não previsões nem aconselhamento financeiro. **Todos os parâmetros são pressupostos definidos pelo utilizador.** Os valores dos cenários Base, Pessimista, Otimista e Estagflação são ilustrativos; nenhum foi estimado a partir de dados históricos.

## 1. Simulação de Monte Carlo

O simulador gera N trajetórias independentes (2 000, 10 000 ou 50 000), cada uma com `12 × anos` passos mensais. Cada trajetória é um cenário. Os resultados são estatísticas dessa amostra: percentis, médias e proporções. A semente aleatória é fixa, por isso a mesma configuração dá sempre os mesmos números.

## 2. Ordem dos cálculos

Para cada ano *y* e cada cenário:

1. **Inflação do ano:** π = π̄ + σ_π·Z, mais o choque com probabilidade p_choque; π ≥ −5 %. Fator mensal (1 + π)^(1/12).
2. **Pausa:** com probabilidade p_pausa, acrescentam-se 6 meses sem aportes (pausas seguidas acumulam).
3. **Aporte-base:** A_y = A·(1 + g)^y; se indexado, × índice de preços no início do ano.

Para cada mês *m*:

4. **Aporte no início do mês:** semanal = A_y·52/12; mensal = A_y; anual = A_y só em janeiro. Divide-se pela composição alvo.
5. **Rentabilidade:** log-retorno mensal r = μ + s·z, com μ = ln(1 + R)/12 e s = σ/√12.
6. **Crise** (probabilidade mensal 1 − (1 − p)^(1/12)): ações × (1 − q_a), cripto × (1 − q_c).
7. **Regulação** (idem): cripto × (1 − q_r).
8. **Custos:** carteira × (1 − c)^(1/12).
9. **Índice de preços:** × fator mensal de inflação.

No fim do ano: **rebalanceamento** opcional para a composição alvo.

## 3. Rentabilidades

### Convenção

O parâmetro R é a **rentabilidade anual mediana**, que é também a geométrica: o crescimento composto típico antes de choques e custos (a mediana de e^(12μ + √12·s·z) é e^(12μ) = 1 + R). Daqui decorrem três números diferentes, que a página mostra lado a lado:

| Medida | Fórmula (log-normal) | Ações (Base) | Cripto (Base) |
|---|---|--:|--:|
| Mediana / geométrica (o parâmetro) | R | 7,0 % | 15,0 % |
| Média aritmética anual, antes de choques | (1 + R)·e^(σ²/2) − 1 | 8,4 % | 42,1 % |
| Efetiva, após crises, regulação e custos | exp(ln(1+R) + ln(1−c) + Σ 12·p_m·ln(1−q)) − 1 | 4,9 % | 8,2 % |

A "efetiva" é exp(E[log crescimento anual]) − 1, a taxa de crescimento composto a longo prazo. O teste S5 confirma-a por simulação.

**Consequência importante.** Com a mediana fixa, mais volatilidade aumenta a média aritmética. Numa carteira rebalanceada, a taxa de crescimento da carteira é aproximadamente Σ wᵢ(μᵢ + σᵢ²/2) − σ_p²/2, cuja derivada em ordem a σ_c é w_c·w_a·(σ_c − ρσ_a) > 0. Por isso, no cenário Base, subir a volatilidade da cripto **sobe** a mediana da carteira, e a mediana simulada fica acima da calculadora clássica. É matematicamente correto dada a convenção, mas depende muito do pressuposto de que a cripto tem uma média aritmética de 42 % ao ano. Uma convenção alternativa (o parâmetro ser a média aritmética) daria resultados muito mais baixos para ativos voláteis; mudar de convenção alteraria todos os resultados e não foi feito sem decisão explícita.

### Distribuições

- **Log-normal (por defeito):** z ~ N(0, 1).
- **Student-t multivariada:** z = n·√((ν − 2)/W), com n normal e W ~ χ²_ν **comum aos dois ativos**. Tem variância 1 (comparável com a normal), a mesma mediana e caudas mais pesadas; o fator comum cria dependência nas caudas. Com a t, a média aritmética teórica de e^r não está definida, por isso a página mostra "n.d.".
- **Bootstrap histórico:** não implementado. Exigiria séries de rentabilidades de fonte verificável (por exemplo, um índice mundial de ações e um índice de criptoativos), com a respetiva licença e documentação.

`convergencia.md` compara as duas distribuições com 50 000 cenários: as diferenças são pequenas porque a soma de 12 choques mensais se aproxima da normal e porque as crises (saltos) já dominam as caudas. A log-normal mantém-se por defeito; a t fica disponível como teste de sensibilidade.

### Correlação

Com dois ativos, z₂ = ρ·z₁ + √(1 − ρ²)·ε. A matriz [[1, ρ], [ρ, 1]] é simétrica, tem diagonal 1 e é semidefinida positiva se e só se |ρ| ≤ 1, condição imposta pela validação. As volatilidades aplicam-se depois, por isso qualquer combinação de σ e ρ válida dá uma covariância válida.

As crises atingem as duas classes no mesmo mês, o que eleva a correlação efetiva (0,35 → ~0,41 no cenário Base; ver `convergencia.md`). Funciona como uma correlação de crise mais alta, sem um segundo parâmetro.

## 4. Eventos económicos

| Evento | Probabilidade | Efeito | Duração |
|---|---|---|---|
| Crise de mercado | anual, convertida em mensal | queda instantânea nas duas classes | permanente: não há recuperação automática |
| Regulação adversa | anual, convertida em mensal | queda só na cripto | permanente |
| Choque de inflação | anual | + pontos percentuais à inflação desse ano | 1 ano (o nível de preços fica mais alto para sempre) |
| Pausa nos aportes | anual | sem aportes | 6 meses (acumulam) |

Os eventos são independentes entre si e entre meses, e podem coincidir. A inflação não afeta as rentabilidades diretamente.

## 5. Valores nominais e reais

- **Nominal:** euros do próprio ano.
- **Real (€ de hoje):** nominal ÷ índice de preços **do cenário**.
- **Capital investido real:** Σ aporteₜ ÷ índiceₜ, com o índice do mês em que o aporte entrou.

Assim, o ganho real (final real − investido real) e a probabilidade de perda real comparam valores na mesma base. No gráfico em euros nominais, o objetivo é convertido com a inflação média, (1 + π̄)^y.

## 6. Indicadores

Todos os ganhos e perdas são calculados **por cenário** e só depois resumidos.

| Indicador | Definição |
|---|---|
| Percentil Pq | interpolação linear entre estatísticas de ordem (igual a `numpy.percentile`) |
| Ganho nominal / real | mediana de (final − investido), na base respetiva |
| Rentabilidade acumulada | mediana de (final ÷ investido − 1), nominal, não anualizada |
| TIR (rentabilidade anualizada) | taxa r que resolve Σ aₜ(1 + r)^(T − t) = valor final; aₜ = aporte médio no mês t; resolvida por bisseção e anualizada. Calculada para P10, P50 e P90 (nominal e real). É ponderada pelo dinheiro. Com pausas, o calendário médio é uma aproximação. |
| Probabilidade de atingir o objetivo | proporção de cenários com final real ≥ objetivo |
| Probabilidade de perda | proporção de cenários com final < investido (nominal ou real) |
| Queda máxima (*drawdown*) | maior queda, do pico ao mínimo, do valor da unidade de participação (rentabilidade ponderada no tempo, sem efeito dos aportes); mediana e P90 entre cenários |
| VaR 95 % anual | percentil 5 das rentabilidades anuais da carteira, juntando todos os anos de todos os cenários |
| CVaR 95 % anual | média das rentabilidades anuais ≤ VaR |
| Cauda no horizonte | P5 do valor final real e média dos 5 % piores cenários |
| Calculadora clássica | taxa constante (1 + Σwᵢ·Rᵢ)(1 − c) − 1, mesmo calendário de aportes, sem volatilidade, eventos nem pausas |

## 7. Precisão da simulação

- **Mediana:** intervalo de confiança de 95 % sem pressupostos de distribuição, pelas estatísticas de ordem de posição n/2 ± 1,96·√n/2.
- **Probabilidades:** erro-padrão √(p(1 − p)/N).

Com 2 000 cenários, a mediana real do cenário Base varia cerca de ±1,8 % entre sementes; com 50 000, cerca de ±0,2 %. **Mais cenários reduzem o erro de amostragem, não o erro dos pressupostos.** Uma rentabilidade errada em 1 p.p. desloca a mediana muito mais do que o erro de Monte Carlo com 2 000 cenários.

## 8. Comparações

A comparação de cenários e a análise de sensibilidade usam **números aleatórios comuns**: a mesma semente e o mesmo número de sorteios por cenário. As diferenças entre linhas vêm, por isso, dos pressupostos e não do acaso. A sensibilidade varia um parâmetro de cada vez, com os restantes fixos, e usa 2 000 cenários.

## 9. Limitações conhecidas

- Retornos independentes de mês para mês: sem ciclos económicos, regimes de mercado, tendência para a média nem volatilidade variável.
- Inflação independente das rentabilidades; o cenário Estagflação aproxima essa ligação só pelos parâmetros.
- Crises sem recuperação própria e com intensidade fixa.
- Sem impostos (mais-valias de ações a 28 % ou englobamento; criptoativos detidos há mais de 365 dias isentos) e sem custos de transação no rebalanceamento.
- A TIR por percentil usa o calendário médio de aportes.
- Sem reamostragem histórica.
