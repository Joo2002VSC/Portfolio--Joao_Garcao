# Os Maias

**Eça de Queirós** · 1888

[← Todos os livros](../../README.md) · **[Painel interativo](painel.html)** (rede de personagens em 3D) · [Excel](eca-de-queiros-os-maias.xlsx) · [JSON](indicadores.json)

## 1. Identificação e metadados

| Campo | Valor |
| --- | --- |
| Título | Os Maias |
| Autor | Eça de Queirós |
| Ano | 1888 |
| Língua declarada | Portuguese |
| Fonte | Project Gutenberg |
| Ficheiro | `eca-de-queiros-os-maias.txt` (TXT) |
| Língua detetada | português · modelo `pt_core_news_md` 3.8.0 |

## 2. Características do texto

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Palavras** | 203 558 | palavras | Base de normalização de quase todos os indicadores. |
| **Frases** | 16 759 | frases | Base para as médias e distribuições por frase. |
| **Parágrafos** | 5 759 | parágrafos | Base para a proporção de diálogo e a extensão dos parágrafos. |
| **Tempo de leitura estimado** | 14,3 | horas | Ordem de grandeza, não uma previsão individual. |

Sem avisos de qualidade: texto não vazio, sem sinais de erro de codificação nem de duplicação, língua detetada com margem confortável e segmentação de frases sem anomalias.

## 3. Resumo dos principais resultados

| Indicador | Valor | Unidade |
| --- | --- | --- |
| Diversidade lexical (MTLD) | 139,0 | palavras por fator |
| Extensão mediana das frases | 9 | palavras |
| Profundidade sintática | 3,29 | níveis |
| Densidade lexical | 49,3 | % das palavras |
| Parágrafos de diálogo | 52,4 | % dos parágrafos |
| Legibilidade (Flesch adaptado) | 64,0 | 0–100 (aprox.) |

## 4. Diversidade lexical

O TTR depende da extensão do texto e não deve ser usado sozinho para comparar livros de tamanhos diferentes; o MTLD e o HD-D são os índices de referência (McCarthy e Jarvis, 2010). Todos dependem da língua.

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **MTLD** | 139,0 | palavras por fator | Mais alto = vocabulário mais variado. É o índice menos dependente da extensão do texto na validação de McCarthy e Jarvis (2010). |
| **HD-D** | 0,884 | 0–1 | Mais alto = vocabulário mais variado. Alternativa probabilística ao vocd-D. |
| **MATTR** | 0,575 | 0–1 | Mais alto = vocabulário mais variado. Comparável entre textos da mesma língua com pelo menos W palavras e a mesma janela. |
| **K de Yule** | 78,2 | índice (×10⁴) | Mais baixo = vocabulário menos repetitivo. |
| **TTR (type-token ratio)** | 0,094 | 0–1 | Mais alto = vocabulário mais variado, mas só para textos de extensão semelhante. |
| **Hapax legomena** | 48,2 | % do vocabulário | Mais alto = mais vocabulário raro ou ocasional. |
| **Vocabulário** | 19 068 | formas | Mais alto = mais formas diferentes. |

<details><summary>Definições</summary>

- **MTLD**: Extensão média (em palavras) dos segmentos sequenciais que mantêm um TTR acima de 0,72; média das passagens no sentido direto e inverso. Fórmula: `N / número de fatores (com fator parcial no fim)`.
- **HD-D**: Contributo médio de cada forma para o TTR esperado numa amostra aleatória de 42 palavras, calculado pela distribuição hipergeométrica. Fórmula: `Σ_formas [1 − P(X = 0)] / 42, X ~ Hipergeométrica(N, f, 42)`.
- **MATTR**: Média do TTR em todas as janelas consecutivas de W palavras (W = 500 por omissão; configurável). Fórmula: `média sobre i de TTR(palavras i … i+W−1)`.
- **K de Yule**: Concentração do vocabulário a partir do espetro de frequências. Fórmula: `10⁴ × (Σ_m m²·V(m) − N) / N²`.
- **TTR (type-token ratio)**: Formas distintas ÷ palavras. Fórmula: `V / N`.
- **Hapax legomena**: Formas que ocorrem uma única vez, em % do vocabulário.
- **Vocabulário**: Número de formas distintas (types), em minúsculas.

</details>

## 5. Extensão das frases e complexidade sintática

A extensão mede quantas palavras tem uma frase; a complexidade sintática mede como essas palavras se organizam (encaixamento, distância entre palavras relacionadas, subordinação). São dimensões distintas.

### Extensão

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Extensão mediana das frases** | 9 | palavras | Metade das frases tem esta extensão ou menos; mais robusta do que a média. |
| **Extensão média das frases** | 12,1 | palavras | Medida de extensão, não de complexidade sintática. |
| **Percentil 25** | 5 | palavras | Com o percentil 75, delimita a metade central das frases. |
| **Percentil 75** | 16 | palavras | Com o percentil 25, delimita a metade central das frases. |
| **Desvio-padrão da extensão** | 11,2 | palavras | Mais alto = alternância maior entre frases curtas e longas. |
| **Frase mais longa** | 121 | palavras | Uma única frase; não descreve o estilo do livro. |
| **Frases longas** | 7,1 | % das frases | Mais alto = mais frases extensas, que exigem mais memória de trabalho na leitura. |
| **Extensão média dos parágrafos** | 35,4 | palavras | Mais alto = blocos de texto mais extensos (narração contínua). |

![Extensão das frases](graficos/extensao-frases.png)
<sub>[SVG](graficos/extensao-frases.svg)</sub>

### Complexidade sintática

Calculada a partir da árvore de dependências do modelo `pt_core_news_md` (exatidão declarada pelo modelo: LAS 0,86).

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Profundidade sintática** | 3,29 | níveis | Mais alto = mais encaixamento (subordinação, complementos aninhados). |
| **Distância de dependência média (MDD)** | 2,45 | palavras | Mais alto = dependências mais longas, associadas a maior esforço de processamento. |
| **Orações subordinadas por frase** | 0,82 | orações por frase | Mais alto = mais subordinação. |

<details><summary>Definições</summary>

- **Profundidade sintática**: Média, por frase, da profundidade máxima da árvore de dependências (raiz = 0). Fórmula: `média_frases(max_palavras profundidade(palavra))`.
- **Distância de dependência média (MDD)**: Média da distância, em palavras, entre cada palavra e a palavra de que depende (sem pontuação nem raiz). Fórmula: `Σ |posição(dependente) − posição(cabeça)| / número de dependências`.
- **Orações subordinadas por frase**: Relações de dependência que introduzem orações subordinadas (advcl, ccomp, csubj, acl, acl:relcl / relcl), por frase.

</details>

## 6. Análise morfossintática

Etiquetas UPOS do modelo `pt_core_news_md` (exatidão declarada: 97,0 %). A exatidão é medida pelo próprio modelo em textos contemporâneos; em textos antigos será mais baixa.

| Classe | Ocorrências | Por 1000 palavras |
| --- | --- | --- |
| Substantivos | 44 135 | 216,8 |
| Preposições | 30 235 | 148,5 |
| Verbos | 28 524 | 140,1 |
| Determinantes | 26 047 | 128,0 |
| Nomes próprios | 16 508 | 81,1 |
| Advérbios | 14 814 | 72,8 |
| Adjetivos | 12 832 | 63,0 |
| Pronomes | 9 858 | 48,4 |
| Conjunções coordenativas | 7 634 | 37,5 |
| Conjunções subordinativas | 5 759 | 28,3 |
| Verbos auxiliares | 5 211 | 25,6 |
| Numerais | 1 368 | 6,7 |

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Densidade lexical** | 49,3 | % das palavras | Mais alto = texto mais informativo e menos marcado por palavras gramaticais. |
| **Pronomes pessoais** | 20,1 | ocorrências por 1000 palavras | Mais alto = narração mais centrada em pessoas e no diálogo. |
| **Verbos modais** | 2,0 | ocorrências por 1000 palavras | Mais alto = mais expressão de possibilidade, obrigação ou hipótese. |
| **Extensão média das palavras** | 4,61 | letras | Mais alto = palavras mais longas, em geral mais raras ou mais derivadas. |

![Classes gramaticais](graficos/classes-gramaticais.png)
<sub>[SVG](graficos/classes-gramaticais.svg)</sub>

## 7. Legibilidade

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Facilidade de leitura (Flesch adaptado)** | 64,0 | 0–100 (aprox.) | Mais alto = leitura mais fácil. |
| **Flesch-Kincaid (nível de escolaridade)** | *não aplicável* (fórmula calibrada apenas para inglês) | ano escolar (EUA) | Mais alto = texto mais exigente. |
| **Sílabas por palavra** | 2,04 | sílabas | Mais alto = palavras mais longas; entra nas fórmulas de legibilidade. |

> A fórmula usada é a adaptação de Martins et al. (1996), calibrada com manuais escolares em português do Brasil. Não foi validada para o português europeu nem para prosa literária: o valor serve para comparar livros em português entre si, não como medida absoluta. As sílabas são estimadas por regras ortográficas (ver a exatidão medida em `docs/indicadores.md`).

<details><summary>Definições</summary>

- **Facilidade de leitura (Flesch adaptado)**: Índice de Flesch com os coeficientes da adaptação de cada língua. Fórmula: `en: 206,835 − 1,015·PF − 84,6·SP; fr: 207 − 1,015·PF − 73,6·SP; pt: 248,835 − 1,015·PF − 84,6·SP (PF = palavras/frase, SP = sílabas/palavra)`.
- **Sílabas por palavra**: Estimativa por grupos de vogais, com regras para ditongos (pt) e vogais mudas (fr, en).

</details>

## 8. Análise lexical e discursiva

### Palavras de conteúdo mais frequentes

![Frequências](graficos/frequencias.png)
<sub>[SVG](graficos/frequencias.svg)</sub>

| Lema | Classe | Ocorrências | Por 1000 palavras |
| --- | --- | --- | --- |
| dizer | VERB | 604 | 2,97 |
| mão | NOUN | 471 | 2,31 |
| ter | VERB | 410 | 2,01 |
| olho | NOUN | 388 | 1,91 |
| casa | NOUN | 334 | 1,64 |
| dia | NOUN | 328 | 1,61 |
| haver | VERB | 315 | 1,55 |
| ficar | VERB | 302 | 1,48 |
| homem | NOUN | 284 | 1,40 |
| braço | NOUN | 271 | 1,33 |
| vir | VERB | 269 | 1,32 |
| passar | VERB | 267 | 1,31 |
| amigo | NOUN | 262 | 1,29 |
| dar | VERB | 259 | 1,27 |
| senhora | NOUN | 254 | 1,25 |
| noite | NOUN | 246 | 1,21 |
| velho | ADJ | 236 | 1,16 |
| exclamar | VERB | 228 | 1,12 |
| ver | VERB | 219 | 1,08 |
| mulher | NOUN | 217 | 1,07 |

### Pontuação e diálogo

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Vírgulas** | 123,4 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Pontos finais** | 44,8 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Pontos e vírgulas** | 5,9 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Dois pontos** | 8,1 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Pontos de exclamação** | 15,0 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Pontos de interrogação** | 6,6 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Reticências** | 17,6 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Travessões** | 17,6 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Aspas** | 4,3 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Parênteses** | 0,4 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Parágrafos de diálogo (estimativa)** | 52,4 | % dos parágrafos | Aproximação do peso do discurso direto. |

### Entidades nomeadas

Reconhecimento automático (NER): estimativas sujeitas a erro.

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Pessoas distintas (NER)** | 1 641 | nomes | Ordem de grandeza do elenco nomeado. |
| **Lugares distintos (NER)** | 1 315 | nomes | Ordem de grandeza dos espaços nomeados. |
| **Organizações distintas (NER)** | 241 | nomes | Ordem de grandeza das instituições nomeadas. |
| **Menções de entidades** | 62,5 | ocorrências por 1000 palavras | Densidade de referências nomeadas. |

![Entidades](graficos/entidades.png)
<sub>[SVG](graficos/entidades.svg)</sub>

### Rede de personagens

Identificação: dicionário (eca-de-queiros-os-maias.json). Duas personagens ligam-se quando aparecem no mesmo parágrafo: é uma co-ocorrência textual, não uma relação narrativa comprovada.

![Rede de personagens](graficos/rede.png)
<sub>[SVG](graficos/rede.svg)</sub>

| Personagem | Menções | Ligações | Parágrafos partilhados | Intermediação | PageRank | Comunidade |
| --- | --- | --- | --- | --- | --- | --- |
| Carlos da Maia | 1 816 | 33 | 1 427 | 0,913 | 0,189 | 1 |
| João da Ega | 1 125 | 31 | 1 004 | 0,307 | 0,132 | 1 |
| Maria Eduarda | 321 | 26 | 380 | 0,000 | 0,052 | 1 |
| Afonso da Maia | 320 | 26 | 363 | 0,055 | 0,051 | 2 |
| Dâmaso Salcede | 415 | 26 | 365 | 0,000 | 0,050 | 1 |
| Vilaça | 309 | 28 | 282 | 0,004 | 0,041 | 2 |
| Craft | 239 | 25 | 275 | 0,000 | 0,039 | 1 |
| Condessa de Gouvarinho | 181 | 24 | 211 | 0,000 | 0,032 | 3 |
| Tomás de Alencar | 204 | 26 | 206 | 0,000 | 0,031 | 2 |
| Cruges | 177 | 25 | 198 | 0,000 | 0,029 | 4 |
| Maria Monforte | 116 | 16 | 137 | 0,059 | 0,024 | 2 |
| Taveira | 83 | 22 | 137 | 0,000 | 0,022 | 4 |
| Conde de Gouvarinho | 89 | 22 | 137 | 0,000 | 0,022 | 3 |
| Pedro da Maia | 129 | 18 | 126 | 0,004 | 0,022 | 2 |
| Jacob Cohen | 95 | 17 | 121 | 0,000 | 0,019 | 1 |

## 9. Evolução ao longo do texto

O livro foi dividido em 10 segmentos com o mesmo número de palavras.

![Evolução](graficos/evolucao.png)
<sub>[SVG](graficos/evolucao.svg)</sub>

| Segmento | Palavras | MTLD | Frase média | Densidade lexical (%) | Diálogo (%) | Pessoas / 1000 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 20 356 | 146,1 | 14,8 | 49,5 | 41 | 36,7 |
| 2 | 20 356 | 144,3 | 13,9 | 48,9 | 55 | 40,0 |
| 3 | 20 356 | 135,4 | 12,1 | 48,7 | 53 | 44,2 |
| 4 | 20 356 | 134,6 | 12,2 | 50,0 | 49 | 39,1 |
| 5 | 20 355 | 136,0 | 12,5 | 50,4 | 48 | 32,6 |
| 6 | 20 356 | 131,4 | 11,7 | 49,1 | 55 | 39,1 |
| 7 | 20 356 | 139,0 | 11,5 | 50,0 | 50 | 35,5 |
| 8 | 20 356 | 137,5 | 11,7 | 47,9 | 61 | 43,5 |
| 9 | 20 356 | 139,2 | 10,9 | 48,5 | 57 | 39,8 |
| 10 | 20 355 | 145,9 | 11,1 | 49,7 | 56 | 40,9 |

## 10. Visualizações

- [Painel interativo](painel.html): rede de personagens em 3D, centralidade, frequências, classes gramaticais, frases, evolução e lugares (abrir num navegador).
- Gráficos estáticos em PNG e SVG na pasta [`graficos/`](graficos/).

## 11. Interpretação

Comentários gerados automaticamente a partir dos valores; descrevem o texto, não explicam as suas causas nem substituem a leitura crítica.

- Metade das frases tem até 9 palavras e a metade central das frases está entre 5 e 16 palavras; 7,1 % têm mais de 30 palavras.
- A extensão das frases varia muito (desvio-padrão próximo da média): alternância marcada entre frases curtas e longas.
- A média (12,1) é bastante superior à mediana: algumas frases muito longas puxam a média para cima, por isso a mediana descreve melhor a frase típica.
- Diversidade lexical: MTLD de 139,0 palavras por fator, ou seja, em média são precisas cerca de 139 palavras até o TTR descer abaixo de 0,72. Este valor só é comparável com livros em português.
- Cerca de 52 % dos parágrafos foram identificados como diálogo (estimativa tipográfica).
- Em média, 0,82 orações subordinadas por frase e uma profundidade sintática média de 3,29 níveis.
- Do primeiro ao último segmento, o MTLD passa de 146,1 para 145,9 e a extensão média das frases de 14,8 para 11,1 palavras (variação descritiva; segmentos isolados são instáveis).
- A rede inclui 35 personagens; a mais central (PageRank) é Carlos da Maia.

## 12. Limitações metodológicas

- **MTLD**: Pouco fiável abaixo de cerca de 100 palavras; valores de línguas diferentes não são comparáveis (a morfologia altera o número de formas).
- **HD-D**: Não aplicável a textos com menos de 42 palavras; não comparável entre línguas.
- **MATTR**: Depende da janela escolhida; não aplicável a textos com menos de W palavras.
- **K de Yule**: Relativamente estável com a extensão, mas sensível às palavras muito frequentes.
- **TTR (type-token ratio)**: Diminui sistematicamente com a extensão do texto; não deve ser usado isoladamente para comparar livros de dimensões diferentes.
- **Hapax legomena**: Depende da extensão do texto e da ortografia (grafias antigas e gralhas contam como formas novas).
- **Vocabulário**: Cresce com a extensão do texto: não serve para comparar textos de tamanhos diferentes.
- **Extensão mediana das frases**: Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática.
- **Extensão média das frases**: Sensível a erros de segmentação e a frases muito longas (assimetria).
- **Percentil 25**: Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática.
- **Percentil 75**: Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática.
- **Desvio-padrão da extensão**: Sensível a frases extremas (incluindo erros de segmentação); a distribuição é assimétrica, por isso os percentis descrevem-na melhor.
- **Frase mais longa**: Valores muito altos indicam muitas vezes erros de segmentação (listas, versos, texto sem pontuação final).
- **Frases longas**: O limiar de 30 palavras é uma convenção (configurável).
- **Extensão média dos parágrafos**: Depende da paginação da edição (diálogos geram muitos parágrafos curtos).
- **Profundidade sintática**: Depende da qualidade do analisador sintático e das convenções de anotação de cada modelo; correlaciona-se com a extensão das frases.
- **Distância de dependência média (MDD)**: Depende do analisador e da ordem das palavras de cada língua.
- **Orações subordinadas por frase**: Estimativa a partir da anotação Universal Dependencies (modelos pt e fr) ou ClearNLP (modelo en); xcomp não conta.
- **Facilidade de leitura (Flesch adaptado)**: As adaptações não são equivalentes entre si: não comparar valores de línguas diferentes. A adaptação portuguesa foi calibrada com manuais escolares em português do Brasil e não foi validada para português europeu nem para prosa literária.
- **Parágrafos de diálogo (estimativa)**: Heurística tipográfica: falha com convenções invulgares e conta citações como diálogo.
- **Pessoas distintas (NER)**: Sobrestimado por variantes do mesmo nome e por erros do reconhecimento de entidades.
- **Densidade lexical**: Depende da etiquetagem morfossintática; os verbos auxiliares não contam como conteúdo.
- **Modelos linguísticos**: os modelos spaCy foram treinados com texto contemporâneo; grafias antigas, diálogos e pontuação literária reduzem a exatidão da segmentação, da etiquetagem e da análise sintática.

## 13. Referências metodológicas

- Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). *Journal of Quantitative Linguistics, 17*(2), 94–100.
- Flesch, R. (1948). A new readability yardstick. *Journal of Applied Psychology, 32*(3), 221–233. https://doi.org/10.1037/h0057532
- Kandel, L., & Moles, A. (1958). Application de l'indice de Flesch à la langue française. *Cahiers d'Études de Radio-Télévision, 19*.
- Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. *Journal of Cognitive Science, 9*(2), 159–191. https://hdl.handle.net/10371/70907
- Martins, T. B. F., Ghiraldelo, C. M., Nunes, M. G. V., & Oliveira Jr., O. N. (1996). *Readability formulas applied to textbooks in Brazilian Portuguese* (Notas do ICMSC-USP, Série Computação, 28). ICMSC-USP.
- McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods, 42*(2), 381–392. https://doi.org/10.3758/BRM.42.2.381
- Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020). Universal Dependencies v2: An evergrowing multilingual treebank collection. In *Proceedings of the 12th Language Resources and Evaluation Conference* (pp. 4034–4043). European Language Resources Association. https://aclanthology.org/2020.lrec-1.497
- Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? Measures of lexical richness in perspective. *Computers and the Humanities, 32*(5), 323–352. https://doi.org/10.1023/A:1001749303137
- Ure, J. (1971). Lexical density and register differentiation. In G. E. Perren & J. L. M. Trim (Eds.), *Applications of linguistics* (pp. 443–452). Cambridge University Press.
- Yule, G. U. (1944). *The statistical study of literary vocabulary*. Cambridge University Press.
- Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). *spaCy: Industrial-strength natural language processing in Python* [Software]. Zenodo. https://doi.org/10.5281/zenodo.1212303

<sub>Processado em 2026-11-06 10:32 UTC · livros_pln 3.1.0 · código `872cc50466db` · commit `725f504` · Python 3.13.5 · spaCy 3.8.18 · pt_core_news_md 3.8.0</sub>
