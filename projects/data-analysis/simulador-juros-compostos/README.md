<p align="center"><img src="web/img/cjr-logo.png" alt="CJR — Calculador de Juros Compostos" width="420"></p>

# 📈 Simulador de Juros Compostos (CJR)

> 🇬🇧 *A Monte Carlo simulator for long-term investing in a stock + crypto portfolio: weekly, monthly or yearly contributions, random inflation, management costs and exogenous events (market crashes, crypto regulation, inflation spikes, contribution pauses). Two engines — Python/NumPy and JavaScript — that implement the same model and are cross-checked by automated tests, plus an interactive web version.*

**[▶ Experimentar a versão interativa](https://joo2002vsc.github.io/Portfolio--Joao_Garcao/projects/data-analysis/simulador-juros-compostos/web/)**

Uma calculadora de juros compostos clássica dá **um só número**: "investindo 200 € por mês a 7 %, terá X em 2046". Mas os mercados não sobem 7 % todos os anos, a inflação muda, há crises e há meses em que não se consegue investir.

O CJR responde à mesma pergunta com **milhares de cenários simulados mês a mês** e mostra o intervalo provável em vez de um valor único:

1. **Quanto património terei num dado ano**, em euros nominais e em poder de compra de hoje?
2. **Qual a probabilidade de atingir o meu objetivo**, e de acabar com menos do que investi?
3. **Que riscos corro pelo caminho** (quedas, maus anos, cauda dos resultados)?
4. **Que pressupostos mais pesam no resultado?**

> ⚠️ Simulação ilustrativa, não é aconselhamento financeiro. Todos os parâmetros são pressupostos definidos pelo utilizador; nenhum é estimado a partir de dados históricos.

---

## 📊 Resultados (cenário Base)

Plano de exemplo: 2 000 € iniciais, 200 €/mês (+2 % ao ano), 80 % ações / 20 % criptoativos, rebalanceamento anual, 2026–2046, objetivo de 100 000 € de hoje. Tabela dos quatro cenários em [`resultados.md`](resultados.md).

| Indicador | Valor |
|---|--:|
| Capital investido (média) | 58 884 € (46 516 € de hoje) |
| Património mediano em 2046 | 165 988 € nominais · **102 204 € de hoje** |
| Intervalo P10–P90 (€ de hoje) | 41 491 € – 277 707 € |
| Rentabilidade anualizada (TIR mediana) | 9,6 % nominal · 6,9 % real |
| Probabilidade de atingir o objetivo | 51 % |
| Probabilidade de perda real | 13,7 % |
| Queda máxima pelo caminho (mediana / pior 10 %) | 50 % / 69 % |
| Perda num mau ano (VaR 95 % / CVaR) | −26 % / −33 % |

### O leque de resultados possíveis
![Leque do cenário Base](graficos/1_leque_cenario_base.png)

A linha pontilhada é a calculadora clássica (taxa média ponderada, sem volatilidade). Metade dos cenários termina acima de 166 k€ nominais, mas 10 % ficam abaixo de 67 k€ e outros 10 % acima de 451 k€.

### Quatro cenários, em € de hoje
![Cenários comparados](graficos/2_cenarios_comparados.png)

### Probabilidade de atingir o objetivo
![Distribuição final](graficos/3_distribuicao_final.png)

### Quanto pôr em criptoativos?
![Efeito da alocação em cripto](graficos/4_efeito_alocacao_cripto.png)

Com estes pressupostos, a mediana sobe até cerca de 70 % em cripto e depois desce, enquanto o cenário pessimista (P10) melhora até ~30 % e a partir daí só piora. Com 100 % em cripto, 1 em cada 10 cenários acaba com menos de metade do P10 de uma carteira só de ações.

---

## ⚙️ O modelo

Cada cenário avança **mês a mês**. A descrição completa, com fórmulas, está em [`METODOLOGIA.md`](METODOLOGIA.md).

| Passo | O que acontece |
|---|---|
| Aportes | Entram no início de cada mês. Semanal = 52/12 por mês; anual = só em janeiro. Podem crescer x % ao ano (em janeiro) ou acompanhar a inflação. |
| Mercados | Log-retornos **normais** (preços log-normais) ou **Student-t** multivariada, correlacionados entre ações e cripto. O parâmetro é a rentabilidade **mediana geométrica**. |
| Eventos | Probabilidade anual convertida em mensal com 1 − (1 − p)^(1/12): **crise** (queda nas duas classes), **regulação** (só cripto), **choque de inflação** e **pausa de 6 meses** nos aportes. |
| Custos | Fator mensal (1 − custo anual)^(1/12): ao fim de um ano, cobra exatamente a taxa indicada. |
| Inflação | Sorteada ano a ano; cada cenário tem o seu índice de preços. |
| Fim do ano | Rebalanceamento opcional. |

Os indicadores comparam sempre valores **na mesma base**: o capital investido real desconta cada aporte pelo índice de preços do mês em que entrou; ganhos e perdas são calculados cenário a cenário.

### Dois motores, um modelo

| | Python (`simulador/`) | JavaScript (`web/js/modelo.js`) |
|---|---|---|
| Uso | Análise, gráficos, estudos de robustez | Página interativa (num Web Worker, sem bloquear a interface) |
| Desempenho | 2 000 cenários × 20 anos ≈ 0,1 s (vetorizado) | 50 000 cenários × 20 anos ≈ 2,3 s |

Os geradores aleatórios são diferentes, por isso os números não coincidem ao cêntimo. Um teste corre os dois motores com 50 000 cenários e exige que as diferenças caibam no erro de Monte Carlo.

---

## ✅ Validação

[`scripts/testes.py`](scripts/testes.py) (26 testes) e [`scripts/testes_web.js`](scripts/testes_web.js) (14 testes) verificam propriedades que o modelo tem de cumprir:

| Teste | Propriedade |
|---|---|
| **A** Capitalização sem volatilidade | Resultado = fórmula clássica `P·qⁿ + a·q·(qⁿ − 1)/(q − 1)`; com custos e aportes crescentes, simulação = calculadora clássica |
| **B** Rentabilidade zero | Valor final = capital inicial + aportes |
| **C** Sem investimento | Todos os cenários terminam em 0; TIR e rentabilidade não definidas |
| **D** Reprodutibilidade | Mesma semente → resultados idênticos (log-normal e Student-t) |
| **E** Inflação | Real = nominal ÷ índice; capital investido real desconta cada aporte no seu mês |
| **F** Aportes crescentes | O aumento aplica-se em janeiro; incrementos anuais crescem à taxa indicada |
| **G** Custos | 1 % ao ano cobra exatamente 1 % por ano, sem duplicação, e cada aporte paga desde que entra |
| Propriedades | Frequências equivalentes, TIR = taxa líquida, equação de Fisher, drawdown, monotonia, perdas por cenário |
| Estatísticos | Frequência anual das crises, mediana log-normal e t, variância e correlação dos choques, volatilidade anual (tolerância de 4 erros-padrão) |
| Cruzado | Python vs JavaScript com 50 000 cenários: Base, Student-t e Pessimista |
| Validação | Entradas fora dos limites são rejeitadas nos dois motores |

[`convergencia.md`](convergencia.md) mostra a estabilidade com 2 000, 10 000 e 50 000 cenários, a comparação log-normal vs Student-t e a correlação efetiva com crises.

Os testes correm no GitHub Actions sempre que a pasta muda.

---

## 🗂️ Estrutura

```
simulador-juros-compostos/
├── simulador/
│   ├── modelo.py           ← parâmetros, validação, simulação, calculadora clássica, rentabilidade implícita
│   ├── risco.py            ← TIR, VaR/CVaR, drawdown, intervalos de confiança, resumo
│   └── cenarios.py         ← Base, Pessimista, Otimista, Estagflação
├── scripts/
│   ├── testes.py           ← testes do motor Python + comparação com o JavaScript
│   ├── testes_web.js       ← testes do motor JavaScript (Node)
│   ├── correr_cenarios.py  ← gera graficos/ e resultados.md
│   └── convergencia.py     ← gera convergencia.md
├── web/
│   ├── index.html          ← versão interativa
│   ├── css/estilo.css
│   ├── js/modelo.js        ← motor JavaScript (página, Web Worker e Node)
│   ├── js/graficos.js      ← gráficos em canvas, sem bibliotecas
│   ├── js/app.js           ← interface
│   └── img/                ← logo CJR e favicon
├── METODOLOGIA.md · resultados.md · convergencia.md
└── requirements.txt
```

## ▶️ Como correr

```bash
pip install -r requirements.txt
python scripts/testes.py          # inclui a comparação com o motor JavaScript, se houver Node
node scripts/testes_web.js
python scripts/correr_cenarios.py
python scripts/convergencia.py    # ~15 s
```

```python
from simulador import CENARIOS, simular, resumir

plano = CENARIOS["Base"].com(aporte=50, frequencia="semanal", peso_cripto=0.1, ano_alvo=2056)
print(resumir(simular(plano)))
```

A versão web não precisa de instalação: basta abrir `web/index.html` no navegador.

---

## ⚠️ Limitações

- Os parâmetros são **pressupostos**, não estimativas históricas. Com a convenção da rentabilidade mediana, os 15 % da cripto com 65 % de volatilidade implicam uma média aritmética de 42 % ao ano; a página mostra este valor para que a escolha seja consciente.
- Retornos independentes de mês para mês: sem ciclos, regimes de mercado ou tendência para a média; inflação independente das rentabilidades.
- Não há reamostragem histórica (*bootstrap*): exigiria séries de rentabilidades com fonte verificável.
- **Impostos não incluídos.** Em Portugal, as mais-valias de ações pagam 28 % (ou englobamento) e as de criptoativos detidos há mais de 365 dias estão isentas.

---

**Ferramentas:** Python · NumPy · matplotlib · JavaScript (Web Workers, Canvas) · HTML/CSS · Node · GitHub Actions

© 2026 João Garção
