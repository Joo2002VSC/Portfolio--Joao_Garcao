# Resultados

Gerado por `scripts/correr_cenarios.py`. Plano comum a todos os cenários: 2 000 € iniciais,
200 € por mês (+2% ao ano), 80% ações / 20% cripto,
rebalanceamento anual, de 2026 a 2046. Objetivo: 100 000 € em € de hoje.

| Cenário | Investido | p10 | Mediana | p90 | Mediana (€ de hoje) | Juros simples | P(objetivo) | P(ganho) |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Base | 58 884 € | 67 342 € | **166 862 €** | 453 295 € | 102 952 € | 147 609 € | 51% | 94% |
| Pessimista | 58 012 € | 29 114 € | **79 716 €** | 251 600 € | 40 600 € | 94 308 € | 15% | 65% |
| Otimista | 59 454 € | 120 542 € | **288 173 €** | 783 966 € | 190 179 € | 226 274 € | 82% | 99% |
| Estagflação | 57 428 € | 31 160 € | **76 677 €** | 222 781 € | 24 207 € | 81 268 € | 5% | 65% |

- **p10 / p90**: 10 % dos cenários terminam abaixo / acima destes valores.
- **Juros simples**: o que daria uma calculadora clássica com o retorno médio, sem volatilidade nem choques.
- **P(objetivo)**: probabilidade de chegar ao objetivo em poder de compra de hoje.
- **P(ganho)**: probabilidade de acabar com mais dinheiro (nominal) do que o investido.
