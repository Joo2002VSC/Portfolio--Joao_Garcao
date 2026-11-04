# Robustez do modelo

Gerado por `scripts/convergencia.py` com o cenário Base (2 000 € iniciais, 200 €/mês, 80/20, 2026–2046).

## 1. Convergência de Monte Carlo

Cada linha repete a simulação com sementes diferentes. O "desvio entre sementes" é o erro de Monte Carlo
observado; o "IC 95 % numa só corrida" é o intervalo que a página mostra, calculado pelas estatísticas de ordem.

| Cenários | Sementes | Mediana real (média) | Desvio entre sementes | IC 95% da mediana numa só corrida | P10 real: desvio | P(objetivo): desvio |
|--:|--:|--:|--:|--:|--:|--:|
| 2 000 | 20 | 100 578 € | ±1 791 € (1,78 %) | ±4 123 € | ±979 € | ±0,88 p.p. |
| 10 000 | 12 | 100 614 € | ±1 020 € (1,01 %) | ±1 883 € | ±370 € | ±0,53 p.p. |
| 50 000 | 6 | 100 180 € | ±233 € (0,23 %) | ±826 € | ±108 € | ±0,13 p.p. |

O erro diminui com √N: multiplicar os cenários por 25 (de 2 000 para 50 000) divide o erro por ~5.
**Mais cenários reduzem o erro de amostragem, não o erro dos pressupostos.** Uma rentabilidade
esperada errada em 1 p.p. desloca a mediana muito mais do que o erro de Monte Carlo com 2 000 cenários.

## 2. Log-normal vs Student-t (50 000 cenários)

Na Student-t os choques mensais têm a mesma variância, mas caudas mais pesadas, e um fator comum às
duas classes de ativos (t multivariada), o que torna as quedas extremas mais prováveis de acontecer juntas.

| Modelo | Mediana real | P10 real | P5 real | Média dos 5 % piores | P(objetivo) | Queda máxima mediana | Perda anual a 95 % (VaR) | Média das perdas além do VaR (CVaR) |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Log-normal | 100 379 € | 41 127 € | 32 907 € | 26 412 € | 50,2 % | 50,2 % | 25,8 % | 33,4 % |
| Student-t, ν = 8 | 100 260 € | 41 176 € | 32 885 € | 26 259 € | 50,1 % | 50,2 % | 25,8 % | 33,6 % |
| Student-t, ν = 5 | 99 797 € | 41 029 € | 32 694 € | 26 293 € | 49,9 % | 49,8 % | 25,9 % | 33,7 % |
| Student-t, ν = 3 | 97 030 € | 40 916 € | 32 676 € | 26 011 € | 48,4 % | 47,7 % | 25,2 % | 33,9 % |

Leitura: com estes parâmetros, trocar a log-normal pela Student-t muda pouco os resultados. Há duas razões.
Os choques são mensais e a soma de 12 meses aproxima-se da normal (teorema do limite central). E as crises
de mercado, que são saltos discretos, já dominam as caudas do modelo. Só com ν = 3 a diferença se nota:
a mediana desce cerca de 3 % e a média das piores perdas anuais (CVaR) agrava-se ligeiramente. A queda
máxima mediana até diminui, porque a t concentra mais meses perto do centro e deixa as perdas para
poucos meses extremos. Por isso o modelo por defeito continua a ser a log-normal, e a t fica disponível
como teste de sensibilidade.

## 3. Correlação efetiva com crises

| Situação | Correlação anual dos log-retornos (ações × cripto) |
|---|--:|
| Sem crises (só a correlação do modelo, ρ = 0,35) | 0,349 |
| Com crises e regulação (cenário Base) | 0,410 |

As crises atingem as duas classes de ativos no mesmo mês, por isso a correlação observada sobe
acima do parâmetro ρ. Na prática, isto já representa uma "correlação de crise" mais alta do que a
de períodos normais, sem ser preciso um segundo parâmetro.
