# Verificação das fontes

Todos os números do balanço, dos juros e do pessoal da SAD usados neste projeto foram conferidos, um a um, com os **Relatórios e Contas (R&C) da Vitória SC – Futebol, SAD de 2012/13 a 2024/25**. Seis desses relatórios (2012/13 a 2016/17 e 2022/23) são digitalizados e foram lidos com OCR e confirmados visualmente na página original.

Foram comparadas três fontes secundárias com os R&C:

| Fonte | Divergências | Épocas afetadas | Diagnóstico |
|:---|:---:|:---|:---|
| CSV `VitóriaSCContasSAD.csv` (e o script e os rácios que dele dependem) | 24 | 2020/21 a 2023/24 | **2022/23 e 2023/24 errados**; 2020/21 e 2021/22 com totais certos mas divisão corrente/não corrente errada |
| Site VSC Contas (fonte original deste projeto) | 13 | 2014/15 a 2018/19 e 2021/22 a 2023/24 | **Balanços de 2014/15 a 2016/17 errados**; juros líquidos em vez de brutos |
| Excel `HistóricoContasSAD.xlsx` | 3 | 2016/17, 2020/21, 2023/24 | Duas gralhas e uma reclassificação. **No resto, bate certo** |

O resultado também está na base de dados (tabela `divergencia`, consulta 35).

---

## 1. CSV `VitóriaSCContasSAD.csv`

- **2019/20** bate certo com os R&C.
- **2020/21 e 2021/22:** o ativo, o passivo e o capital próprio estão certos, mas a divisão entre corrente e não corrente não corresponde a nenhum relatório publicado (nem ao da própria época, nem aos comparativos do ano seguinte).
- **2022/23 e 2023/24:** os valores não correspondem a nenhum R&C da SAD nem às contas consolidadas. O CSV dá um capital próprio de **+10,1 M€ em 2022/23**, quando o R&C mostra **(16,5 M€)**, e um ativo de 73,3 M€ em vez de 36,5 M€.

**Consequências:** o gráfico `evolucao_indicadores_balanco_barras_custom_cores.png` e o ficheiro `vitoria_sc_balanco_ratios.csv` herdam estes erros. Por exemplo, o rácio de endividamento de 2022/23 aparece como 0,86, quando o valor correto é **1,45**. A liquidez geral de 2022/23 aparece como 1,59, quando o valor correto é **0,46**.

| Época | Indicador | No CSV | Nos R&C | Diferença |
|:---|:---|---:|---:|---:|
| 2020/21 | Ativo Corrente | 13 567 877,65 | 18 344 725,38 | (4 776 847,73) |
| 2020/21 | Ativo Não Corrente | 44 278 774,19 | 39 501 926,46 | 4 776 847,73 |
| 2020/21 | Passivo Corrente | 26 837 915,03 | 27 162 582,63 | (324 667,60) |
| 2020/21 | Passivo Não Corrente | 34 852 845,13 | 34 528 177,53 | 324 667,60 |
| 2021/22 | Ativo Corrente | 8 599 309,69 | 9 004 953,89 | (405 644,20) |
| 2021/22 | Ativo Não Corrente | 25 943 633,01 | 25 537 988,81 | 405 644,20 |
| 2021/22 | Passivo Corrente | 31 425 405,17 | 36 212 322,40 | (4 786 917,23) |
| 2021/22 | Passivo Não Corrente | 20 691 339,66 | 15 904 422,43 | 4 786 917,23 |
| 2022/23 | Ativo Total | 73 303 045,91 | 36 487 874,98 | 36 815 170,93 |
| 2022/23 | Ativo Corrente | 53 076 657,32 | 13 611 379,00 | 39 465 278,32 |
| 2022/23 | Ativo Não Corrente | 20 226 388,59 | 22 876 495,98 | (2 650 107,39) |
| 2022/23 | Passivo Total | 63 153 945,71 | 52 957 514,69 | 10 196 431,02 |
| 2022/23 | Passivo Corrente | 33 407 962,55 | 29 742 528,49 | 3 665 434,06 |
| 2022/23 | Passivo Não Corrente | 29 745 983,16 | 23 214 986,19 | 6 530 996,97 |
| 2022/23 | Capital Próprio | 10 149 100,20 | (16 469 639,70) | 26 618 739,90 |
| 2022/23 | Caixa | 13 626 852,70 | 138 409,99 | 13 488 442,71 |
| 2023/24 | Ativo Total | 56 095 420,01 | 35 823 548,40 | 20 271 871,61 |
| 2023/24 | Ativo Corrente | 29 407 382,60 | 17 641 863,85 | 11 765 518,75 |
| 2023/24 | Ativo Não Corrente | 26 688 037,41 | 18 181 684,55 | 8 506 352,86 |
| 2023/24 | Passivo Total | 77 828 591,15 | 67 016 655,29 | 10 811 935,86 |
| 2023/24 | Passivo Corrente | 39 567 893,95 | 52 493 021,89 | (12 925 127,94) |
| 2023/24 | Passivo Não Corrente | 38 260 697,20 | 14 523 633,40 | 23 737 063,80 |
| 2023/24 | Capital Próprio | (21 733 171,14) | (31 193 106,89) | 9 459 935,75 |
| 2023/24 | Caixa | 1 523 585,02 | 78 684,27 | 1 444 900,75 |

**No script `ScriptAnalisarContasSAD.py`:** o código está correto, mas:
- O "rácio de estrutura de capital" (passivo ÷ capital próprio) não tem leitura quando o capital próprio é negativo, como em 2020/21, 2021/22 e 2023/24. Os valores negativos (−16,0; −3,0; −3,6) não significam nada. É mais útil a autonomia financeira (capital próprio ÷ ativo).
- O código lê `VitóriaSCContasSAD.csv` diretamente. Corrigindo o CSV, os gráficos e os rácios ficam certos.

## 2. Excel `HistóricoContasSAD.xlsx`

O balanço de 2012/13 a 2022/23, os gastos com pessoal e o número de funcionários batem certo com os R&C em todas as épocas, incluindo as digitalizadas. Há três pontos a corrigir ou anotar:

| Folha · célula | Época | No Excel | Nos R&C | O que é |
|:---|:---|---:|---:|:---|
| Indicadores Gerais · B13 | 2023/24 | 38 823 548,40 | 35 823 548,40 | Gralha: o 5 virou 8. As parcelas corrente e não corrente estão certas |
| Gastos com Pessoal · D6 | 2016/17 | 313 868,33 | 312 868,33 | Gralha de 1 000 € |
| Gastos com Pessoal · E10 | 2020/21 | 1 242 836,91 | 1 636 456,86 | Não é erro: é o valor reclassificado no R&C 2021/22, sem o pessoal de apoio |

Outros problemas na folha:
- **Passivo · B4:** `=113605.7` em vez de `11360570.07` (2014/15).
- **Indicadores Gerais · I13** (caixa de 2023/24) e várias células de "Gastos com Pessoal" e "Ativo" estão guardadas como **texto** (por exemplo `'78 684,27'` e `'184313, 51'`). O Excel não as soma nem as inclui em gráficos.
- **Fórmulas de variação (Indicadores Gerais, D125:D135 e D150:D160):** dividem pelo valor do ano **novo**, `(C125-C124)/C125`, em vez do ano anterior. Por isso, a "variação média do ativo" dá 3,46% em vez de **19%** (valor certo, que está na folha "Ativo"), e a do passivo dá 9,2%. O mesmo acontece na folha "Espectadores".
- **Vendas de Jogadores:** faltam as épocas 2013/14, 2014/15, 2015/16 e 2020/21, que aparecem no gráfico da apresentação.

## 3. Apresentação `AnáliseVSCSAD.pptx`

| Diapositivo | Afirmação | Correção |
|:---:|:---|:---|
| 9 | Ativo de 2023/24 = 38,8 M€; "quase quatro vezes" o de 2012/13 | 35,8 M€ (gralha do Excel), ou seja, **3,1 vezes** |
| 9 | Crescimento médio do ativo de 3,46% por exercício | **19%** com a fórmula correta |
| 13 | "Média de 5,8 M€ de lucro por exercício" | 102,9 M€ ÷ 12 épocas = **8,6 M€** |
| 20 | 2023/24 é o "segundo maior" rácio de endividamento (1,726) | Com o ativo correto, o rácio é **1,87, o maior da história da SAD** (acima de 1,80 em 2013/14) |
| 23–24 | Duas participações na Liga Europa (2013/14 e 2017/18) | Foram **três**: também 2019/20, fase de grupos (prémios de 5,4 M€). Em 2015/16 houve ainda uma pré-eliminatória |
| 5 | A UEFA obrigou a V Sports a descer para menos de 30% em 2024 | A redução de 46% para 29% foi em **junho de 2023** |
| 27 | Encaixe de 9,9 M€ com a Liga Conferência | O R&C 2024/25 indica 9,7 M€ em receitas de competições (UEFA e nacionais) |
| 25 | 2022/23: 20 823 min · 2023/24: 9 816 min e 10 jogadores | A folha "Formação" dá 20 896 min, e 12 041 min com 11 jogadores |

A conclusão do diapositivo 20 (capital próprio positivo só de 2016/17 a 2019/20) **está certa** e foi confirmada nos R&C.

## 4. Site VSC Contas

O site, que serviu de base ao projeto, tem os **balanços de 2014/15 a 2016/17 errados**. O ativo é igual ao passivo em 2014/15 (capital próprio = 0) e há um capital próprio de exatamente 5 000 000 € em 2016/17. Os R&C mostram capital próprio de (3,85 M€), (0,52 M€) e +2,26 M€. Em 2017/18 e 2018/19 há diferenças menores, de origem desconhecida.

Os juros de 2021/22 a 2023/24 aparecem **líquidos** dos juros obtidos, mas os de 2024/25 aparecem brutos.

O site regista também um aumento de capital de 450 000 € em 2016/17. Os R&C não o confirmam: o capital próprio de 2016/17 é exatamente o de 2015/16 mais o resultado do ano.

**O que foi corrigido no projeto:** a tabela `balanco` usa agora os valores dos R&C para a SAD, de 2012/13 a 2024/25. A nova tabela `balanco_sad_rc` guarda o balanço detalhado, a dívida financeira e os juros brutos. Os valores antigos do site ficam registados na tabela `divergencia`.

## Método

1. Extração do texto dos R&C em PDF (`pdftotext`) e OCR (Tesseract) dos relatórios digitalizados.
2. Leitura do balanço, da demonstração de resultados e da nota "Benefícios dos empregados" de cada época, usando sempre o **relatório da própria época** e, quando este não é legível, os comparativos do ano seguinte.
3. Testes de coerência em todas as épocas: ativo = corrente + não corrente, passivo = corrente + não corrente, capital próprio = ativo − passivo, soma das rubricas de pessoal = total, soma das categorias = nº de funcionários. As restrições `CHECK` da tabela `balanco_sad_rc` repetem estes testes sempre que a base é construída.
4. Comparação automática de cada fonte com os R&C. É considerada divergência qualquer diferença igual ou superior a 1 €.
