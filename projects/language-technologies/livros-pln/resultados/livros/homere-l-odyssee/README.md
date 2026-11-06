# L'Odyssée

**Homère**

[← Todos os livros](../../README.md) · **[Painel interativo](painel.html)** (rede de personagens em 3D) · [Excel](homere-l-odyssee.xlsx) · [JSON](indicadores.json)

## 1. Identificação e metadados

| Campo | Valor |
| --- | --- |
| Título | L'Odyssée |
| Autor | Homère |
| Ano | *desconhecido* |
| Idioma | Francês |
| Fonte | Project Gutenberg, n.º 14286 (tradução de Leconte de Lisle) |

<sub>Ficheiro `homere-l-odyssee.txt` · modelo linguístico `fr_core_news_md` 3.8.0</sub>

## 2. Características do texto

Forma: **prosa**.

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Palavras** | 111 968 | palavras | Base de normalização de quase todos os indicadores. |
| **Frases** | 6 617 | frases | Base para as médias e distribuições por frase. |
| **Parágrafos** | 1 634 | parágrafos | Base para a proporção de diálogo e a extensão dos parágrafos. |
| **Tempo de leitura estimado** | 7,8 | horas | Ordem de grandeza, não uma previsão individual. |

Sem avisos de qualidade: texto não vazio, sem sinais de erro de codificação nem de duplicação, língua detetada com margem confortável e segmentação de frases sem anomalias.

## 3. Resumo dos principais resultados

| Indicador | Valor | Unidade |
| --- | --- | --- |
| Diversidade lexical (MTLD) | 100,5 | palavras por fator |
| Extensão mediana das frases | 16 | palavras |
| Profundidade sintática | 3,87 | níveis |
| Densidade lexical | 45,8 | % das palavras |
| Parágrafos de diálogo | 40,6 | % dos parágrafos |
| Legibilidade (Flesch adaptado) | 83,3 | 0–100 (aprox.) |

## 4. Diversidade lexical

O TTR depende da extensão do texto e não deve ser usado sozinho para comparar livros de tamanhos diferentes; o MTLD e o HD-D são os índices de referência (McCarthy e Jarvis, 2010). Todos dependem da língua.

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **MTLD** | 100,5 | palavras por fator | Mais alto = vocabulário mais variado. É o índice menos dependente da extensão do texto na validação de McCarthy e Jarvis (2010). |
| **HD-D** | 0,866 | 0–1 | Mais alto = vocabulário mais variado. Alternativa probabilística ao vocd-D. |
| **MATTR** | 0,515 | 0–1 | Mais alto = vocabulário mais variado. Comparável entre textos da mesma língua com pelo menos W palavras e a mesma janela. |
| **K de Yule** | 97,9 | índice (×10⁴) | Mais baixo = vocabulário menos repetitivo. |
| **TTR (type-token ratio)** | 0,072 | 0–1 | Mais alto = vocabulário mais variado, mas só para textos de extensão semelhante. |
| **Hapax legomena** | 43,7 | % do vocabulário | Mais alto = mais vocabulário raro ou ocasional. |
| **Vocabulário** | 8 115 | formas | Mais alto = mais formas diferentes. |

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
| **Extensão mediana das frases** | 16 | palavras | Metade das frases tem esta extensão ou menos; mais robusta do que a média. |
| **Extensão média das frases** | 16,9 | palavras | Medida de extensão, não de complexidade sintática. |
| **Percentil 25** | 9 | palavras | Com o percentil 75, delimita a metade central das frases. |
| **Percentil 75** | 23 | palavras | Com o percentil 25, delimita a metade central das frases. |
| **Desvio-padrão da extensão** | 11,0 | palavras | Mais alto = alternância maior entre frases curtas e longas. |
| **Frase mais longa** | 101 | palavras | Uma única frase; não descreve o estilo do livro. |
| **Frases longas** | 10,8 | % das frases | Mais alto = mais frases extensas, que exigem mais memória de trabalho na leitura. |
| **Extensão média dos parágrafos** | 69,6 | palavras | Mais alto = blocos de texto mais extensos (narração contínua). |

![Extensão das frases](graficos/extensao-frases.png)
<sub>[SVG](graficos/extensao-frases.svg)</sub>

### Complexidade sintática

Calculada a partir da árvore de dependências do modelo `fr_core_news_md` (exatidão declarada pelo modelo: LAS 0,86).

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Profundidade sintática** | 3,87 | níveis | Mais alto = mais encaixamento (subordinação, complementos aninhados). |
| **Distância de dependência média (MDD)** | 2,60 | palavras | Mais alto = dependências mais longas, associadas a maior esforço de processamento. |
| **Orações subordinadas por frase** | 0,89 | orações por frase | Mais alto = mais subordinação. |

<details><summary>Definições</summary>

- **Profundidade sintática**: Média, por frase, da profundidade máxima da árvore de dependências (raiz = 0). Fórmula: `média_frases(max_palavras profundidade(palavra))`.
- **Distância de dependência média (MDD)**: Média da distância, em palavras, entre cada palavra e a palavra de que depende (sem pontuação nem raiz). Fórmula: `Σ |posição(dependente) − posição(cabeça)| / número de dependências`.
- **Orações subordinadas por frase**: Relações de dependência que introduzem orações subordinadas (advcl, ccomp, csubj, acl, acl:relcl / relcl), por frase.

</details>

## 6. Análise morfossintática

Etiquetas UPOS do modelo `fr_core_news_md` (exatidão declarada: 97,1 %). A exatidão é medida pelo próprio modelo em textos contemporâneos; em textos antigos será mais baixa.

| Classe | Ocorrências | Por 1000 palavras |
| --- | --- | --- |
| Substantivos | 21 113 | 188,6 |
| Verbos | 15 947 | 142,4 |
| Determinantes | 14 919 | 133,2 |
| Preposições | 13 475 | 120,3 |
| Pronomes | 13 046 | 116,5 |
| Conjunções coordenativas | 8 881 | 79,3 |
| Adjetivos | 7 697 | 68,7 |
| Advérbios | 6 546 | 58,5 |
| Nomes próprios | 4 132 | 36,9 |
| Verbos auxiliares | 3 867 | 34,5 |
| Conjunções subordinativas | 1 902 | 17,0 |
| Numerais | 322 | 2,9 |

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Densidade lexical** | 45,8 | % das palavras | Mais alto = texto mais informativo e menos marcado por palavras gramaticais. |
| **Pronomes pessoais** | 111,8 | ocorrências por 1000 palavras | Mais alto = narração mais centrada em pessoas e no diálogo. |
| **Verbos modais** | 2,4 | ocorrências por 1000 palavras | Mais alto = mais expressão de possibilidade, obrigação ou hipótese. |
| **Extensão média das palavras** | 4,45 | letras | Mais alto = palavras mais longas, em geral mais raras ou mais derivadas. |

![Classes gramaticais](graficos/classes-gramaticais.png)
<sub>[SVG](graficos/classes-gramaticais.svg)</sub>

## 7. Legibilidade

**Leitura fácil** · índice 83,3 · faixa «fácil»

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Facilidade de leitura (Flesch adaptado)** | 83,3 | 0–100 (aprox.) | Mais alto = leitura mais fácil. Faixas em português (Martins et al., 1996): 75–100 muito fácil (1.º–4.º ano de escolaridade), 50–75 fácil (5.º–8.º ano), 25–50 razoavelmente difícil (ensino secundário e superior), abaixo de 25 muito difícil (textos académicos). Em inglês e francês, escala de Flesch (1948): 90 muito fácil, 80 fácil, 70 razoavelmente fácil, 60 padrão, 50 razoavelmente difícil, 30 difícil, abaixo muito difícil. O painel resume em «fácil» (pt ≥ 50; en e fr ≥ 60) ou «difícil». |
| **Flesch-Kincaid (nível de escolaridade)** | *não aplicável* (fórmula calibrada apenas para inglês) | ano escolar (EUA) | Mais alto = texto mais exigente. |
| **Sílabas por palavra** | 1,45 | sílabas | Mais alto = palavras mais longas; entra nas fórmulas de legibilidade. |

> A fórmula usada é a adaptação de Kandel e Moles (1958); não é equivalente às de outras línguas. As sílabas são estimadas por regras ortográficas (ver a exatidão medida em `docs/indicadores.md`).

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
| demeure | NOUN | 615 | 5,49 |
| homme | NOUN | 531 | 4,74 |
| parler | VERB | 525 | 4,69 |
| dieu | NOUN | 422 | 3,77 |
| nef | NOUN | 421 | 3,76 |
| grand | ADJ | 332 | 2,97 |
| répondre | VERB | 299 | 2,67 |
| terre | NOUN | 288 | 2,57 |
| fils | NOUN | 281 | 2,51 |
| divin | ADJ | 253 | 2,26 |
| compagnon | NOUN | 246 | 2,20 |
| prétendant | NOUN | 241 | 2,15 |
| père | NOUN | 241 | 2,15 |
| point | NOUN | 236 | 2,11 |
| femme | NOUN | 233 | 2,08 |
| parole | NOUN | 232 | 2,07 |
| faire | VERB | 225 | 2,01 |
| main | NOUN | 220 | 1,96 |
| venir | VERB | 218 | 1,95 |
| cher | ADJ | 207 | 1,85 |

### Pontuação e diálogo

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Vírgulas** | 106,5 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Pontos finais** | 39,1 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Pontos e vírgulas** | 6,8 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Dois pontos** | 6,4 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Pontos de exclamação** | 2,7 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Pontos de interrogação** | 2,7 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Reticências** | 0,0 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Travessões** | 6,1 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Aspas** | 0,0 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Parênteses** | 0,0 | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. |
| **Parágrafos de diálogo (estimativa)** | 40,6 | % dos parágrafos | Aproximação do peso do discurso direto. |

### Entidades nomeadas

Reconhecimento automático (NER): estimativas sujeitas a erro.

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Pessoas distintas (NER)** | 420 | nomes | Ordem de grandeza do elenco nomeado. |
| **Lugares distintos (NER)** | 328 | nomes | Ordem de grandeza dos espaços nomeados. |
| **Organizações distintas (NER)** | 54 | nomes | Ordem de grandeza das instituições nomeadas. |
| **Menções de entidades** | 38,0 | ocorrências por 1000 palavras | Densidade de referências nomeadas. |

![Entidades](graficos/entidades.png)
<sub>[SVG](graficos/entidades.svg)</sub>

### Rede de personagens

Identificação: dicionário (homere-l-odyssee.json). Duas personagens ligam-se quando aparecem no mesmo parágrafo: é uma co-ocorrência textual, não uma relação narrativa comprovada.

![Rede de personagens](graficos/rede.png)
<sub>[SVG](graficos/rede.svg)</sub>

| Personagem | Menções | Ligações | Parágrafos partilhados | Intermediação | PageRank | Comunidade |
| --- | --- | --- | --- | --- | --- | --- |
| Odysseus | 711 | 33 | 512 | 0,881 | 0,188 | 2 |
| Zeus | 267 | 31 | 289 | 0,254 | 0,106 | 1 |
| Tèlémakhos | 268 | 24 | 265 | 0,111 | 0,095 | 2 |
| Athènè | 175 | 27 | 220 | 0,000 | 0,079 | 2 |
| Hèlios | 90 | 26 | 103 | 0,161 | 0,043 | 1 |
| Pènélopéia | 114 | 15 | 105 | 0,000 | 0,039 | 2 |
| Ménélaos | 65 | 19 | 78 | 0,054 | 0,032 | 3 |
| Nestôr | 42 | 12 | 55 | 0,000 | 0,023 | 3 |
| Apollôn | 28 | 20 | 52 | 0,000 | 0,023 | 1 |
| Antinoos | 59 | 13 | 54 | 0,000 | 0,023 | 2 |
| Alkinoos | 73 | 10 | 51 | 0,000 | 0,023 | 4 |
| Laertès | 34 | 15 | 52 | 0,000 | 0,022 | 2 |
| Eumaios | 56 | 13 | 49 | 0,000 | 0,021 | 2 |
| Poseidaôn | 47 | 18 | 45 | 0,000 | 0,020 | 1 |
| Agamemnôn | 23 | 17 | 43 | 0,000 | 0,020 | 1 |

## 9. Evolução ao longo do texto

O livro foi dividido em 10 segmentos com o mesmo número de palavras.

![Evolução](graficos/evolucao.png)
<sub>[SVG](graficos/evolucao.svg)</sub>

| Segmento | Palavras | MTLD | Frase média | Densidade lexical (%) | Diálogo (%) | Pessoas / 1000 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 11 197 | 118,8 | 16,1 | 46,2 | 38 | 32,7 |
| 2 | 11 197 | 100,0 | 18,1 | 45,1 | 39 | 27,9 |
| 3 | 11 197 | 92,4 | 19,1 | 45,8 | 39 | 25,9 |
| 4 | 11 197 | 93,2 | 17,7 | 45,9 | 35 | 17,3 |
| 5 | 11 196 | 99,6 | 17,2 | 46,1 | 39 | 22,2 |
| 6 | 11 197 | 100,1 | 17,9 | 45,3 | 37 | 22,8 |
| 7 | 11 197 | 102,6 | 15,0 | 45,1 | 46 | 28,4 |
| 8 | 11 197 | 111,3 | 15,7 | 46,3 | 46 | 28,7 |
| 9 | 11 197 | 97,8 | 16,5 | 46,5 | 45 | 29,1 |
| 10 | 11 196 | 93,7 | 16,7 | 45,8 | 43 | 29,3 |

## 10. Sentimento

Método: VADER-FR (VADER adaptado ao francês) 1.3.4, com léxico e regras (Hutto e Gilbert, 2014). Cada frase com pelo menos 3 palavras recebe uma pontuação entre −1 e +1. Os léxicos foram criados para mensagens curtas das redes sociais: os valores descrevem a polaridade do vocabulário, não o tom da narrativa, e não foram validados com anotação humana neste projeto.

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Sentimento médio** | 0,089 | −1 a +1 | Acima de 0 = vocabulário globalmente positivo; abaixo de 0 = negativo. Valores entre −0,05 e +0,05 são neutros. |
| **Frases positivas** | 46,8 | % das frases pontuadas | Proporção de frases com vocabulário predominantemente positivo. |
| **Frases negativas** | 25,2 | % das frases pontuadas | Proporção de frases com vocabulário predominantemente negativo. |
| **Frases neutras** | 28,0 | % das frases pontuadas | Inclui frases sem nenhuma palavra do léxico. |
| **Cobertura do léxico de sentimento** | 7,1 | % das palavras | Indicador de qualidade: abaixo de ~5 %, o sentimento assenta em muito poucas palavras. |

![Arco de sentimento](graficos/sentimento.png)
<sub>[SVG](graficos/sentimento.svg)</sub>

**Frases com pontuação mais extrema** (entre 8 e 60 palavras)

| Polaridade | Compound | Frase |
| --- | --- | --- |
| positiva | 0,950 | Il parla ainsi en priant, et le très sage Zeus l'entendit, et, aussitôt, il tonna du haut de l'Olympos éclatant et par-dessus les nuées, et le divin Odysseus s'en réjouit. |
| positiva | 0,938 | Mais les dieux heureux n'aiment pas les actions impies, et ils aiment au contraire la justice et les actions équitables. |
| positiva | 0,938 | et les femmes se parèrent, et le divin aoide fit vibrer sa kithare sonore et leur inspira le désir du doux chant et de la danse joyeuse, et la grande demeure résonna sous les pieds des hommes qui dansaient et des femmes aux belles ceintures. |
| negativa | −0,964 | Et si, étant seul, leur multitude me domptait, j'aimerais mieux être tué dans mes demeures que de voir ces choses honteuses: mes hôtes maltraités, mes servantes misérablement violées dans mes belles demeures, mon vin épuisé, mes vivres dévorés effrontément, et cela pour un… |
| negativa | −0,922 | mais, si tu désires m'entendre, certes, je ne refuserai pas de raconter les misères et les douleurs de mes compagnons, de ceux qui ont péri auparavant, ou qui, ayant échappé à la guerre lamentable des Troiens, ont péri au retour par la ruse d'une femme perfide. |
| negativa | −0,920 | J'ai tué les prétendants dans nos demeures, châtiant leurs indignes outrages et leurs mauvaises actions. |

<details><summary>Definições</summary>

- **Sentimento médio**: Média da pontuação «compound» do VADER nas frases com pelo menos 3 palavras. Fórmula: `média das pontuações compound por frase`.
- **Frases positivas**: Frases com compound ≥ 0,05. Fórmula: `frases com compound ≥ 0,05 ÷ frases pontuadas × 100`.
- **Frases negativas**: Frases com compound ≤ −0,05. Fórmula: `frases com compound ≤ −0,05 ÷ frases pontuadas × 100`.
- **Frases neutras**: Frases com compound entre −0,05 e 0,05.
- **Cobertura do léxico de sentimento**: Palavras do texto que existem no léxico de sentimento usado.

</details>

### Tonalidade emocional (experimental)

**Predominantemente positivo (feliz)**. Intervalo de confiança a 95 % da polaridade média dos 24 segmentos: [0,072; 0,116], inteiramente acima de +0,050. Atenção: no léxico de emoções NRC, a razão alegria/tristeza é 0,74, com mais vocabulário de tristeza do que de alegria. Os dois léxicos divergem: a classificação deve ser lida com prudência..

Classificação interpretativa: polaridade por frase do método de sentimento, média por capítulo e intervalo de confiança a 95 % por bootstrap dos capítulos. Positivo/negativo: intervalo inteiro acima de +0,05 / abaixo de −0,05; misto: pelo menos 10 % de frases fortemente positivas e 10 % fortemente negativas; neutro: intervalo entre −0,05 e +0,05; indeterminado nos restantes casos. Não validada com anotação humana.

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Intensidade da polaridade** | 0,286 | 0 a 1 | Distingue um livro neutro por ausência de emoção (valor baixo) de um livro neutro por equilíbrio entre frases muito positivas e muito negativas (valor alto). |
| **Oscilação entre capítulos** | 0,056 | desvio-padrão | Valores altos indicam capítulos com tonalidades muito diferentes; baixos, uma tonalidade estável. |
| **Frases fortemente positivas** | 16,3 | % das frases pontuadas | Momentos de vocabulário claramente positivo. |
| **Frases fortemente negativas** | 7,7 | % das frases pontuadas | Momentos de vocabulário claramente negativo. |
| **Polaridade média: limite inferior (IC 95 %)** | 0,072 | −1 a +1 | Com o limite superior, mostra a incerteza da tonalidade: um intervalo largo pede prudência. |
| **Polaridade média: limite superior (IC 95 %)** | 0,116 | −1 a +1 | Ver o limite inferior. |
| **Frases ambivalentes** | 41,2 | % das frases | Mistura de valências na mesma frase (por exemplo, «uma alegria triste»). |
| **Concordância entre léxicos** | 0,36 | −1 a +1 | Verificação de convergência entre dois léxicos independentes: valores baixos pedem mais prudência na leitura da tonalidade. Não é uma validação: nenhum dos léxicos foi comparado com anotação humana aqui. |
| **Frases em discurso direto** | 52,9 | % das frases | Permite separar as emoções do discurso direto (personagens) das da narração. |

### Emoções (léxico NRC, modelo de Plutchik)

Léxico: NRC EmoLex v0.92 (tradução automática do inglês (Google Translate, 2022) — experimental). Emoção mais frequente: **confianca**. Por capítulo, por fase (início, desenvolvimento, conclusão) e por canal (narração e discurso direto): [`emocoes-por-capitulo.csv`](emocoes-por-capitulo.csv), [`emocoes-por-fase.csv`](emocoes-por-fase.csv), [`emocoes-narracao-dialogo.csv`](emocoes-narracao-dialogo.csv).

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Intensidade emocional** | 228,1 | ocorrências por 1000 palavras | Quanto do vocabulário está associado a alguma emoção. |
| **Diversidade emocional** | 0,969 | 0 a 1 | 1 = as oito emoções com o mesmo peso; perto de 0 = uma emoção domina. |
| **Cobertura do léxico de emoções** | 16,0 | % das palavras | Indicador de qualidade: com cobertura baixa, as emoções assentam em poucas palavras. |
| **Palavras emocionais negadas** | 5,4 | % das palavras do léxico | Indicador do efeito da regra de negação. |
| **Razão alegria / tristeza** | 0,74 | razão | Acima de 1 = mais vocabulário de alegria do que de tristeza. |
| **Alegria** | 26,85 | ocorrências por 1000 palavras | Intensidade relativa do vocabulário de alegria (modelo de Plutchik). |
| **Tristeza** | 36,34 | ocorrências por 1000 palavras | Intensidade relativa do vocabulário de tristeza (modelo de Plutchik). |
| **Medo** | 33,22 | ocorrências por 1000 palavras | Intensidade relativa do vocabulário de medo (modelo de Plutchik). |
| **Raiva** | 24,76 | ocorrências por 1000 palavras | Intensidade relativa do vocabulário de raiva (modelo de Plutchik). |
| **Aversão** | 15,13 | ocorrências por 1000 palavras | Intensidade relativa do vocabulário de aversão (modelo de Plutchik). |
| **Surpresa** | 13,45 | ocorrências por 1000 palavras | Intensidade relativa do vocabulário de surpresa (modelo de Plutchik). |
| **Confiança** | 43,96 | ocorrências por 1000 palavras | Intensidade relativa do vocabulário de confiança (modelo de Plutchik). |
| **Antecipação** | 34,37 | ocorrências por 1000 palavras | Intensidade relativa do vocabulário de antecipação (modelo de Plutchik). |

### Género literário inferido (exploratório)

Forma: **Prosa narrativa**. Género inferido: **Romance**. Género bibliográfico (proposto): **Epopeia (tradução francesa em prosa)** — fonte: Project Gutenberg n.º 14286 (assunto LoC: «Epic poetry, Greek -- Translations into French»).

- Muito discurso direto (52,9 % das frases).

| Categoria | Pontuação de regras | Critérios |
| --- | --- | --- |
| Prosa narrativa | 1,00 | ✓ texto em prosa (deteção pela extensão das linhas); ✓ poucos parágrafos com nome de personagem antes da fala (0,0 % < 20 %) |
| Romance | 1,00 | ✓ prosa narrativa; ✓ 111 968 palavras ≥ 40 000 (convenção SFWA) |
| Ensaio | 0,33 | ✓ prosa; ✗ pouco discurso direto (52,9 % < 5 %); ✗ poucas personagens (36 < 5 na rede) |

Regras transparentes sobre indicadores do texto; a pontuação é a fração dos critérios cumpridos (0 se falhar um critério essencial), não uma probabilidade. Limiares de extensão: regras dos prémios Nebula (SFWA). O género bibliográfico não entra no cálculo.

## 11. Outros conceitos de PLN

### Tipos de frase

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Frases interrogativas** | 4,4 | % das frases | Mais alto = mais perguntas, em geral associadas ao diálogo. |
| **Frases exclamativas** | 4,3 | % das frases | Mais alto = mais exclamações, em geral associadas ao diálogo e à expressividade. |

### Tempos verbais e pessoa gramatical

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Verbos no passado** | 36,2 | % das formas verbais finitas com tempo anotado | Mais alto = narração no passado, típica do romance. |
| **Verbos no presente** | 58,9 | % das formas verbais finitas com tempo anotado | Mais alto = narração ou diálogo mais ancorados no presente. |
| **Verbos no futuro** | 4,9 | % das formas verbais finitas com tempo anotado | Mais alto = mais projeção, promessa ou hipótese. |
| **Verbos no conjuntivo** | 2,6 | % das formas verbais finitas com modo anotado | Mais alto = mais hipótese, desejo, dúvida ou subordinação. |
| **Pronomes de 1.ª pessoa** | 42,9 | ocorrências por 1000 palavras | Mais alto = narrador na 1.ª pessoa ou muito diálogo. |
| **Pronomes de 2.ª pessoa** | 2,2 | ocorrências por 1000 palavras | Mais alto = mais interpelação direta, sobretudo no diálogo. |
| **Pronomes de 3.ª pessoa** | 66,6 | ocorrências por 1000 palavras | Mais alto = narração centrada em terceiros, típica do narrador heterodiegético. |

| Tempo | Modo | Ocorrências | % das formas finitas |
| --- | --- | --- | --- |
| presente | indicativo | 6 566 | 53,7 |
| imperfeito | indicativo | 2 393 | 19,6 |
| passado | indicativo | 2 026 | 16,6 |
| futuro | indicativo | 601 | 4,9 |
| presente | conjuntivo | 309 | 2,5 |
| presente | condicional | 251 | 2,1 |
| presente | imperativo | 81 | 0,7 |
| passado | conjuntivo | 11 | 0,1 |

### Leis de Zipf e de Heaps

Duas regularidades estatísticas do vocabulário: poucas palavras são muito frequentes e muitas são raras (Zipf); o vocabulário cresce cada vez mais devagar à medida que o texto avança (Heaps).

| Indicador | Valor | Unidade / escala | Interpretação |
| --- | --- | --- | --- |
| **Expoente de Zipf** | 1,12 | adimensional | Próximo de 1 na maior parte dos textos; mais alto = vocabulário mais concentrado nas palavras mais frequentes. |
| **Ajuste da lei de Zipf (R²)** | 0,995 | 0–1 | Mais perto de 1 = a distribuição segue bem uma lei de potência. |
| **Expoente de Heaps (β)** | 0,669 | adimensional | Entre 0 e 1; mais alto = o livro continua a introduzir palavras novas. |
| **Constante de Heaps (K)** | 4,2 | adimensional | Interpreta-se em conjunto com β; sozinho tem pouco significado. |
| **Ajuste da lei de Heaps (R²)** | 0,997 | 0–1 | Mais perto de 1 = o crescimento do vocabulário segue bem uma lei de potência. |

![Leis de Zipf e de Heaps](graficos/zipf-heaps.png)
<sub>[SVG](graficos/zipf-heaps.svg)</sub>

<details><summary>Definições</summary>

- **Expoente de Zipf**: Declive (com sinal trocado) da reta ajustada à frequência das formas em função da sua posição, em escala log-log. Fórmula: `f(r) ≈ C · r^−s; s = −declive de log f em log r`.
- **Ajuste da lei de Zipf (R²)**: Coeficiente de determinação da reta de Zipf em escala log-log.
- **Expoente de Heaps (β)**: Ritmo de crescimento do vocabulário à medida que o texto avança. Fórmula: `V(N) ≈ K · N^β, ajustado em escala log-log`.
- **Constante de Heaps (K)**: Fator de escala da lei de Heaps. Fórmula: `V(N) ≈ K · N^β`.
- **Ajuste da lei de Heaps (R²)**: Coeficiente de determinação do ajuste de Heaps.

</details>

### Colocações

Pares de palavras contíguas na mesma frase que ocorrem juntas muito mais do que o acaso faria prever; excluem-se os pares formados só por palavras gramaticais. Ordenadas pela razão de verosimilhança G² (Dunning, 1993); o PMI (Church e Hanks, 1990) mede a exclusividade da associação.

| Colocação | Ocorrências | G² | PMI |
| --- | --- | --- | --- |
| parla ainsi | 277 | 2 906,1 | 7,44 |
| lui répondit | 210 | 1 974,4 | 6,93 |
| la mer | 232 | 1 443,6 | 4,88 |
| la terre | 193 | 1 022,6 | 4,54 |
| il parla | 175 | 990,0 | 4,91 |
| divin odysseus | 120 | 934,5 | 6,42 |
| au milieu | 82 | 874,5 | 7,88 |
| paroles ailées | 62 | 831,7 | 9,35 |
| yeux clairs | 57 | 812,1 | 9,84 |
| un dieu | 96 | 781,0 | 6,32 |
| mes compagnons | 92 | 770,8 | 6,94 |
| ainsi parlé | 75 | 671,8 | 7,07 |
| la nef | 143 | 612,1 | 4,03 |
| ces paroles | 68 | 611,7 | 7,39 |
| un homme | 89 | 579,2 | 5,61 |
| les dieux | 137 | 571,6 | 4,00 |
| les prétendants | 125 | 561,2 | 4,19 |
| la demeure | 146 | 532,3 | 3,66 |
| subtil odysseus | 55 | 526,6 | 7,17 |
| aux dieux | 83 | 521,1 | 5,63 |

### Palavras-chave por segmento

Lemas de conteúdo mais característicos de cada segmento, por comparação com os outros segmentos do mesmo livro. Medida: TF-IDF (Spärck Jones, 1972), com os segmentos como documentos.

| Segmento | Palavras-chave |
| --- | --- |
| 1 | aigisthos, festin, tèlémakhos, prétendant, pylos |
| 2 | gérennien, nestôr, phoque, génisse, ménélao |
| 3 | alkinoos, nausikaa, radeau, laodamas, mulet |
| 4 | kyklope, épieu, alkinoos, aiolos, kikône |
| 5 | kirkè, perséphonéia, teirésias, fosse, gaine |
| 6 | porcher, skyllè, légitime, alkinoos, broche |
| 7 | porcher, peiraios, tèlémakhos, phoinikes, pâtre |
| 8 | iros, porcher, antinoos, eurynomè, prétendant |
| 9 | épreuve, autolyko, arc, prétendant, chevrier |
| 10 | amphimédôn, prétendant, pique, verger, cadavre |

## 12. Visualizações

- [Painel interativo](painel.html): gráficos em 3D (com alternativa em 2D) da rede de personagens, centralidade, vocabulário, classes gramaticais, frases, sentimento, evolução, colocações, palavras-chave, tempos verbais e lugares (abrir num navegador).
- Gráficos estáticos em PNG e SVG na pasta [`graficos/`](graficos/).

## 13. Interpretação

Comentários gerados automaticamente a partir dos valores; descrevem o texto, não explicam as suas causas nem substituem a leitura crítica.

- Metade das frases tem até 16 palavras e a metade central das frases está entre 9 e 23 palavras; 10,8 % têm mais de 30 palavras.
- Diversidade lexical: MTLD de 100,5 palavras por fator, ou seja, em média são precisas cerca de 100 palavras até o TTR descer abaixo de 0,72. Este valor só é comparável com livros em francês.
- Cerca de 41 % dos parágrafos foram identificados como diálogo (estimativa tipográfica).
- Em média, 0,89 orações subordinadas por frase e uma profundidade sintática média de 3,87 níveis.
- Do primeiro ao último segmento, o MTLD passa de 118,8 para 93,7 e a extensão média das frases de 16,1 para 16,7 palavras (variação descritiva; segmentos isolados são instáveis).
- Pelo índice de Flesch adaptado (83, «fácil»), a leitura classifica-se como **fácil**. O índice só considera a extensão das frases e das palavras: vocabulário antigo, ironia ou referências culturais não entram no cálculo.
- Sentimento: média de 0,089 (vocabulário globalmente positivo); 47 % das frases pontuadas são positivas e 25 % negativas. Só 7,1 % das palavras existem no léxico, por isso estes valores devem ser lidos com cautela.
- No arco de sentimento, o segmento mais negativo é o 4 (0,035) e o mais positivo o 3 (0,148).
- 36 % das formas verbais finitas estão no passado e 59 % no presente.
- A rede inclui 36 personagens; a mais central (PageRank) é Odysseus.

## 14. Limitações metodológicas

- **Intensidade da polaridade**: Classificação interpretativa e experimental: não foi validada com anotação humana neste projeto. Assenta na polaridade do vocabulário (léxico e regras), que não deteta ironia nem metáforas e não distingue o narrador das personagens. Não mede o que o autor sentiu nem o que o leitor sentirá.
- **Oscilação entre capítulos**: Classificação interpretativa e experimental: não foi validada com anotação humana neste projeto. Assenta na polaridade do vocabulário (léxico e regras), que não deteta ironia nem metáforas e não distingue o narrador das personagens. Não mede o que o autor sentiu nem o que o leitor sentirá. Depende do número e da extensão dos capítulos.
- **Frases fortemente positivas**: Classificação interpretativa e experimental: não foi validada com anotação humana neste projeto. Assenta na polaridade do vocabulário (léxico e regras), que não deteta ironia nem metáforas e não distingue o narrador das personagens. Não mede o que o autor sentiu nem o que o leitor sentirá.
- **Frases fortemente negativas**: Classificação interpretativa e experimental: não foi validada com anotação humana neste projeto. Assenta na polaridade do vocabulário (léxico e regras), que não deteta ironia nem metáforas e não distingue o narrador das personagens. Não mede o que o autor sentiu nem o que o leitor sentirá.
- **Polaridade média: limite inferior (IC 95 %)**: Classificação interpretativa e experimental: não foi validada com anotação humana neste projeto. Assenta na polaridade do vocabulário (léxico e regras), que não deteta ironia nem metáforas e não distingue o narrador das personagens. Não mede o que o autor sentiu nem o que o leitor sentirá. O bootstrap por capítulos supõe que os capítulos são comparáveis entre si.
- **Polaridade média: limite superior (IC 95 %)**: Classificação interpretativa e experimental: não foi validada com anotação humana neste projeto. Assenta na polaridade do vocabulário (léxico e regras), que não deteta ironia nem metáforas e não distingue o narrador das personagens. Não mede o que o autor sentiu nem o que o leitor sentirá.
- **Frases ambivalentes**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Concordância entre léxicos**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Frases em discurso direto**: Heurística tipográfica: depende das convenções da edição; as falas inseridas a meio de um parágrafo e o discurso indireto livre não são separados.
- **Intensidade emocional**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Diversidade emocional**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Cobertura do léxico de emoções**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Palavras emocionais negadas**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Razão alegria / tristeza**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Alegria**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Tristeza**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Medo**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Raiva**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Aversão**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Surpresa**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Confiança**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
- **Antecipação**: Léxico de associações palavra–emoção: conta palavras, não emoções vividas. Em português e em francês, o léxico é uma tradução automática do inglês (experimental); traduções erradas ou ambíguas e a polissemia afetam os valores. A negação é tratada por uma regra simples (janela de 3 palavras); a ironia não. Léxicos diferentes por língua: compare só obras da mesma língua.
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
- **Facilidade de leitura (Flesch adaptado)**: As adaptações não são equivalentes entre si: não comparar valores de línguas diferentes. A adaptação portuguesa foi calibrada com manuais escolares em português do Brasil e não foi validada para português europeu nem para prosa literária; os níveis escolares são os do sistema brasileiro de 1996. O índice só mede a extensão das frases e das palavras: ignora o vocabulário raro, a sintaxe, a ironia e o conhecimento que o texto pressupõe.
- **Parágrafos de diálogo (estimativa)**: Heurística tipográfica: falha com convenções invulgares e conta citações como diálogo.
- **Pessoas distintas (NER)**: Sobrestimado por variantes do mesmo nome e por erros do reconhecimento de entidades.
- **Densidade lexical**: Depende da etiquetagem morfossintática; os verbos auxiliares não contam como conteúdo.
- **Sentimento médio**: Método de léxico e regras criado para redes sociais, não para literatura; não deteta ironia nem distingue a voz do narrador da das personagens; o léxico português foi criado para português do Brasil e cobre mal a ortografia antiga. Não validado com anotação humana neste projeto. Léxicos diferentes por língua.
- **Frases positivas**: Ver «Sentimento médio».
- **Frases negativas**: Ver «Sentimento médio».
- **Frases neutras**: Uma cobertura baixa do léxico aumenta esta percentagem.
- **Cobertura do léxico de sentimento**: Conta formas exatas (sem lematização), como o próprio VADER.
- **Verbos no passado**: Cada língua divide os tempos de forma diferente (o inglês não tem imperfeito morfológico).
- **Verbos no presente**: Depende do analisador morfológico; o presente histórico e o diálogo contam como presente.
- **Verbos no futuro**: Não aplicável ao inglês (futuro com o auxiliar will). O futuro perifrástico (vou fazer) não conta.
- **Verbos no conjuntivo**: Não aplicável ao inglês (sem conjuntivo morfológico distinto no modelo).
- **Pronomes de 1.ª pessoa**: Nas línguas de sujeito nulo (português) o sujeito fica muitas vezes implícito no verbo.
- **Pronomes de 2.ª pessoa**: As formas de tratamento (você, o senhor) são gramaticalmente de 3.ª pessoa em português.
- **Pronomes de 3.ª pessoa**: Inclui pronomes reflexos e clíticos conforme a anotação do modelo.
- **Expoente de Zipf**: Depende do intervalo de frequências usado no ajuste (só formas com frequência mínima configurável) e da extensão do texto.
- **Ajuste da lei de Zipf (R²)**: Um R² alto em escala log-log não prova uma lei de potência; serve só para descrever o ajuste.
- **Expoente de Heaps (β)**: Depende da extensão do texto e da morfologia da língua (línguas com mais flexão têm β maior).
- **Constante de Heaps (K)**: Muito sensível a β.
- **Ajuste da lei de Heaps (R²)**: Descreve só a qualidade do ajuste.
- **Colocações**: Formas, não lemas; não distingue expressões fixas de repetições de nomes («Carlos da Maia»).
- **Palavras-chave por segmento**: Lemas presentes em todos os segmentos nunca aparecem (idf = 0); depende do número de segmentos.
- **Arco de sentimento**: Herda as limitações do léxico; com poucos segmentos, as oscilações podem dever-se a episódios isolados.
- **Modelos linguísticos**: os modelos spaCy foram treinados com texto contemporâneo; grafias antigas, diálogos e pontuação literária reduzem a exatidão da segmentação, da etiquetagem e da análise sintática.

## 15. Referências metodológicas

- Church, K. W., & Hanks, P. (1990). Word association norms, mutual information, and lexicography. *Computational Linguistics, 16*(1), 22–29. https://aclanthology.org/J90-1003
- Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). *Journal of Quantitative Linguistics, 17*(2), 94–100.
- Deprez, O., & Ek, T. (2021). *vaderSentiment-fr* (Versão 1.3.4) [Software]. PyPI. https://pypi.org/project/vaderSentiment-fr/
- Dunning, T. (1993). Accurate methods for the statistics of surprise and coincidence. *Computational Linguistics, 19*(1), 61–74. https://aclanthology.org/J93-1003
- Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall.
- Flesch, R. (1948). A new readability yardstick. *Journal of Applied Psychology, 32*(3), 221–233. https://doi.org/10.1037/h0057532
- Heaps, H. S. (1978). *Information retrieval: Computational and theoretical aspects*. Academic Press.
- Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1), 216–225. https://doi.org/10.1609/icwsm.v8i1.14550
- Kandel, L., & Moles, A. (1958). Application de l'indice de Flesch à la langue française. *Cahiers d'Études de Radio-Télévision, 19*.
- Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. *Journal of Cognitive Science, 9*(2), 159–191. https://hdl.handle.net/10371/70907
- Martins, T. B. F., Ghiraldelo, C. M., Nunes, M. G. V., & Oliveira Jr., O. N. (1996). *Readability formulas applied to textbooks in Brazilian Portuguese* (Notas do ICMSC-USP, Série Computação, 28). ICMSC-USP.
- McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods, 42*(2), 381–392. https://doi.org/10.3758/BRM.42.2.381
- Mohammad, S. M., & Turney, P. D. (2013). Crowdsourcing a word–emotion association lexicon. *Computational Intelligence, 29*(3), 436–465.
- Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020). Universal Dependencies v2: An evergrowing multilingual treebank collection. In *Proceedings of the 12th Language Resources and Evaluation Conference* (pp. 4034–4043). European Language Resources Association. https://aclanthology.org/2020.lrec-1.497
- Plutchik, R. (1980). *Emotion: A psychoevolutionary synthesis*. Harper & Row.
- Reagan, A. J., Mitchell, L., Kiley, D., Danforth, C. M., & Dodds, P. S. (2016). The emotional arcs of stories are dominated by six basic shapes. *EPJ Data Science, 5*(1). https://doi.org/10.1140/epjds/s13688-016-0093-1
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal, 27*(3), 379–423.
- Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. *Journal of Documentation, 28*(1), 11–21. https://doi.org/10.1108/eb026526
- Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? Measures of lexical richness in perspective. *Computers and the Humanities, 32*(5), 323–352. https://doi.org/10.1023/A:1001749303137
- Ure, J. (1971). Lexical density and register differentiation. In G. E. Perren & J. L. M. Trim (Eds.), *Applications of linguistics* (pp. 443–452). Cambridge University Press.
- Yule, G. U. (1944). *The statistical study of literary vocabulary*. Cambridge University Press.
- Zipf, G. K. (1949). *Human behavior and the principle of least effort*. Addison-Wesley.
- rafjaa. (s.d.). *LeIA: Léxico para Inferência Adaptada* [Software]. GitHub. https://github.com/rafjaa/LeIA
- Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). *spaCy: Industrial-strength natural language processing in Python* [Software]. Zenodo. https://doi.org/10.5281/zenodo.1212303

<sub>Processado em 2026-11-06 15:17 UTC · livros_pln 3.8.1 · código `4fed474e64a6` · commit `3645d4a` · Python 3.12.16 · spaCy 3.8.18 · fr_core_news_md 3.8.0</sub>
