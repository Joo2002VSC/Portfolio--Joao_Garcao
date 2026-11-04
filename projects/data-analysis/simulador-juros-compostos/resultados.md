# Resultados

Gerado por `scripts/correr_cenarios.py`. Plano comum a todos os cenários: 2 000 € iniciais,
200 € por mês (+2% ao ano), 80% ações / 20% cripto,
rebalanceamento anual, de 2026 a 2046. Objetivo: 100 000 € em € de hoje.

| Cenário | Investido | Mediana (nominal) | Mediana (€ de hoje) | P10–P90 (€ de hoje) | TIR real mediana | P(objetivo) | P(perda real) | Queda máx. mediana |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Base | 58 884 € | 165 988 € | **102 204 €** | 41 491 € – 277 707 € | 6,9 % | 51,0 % | 13,7 % | 49,9 % |
| Pessimista | 58 012 € | 78 041 € | **39 592 €** | 14 222 € – 124 048 € | -0,5 % | 14,4 % | 52,2 % | 73,6 % |
| Otimista | 59 454 € | 288 070 € | **189 657 €** | 79 026 € – 513 035 € | 11,7 % | 81,6 % | 1,7 % | 38,0 % |
| Estagflação | 57 428 € | 75 856 € | **23 839 €** | 9 070 € – 68 966 € | -3,0 % | 4,5 % | 67,1 % | 70,5 % |

Todos os cenários usam o mesmo plano e a mesma semente aleatória (números aleatórios comuns),
por isso as diferenças entre linhas vêm dos pressupostos de mercado e não do acaso da simulação.

- **Mediana**: metade dos cenários termina acima deste valor. *Nominal* = euros do ano final; *€ de hoje* = poder de compra atual.
- **P10–P90**: 80 % dos cenários terminam dentro deste intervalo.
- **TIR real mediana**: rentabilidade anual ponderada pelo dinheiro, já descontada a inflação.
- **P(objetivo)**: probabilidade de chegar ao objetivo em poder de compra de hoje.
- **P(perda real)**: probabilidade de o valor final valer menos do que o dinheiro investido, ambos em € de hoje.
- **Queda máx. mediana**: maior queda, do pico ao mínimo, da unidade de participação da carteira (*drawdown*).
