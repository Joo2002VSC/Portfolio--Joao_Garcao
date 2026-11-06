# Indicadores

<!-- Gerado por `python -m livros_pln.documentacao` a partir de livros_pln/catalogo.py. Não editar à mão. -->

Cada indicador tem definição, fórmula, unidade, interpretação, limitações e referências. A coluna «Entre línguas» indica se os valores de livros em línguas diferentes são diretamente comparáveis; quando não são, compare apenas livros da mesma língua.

Notação: *N* = palavras; *V* = formas distintas; *V(i)* = formas que ocorrem *i* vezes; *PF* = palavras por frase; *SP* = sílabas por palavra.

## Estados dos valores

Um valor ausente nunca é substituído por zero. Cada indicador tem um destes estados:

| Estado | Significado |
|---|---|
| válido | Calculado e dentro das condições de aplicação. |
| não aplicável | O indicador não se aplica a este texto (por exemplo, MATTR num texto com menos palavras do que a janela, ou Flesch–Kincaid fora do inglês). O motivo é registado. |
| desconhecido | A informação necessária não está disponível (por exemplo, sem personagens identificadas). |
| falha | O cálculo produziu um valor inválido. |

## Parâmetros por omissão

Alteráveis em `config/parametros.toml`; os valores usados ficam registados em cada `indicadores.json` e no Excel.

| Parâmetro | Valor |
|---|---|
| `janela_mattr` | 500 |
| `limiar_mtld` | 0,72 |
| `minimo_fator_mtld` | 10 |
| `amostra_hdd` | 42 |
| `minimo_mtld` | 100 |
| `minimo_texto` | 1000 |
| `frase_longa` | 30 |
| `segmentos` | 10 |
| `palavras_por_minuto` | 238 |
| `delta_palavras_frequentes` | 150 |
| `delta_minimo_textos` | 3 |
| `rede_minimo_mencoes` | 5 |
| `rede_maximo_personagens` | 40 |
| `sentimento_limiar` | 0,05 |
| `sentimento_minimo_palavras` | 3 |
| `zipf_frequencia_minima` | 5 |
| `colocacao_frequencia_minima` | 5 |
| `palavras_chave_por_segmento` | 5 |

## Dimensão

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Palavras** <br>`palavras` | Tokens alfabéticos (sem pontuação nem números). | — | palavras | Base de normalização de quase todos os indicadores. | Depende da tokenização do spaCy (contrações e hífenes variam entre línguas). | sim | — |
| **Frases** <br>`frases` | Frases segmentadas pelo analisador sintático do spaCy. | — | frases | Base para as médias e distribuições por frase. | A segmentação erra com abreviaturas, diálogos e pontuação pouco convencional. | sim | — |
| **Parágrafos** <br>`paragrafos` | Blocos de texto separados por linha em branco (TXT) ou por elementos de bloco (EPUB). | — | parágrafos | Base para a proporção de diálogo e a extensão dos parágrafos. | Inclui títulos de capítulos. | sim | — |
| **Tempo de leitura estimado** <br>`tempo_leitura_horas` | Palavras ÷ velocidade de leitura. | palavras / (238 × 60) | horas | Ordem de grandeza, não uma previsão individual. | Velocidade de referência de leitura silenciosa de adultos em inglês; varia com a língua, o leitor e o texto. | sim | Brysbaert, M. (2019) |
| **Versos** <br>`versos` | Linhas dos blocos identificados como estrofes. | — | versos | Dimensão do poema. | Deteção automática pela extensão das linhas do ficheiro TXT (não disponível para EPUB); títulos e números de estrofe com 4 ou mais linhas curtas podem ser contados como versos. | sim | — |
| **Estrofes** <br>`estrofes` | Blocos de 4 ou mais linhas curtas, separados por linhas em branco. | — | estrofes | Dimensão do poema. | Deteção automática pela extensão das linhas do ficheiro TXT (não disponível para EPUB); títulos e números de estrofe com 4 ou mais linhas curtas podem ser contados como versos. | sim | — |
| **Versos por estrofe (mediana)** <br>`versos_por_estrofe` | Número de versos da estrofe típica. | — | versos | 8 = oitava (a estrofe de Os Lusíadas); 14 em blocos = soneto; 4 = quadra. | Deteção automática pela extensão das linhas do ficheiro TXT (não disponível para EPUB); títulos e números de estrofe com 4 ou mais linhas curtas podem ser contados como versos. | sim | — |

## Diversidade lexical

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Vocabulário** <br>`vocabulario` | Número de formas distintas (types), em minúsculas. | — | formas | Mais alto = mais formas diferentes. | Cresce com a extensão do texto: não serve para comparar textos de tamanhos diferentes. | não | — |
| **Lemas distintos** <br>`lemas_distintos` | Número de lemas diferentes atribuídos pelo spaCy às palavras. | — | lemas | Aproxima o vocabulário sem as flexões (cantar, cantou e cantava contam uma vez). | Cresce com a extensão do texto e herda os erros de lematização do modelo. | não | Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020) |
| **TTR (type-token ratio)** <br>`ttr` | Formas distintas ÷ palavras. | V / N | 0–1 | Mais alto = vocabulário mais variado, mas só para textos de extensão semelhante. | Diminui sistematicamente com a extensão do texto; não deve ser usado isoladamente para comparar livros de dimensões diferentes. | não | Tweedie, F. J., & Baayen, R. H. (1998) |
| **MATTR** <br>`mattr` | Média do TTR em todas as janelas consecutivas de W palavras (W = 500 por omissão; configurável). | média sobre i de TTR(palavras i … i+W−1) | 0–1 | Mais alto = vocabulário mais variado. Comparável entre textos da mesma língua com pelo menos W palavras e a mesma janela. | Depende da janela escolhida; não aplicável a textos com menos de W palavras. | não | Covington, M. A., & McFall, J. D. (2010) |
| **MTLD** <br>`mtld` | Extensão média (em palavras) dos segmentos sequenciais que mantêm um TTR acima de 0,72; média das passagens no sentido direto e inverso. | N / número de fatores (com fator parcial no fim) | palavras por fator | Mais alto = vocabulário mais variado. É o índice menos dependente da extensão do texto na validação de McCarthy e Jarvis (2010). | Pouco fiável abaixo de cerca de 100 palavras; valores de línguas diferentes não são comparáveis (a morfologia altera o número de formas). | não | McCarthy, P. M., & Jarvis, S. (2010) |
| **HD-D** <br>`hdd` | Contributo médio de cada forma para o TTR esperado numa amostra aleatória de 42 palavras, calculado pela distribuição hipergeométrica. | Σ_formas [1 − P(X = 0)] / 42, X ~ Hipergeométrica(N, f, 42) | 0–1 | Mais alto = vocabulário mais variado. Alternativa probabilística ao vocd-D. | Não aplicável a textos com menos de 42 palavras; não comparável entre línguas. | não | McCarthy, P. M., & Jarvis, S. (2010) |
| **K de Yule** <br>`yule_k` | Concentração do vocabulário a partir do espetro de frequências. | 10⁴ × (Σ_m m²·V(m) − N) / N² | índice (×10⁴) | Mais baixo = vocabulário menos repetitivo. | Relativamente estável com a extensão, mas sensível às palavras muito frequentes. | não | Yule, G. U. (1944); Tweedie, F. J., & Baayen, R. H. (1998) |
| **Hapax legomena** <br>`hapax_pct` | Formas que ocorrem uma única vez, em % do vocabulário. | — | % do vocabulário | Mais alto = mais vocabulário raro ou ocasional. | Depende da extensão do texto e da ortografia (grafias antigas e gralhas contam como formas novas). | não | — |

## Densidade e extensão das palavras

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Densidade lexical** <br>`densidade_lexical_pct` | Palavras de conteúdo (substantivos, verbos plenos, adjetivos, advérbios) em % das palavras. | (NOUN + VERB + ADJ + ADV) / palavras × 100 | % das palavras | Mais alto = texto mais informativo e menos marcado por palavras gramaticais. | Depende da etiquetagem morfossintática; os verbos auxiliares não contam como conteúdo. | não | Ure, J. (1971) |
| **Extensão média das palavras** <br>`palavra_media_letras` | Média de letras por palavra. | — | letras | Mais alto = palavras mais longas, em geral mais raras ou mais derivadas. | Muito dependente da língua. | não | — |

## Extensão das frases

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Extensão média das frases** <br>`frase_media` | Média de palavras por frase. | — | palavras | Medida de extensão, não de complexidade sintática. | Sensível a erros de segmentação e a frases muito longas (assimetria). | sim | — |
| **Extensão mediana das frases** <br>`frase_mediana` | Mediana de palavras por frase. | — | palavras | Metade das frases tem esta extensão ou menos; mais robusta do que a média. | Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática. | sim | — |
| **Percentil 25** <br>`frase_p25` | 25 % das frases têm esta extensão ou menos. | — | palavras | Com o percentil 75, delimita a metade central das frases. | Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática. | sim | — |
| **Percentil 75** <br>`frase_p75` | 75 % das frases têm esta extensão ou menos. | — | palavras | Com o percentil 25, delimita a metade central das frases. | Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática. | sim | — |
| **Desvio-padrão da extensão** <br>`frase_desvio_padrao` | Dispersão da extensão das frases. | — | palavras | Mais alto = alternância maior entre frases curtas e longas. | Sensível a frases extremas (incluindo erros de segmentação); a distribuição é assimétrica, por isso os percentis descrevem-na melhor. | sim | — |
| **Frase mais longa** <br>`frase_maxima` | Extensão máxima de uma frase. | — | palavras | Uma única frase; não descreve o estilo do livro. | Valores muito altos indicam muitas vezes erros de segmentação (listas, versos, texto sem pontuação final). | sim | — |
| **Frases longas** <br>`frases_longas_pct` | Frases com mais de 30 palavras, em % das frases. | — | % das frases | Mais alto = mais frases extensas, que exigem mais memória de trabalho na leitura. | O limiar de 30 palavras é uma convenção (configurável). | sim | — |
| **Extensão média dos parágrafos** <br>`paragrafo_medio` | Média de palavras por parágrafo. | — | palavras | Mais alto = blocos de texto mais extensos (narração contínua). | Depende da paginação da edição (diálogos geram muitos parágrafos curtos). | sim | — |

## Complexidade sintática

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Profundidade sintática** <br>`profundidade_media` | Média, por frase, da profundidade máxima da árvore de dependências (raiz = 0). | média_frases(max_palavras profundidade(palavra)) | níveis | Mais alto = mais encaixamento (subordinação, complementos aninhados). | Depende da qualidade do analisador sintático e das convenções de anotação de cada modelo; correlaciona-se com a extensão das frases. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Distância de dependência média (MDD)** <br>`distancia_dependencia` | Média da distância, em palavras, entre cada palavra e a palavra de que depende (sem pontuação nem raiz). | Σ \|posição(dependente) − posição(cabeça)\| / número de dependências | palavras | Mais alto = dependências mais longas, associadas a maior esforço de processamento. | Depende do analisador e da ordem das palavras de cada língua. | não | Liu, H. (2008) |
| **Orações subordinadas por frase** <br>`subordinadas_por_frase` | Relações de dependência que introduzem orações subordinadas (advcl, ccomp, csubj, acl, acl:relcl / relcl), por frase. | — | orações por frase | Mais alto = mais subordinação. | Estimativa a partir da anotação Universal Dependencies (modelos pt e fr) ou ClearNLP (modelo en); xcomp não conta. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |

## Classes gramaticais

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Substantivos** <br>`pos_noun_por_1000` | Substantivos (etiqueta UPOS NOUN) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Verbos** <br>`pos_verb_por_1000` | Verbos (etiqueta UPOS VERB) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Adjetivos** <br>`pos_adj_por_1000` | Adjetivos (etiqueta UPOS ADJ) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Advérbios** <br>`pos_adv_por_1000` | Advérbios (etiqueta UPOS ADV) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Pronomes** <br>`pos_pron_por_1000` | Pronomes (etiqueta UPOS PRON) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Nomes próprios** <br>`pos_propn_por_1000` | Nomes próprios (etiqueta UPOS PROPN) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Determinantes** <br>`pos_det_por_1000` | Determinantes (etiqueta UPOS DET) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Preposições** <br>`pos_adp_por_1000` | Preposições (etiqueta UPOS ADP) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Conjunções coordenativas** <br>`pos_cconj_por_1000` | Conjunções coordenativas (etiqueta UPOS CCONJ) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Conjunções subordinativas** <br>`pos_sconj_por_1000` | Conjunções subordinativas (etiqueta UPOS SCONJ) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Verbos auxiliares** <br>`pos_aux_por_1000` | Verbos auxiliares (etiqueta UPOS AUX) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Numerais** <br>`pos_num_por_1000` | Numerais (etiqueta UPOS NUM) por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa da classe; comparar só entre livros da mesma língua. | A exatidão da etiquetagem varia entre modelos e é menor em textos antigos. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Pronomes pessoais** <br>`pronomes_pessoais_por_1000` | Pronomes com o traço morfológico PronType=Prs por 1000 palavras. | — | ocorrências por 1000 palavras | Mais alto = narração mais centrada em pessoas e no diálogo. | Depende da anotação morfológica do modelo; as línguas de sujeito nulo (português) usam menos pronomes sujeito. | não | — |
| **Verbos modais** <br>`modais_por_1000` | pt: poder, dever; fr: pouvoir, devoir; en: can, could, may, might, must, shall, should, will, would (etiqueta MD). | — | ocorrências por 1000 palavras | Mais alto = mais expressão de possibilidade, obrigação ou hipótese. | Listas fechadas; não distinguem os valores (epistémico, deôntico) nem usos não modais. | não | — |

## Legibilidade

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Sílabas por palavra** <br>`silabas_por_palavra` | Estimativa por grupos de vogais, com regras para ditongos (pt) e vogais mudas (fr, en). | — | sílabas | Mais alto = palavras mais longas; entra nas fórmulas de legibilidade. | Estimativa heurística; ver a exatidão medida nos testes. | não | — |
| **Facilidade de leitura (Flesch adaptado)** <br>`legibilidade` | Índice de Flesch com os coeficientes da adaptação de cada língua. | en: 206,835 − 1,015·PF − 84,6·SP; fr: 207 − 1,015·PF − 73,6·SP; pt: 248,835 − 1,015·PF − 84,6·SP (PF = palavras/frase, SP = sílabas/palavra) | 0–100 (aprox.) | Mais alto = leitura mais fácil. Faixas em português (Martins et al., 1996): 75–100 muito fácil (1.º–4.º ano de escolaridade), 50–75 fácil (5.º–8.º ano), 25–50 razoavelmente difícil (ensino secundário e superior), abaixo de 25 muito difícil (textos académicos). Em inglês e francês, escala de Flesch (1948): 90 muito fácil, 80 fácil, 70 razoavelmente fácil, 60 padrão, 50 razoavelmente difícil, 30 difícil, abaixo muito difícil. O painel resume em «fácil» (pt ≥ 50; en e fr ≥ 60) ou «difícil». | As adaptações não são equivalentes entre si: não comparar valores de línguas diferentes. A adaptação portuguesa foi calibrada com manuais escolares em português do Brasil e não foi validada para português europeu nem para prosa literária; os níveis escolares são os do sistema brasileiro de 1996. O índice só mede a extensão das frases e das palavras: ignora o vocabulário raro, a sintaxe, a ironia e o conhecimento que o texto pressupõe. | não | Flesch, R. (1948); Kandel, L., & Moles, A. (1958); Martins, T. B. F., Ghiraldelo, C. M., Nunes, M. G. V., & Oliveira Jr., O. N. (1996) |
| **Flesch-Kincaid (nível de escolaridade)** <br>`flesch_kincaid` | Ano de escolaridade norte-americano estimado. Só para inglês. | 0,39·PF + 11,8·SP − 15,59 | ano escolar (EUA) | Mais alto = texto mais exigente. | Calibrado para inglês e para o sistema escolar norte-americano; não aplicável a outras línguas. | não | Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975) |

## Pontuação

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Vírgulas** <br>`virgula_por_1000` | Vírgulas por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Pontos finais** <br>`ponto_por_1000` | Pontos finais por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Pontos e vírgulas** <br>`ponto_e_virgula_por_1000` | Pontos e vírgulas por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Dois pontos** <br>`dois_pontos_por_1000` | Dois pontos por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Pontos de exclamação** <br>`exclamacao_por_1000` | Pontos de exclamação por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Pontos de interrogação** <br>`interrogacao_por_1000` | Pontos de interrogação por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Reticências** <br>`reticencias_por_1000` | Reticências por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Travessões** <br>`travessao_por_1000` | Travessões por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Aspas** <br>`aspas_por_1000` | Aspas por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |
| **Parênteses** <br>`parenteses_por_1000` | Parênteses por 1000 palavras. | — | ocorrências por 1000 palavras | Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua. | As convenções tipográficas variam com a edição e a língua (por exemplo, travessão ou aspas no diálogo). | não | — |

## Discurso e entidades

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Parágrafos de diálogo (estimativa)** <br>`dialogo_pct` | Parágrafos que começam por travessão, aspas ou aspas angulares, ou que contêm uma fala entre aspas. | — | % dos parágrafos | Aproximação do peso do discurso direto. | Heurística tipográfica: falha com convenções invulgares e conta citações como diálogo. | não | — |
| **Pessoas distintas (NER)** <br>`entidades_pessoa` | Nomes distintos reconhecidos como pessoa. | — | nomes | Ordem de grandeza do elenco nomeado. | Sobrestimado por variantes do mesmo nome e por erros do reconhecimento de entidades. | sim | — |
| **Lugares distintos (NER)** <br>`entidades_lugar` | Nomes distintos reconhecidos como lugar. | — | nomes | Ordem de grandeza dos espaços nomeados. | Confusões frequentes entre pessoas e lugares (apelidos que são topónimos). | sim | — |
| **Organizações distintas (NER)** <br>`entidades_organizacao` | Nomes distintos reconhecidos como organização. | — | nomes | Ordem de grandeza das instituições nomeadas. | Categoria com a menor exatidão nos modelos. | sim | — |
| **Menções de entidades** <br>`entidades_por_1000` | Menções a pessoas, lugares e organizações por 1000 palavras. | — | ocorrências por 1000 palavras | Densidade de referências nomeadas. | Depende da exatidão do NER, que varia entre línguas. | não | — |

## Rede de personagens

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Personagens na rede** <br>`personagens_na_rede` | Personagens com menções suficientes e pelo menos uma ligação. | — | personagens | Dimensão do elenco que interage no texto. | Depende do método de identificação (NER ou dicionário). | sim | — |
| **Ligações** <br>`ligacoes_na_rede` | Pares de personagens que aparecem no mesmo parágrafo. | — | ligações | Mais alto = mais pares de personagens partilham parágrafos. | Co-ocorrência textual, não relação narrativa comprovada; depende da lista de personagens e do limiar mínimo de menções. | sim | — |
| **Densidade da rede** <br>`densidade_da_rede` | Ligações existentes ÷ ligações possíveis. | 2L / (n(n − 1)) | 0–1 | Mais alto = elenco mais interligado. | Depende do número de personagens incluídas. | sim | Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008) |

## Tipos de frase

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Frases interrogativas** <br>`frases_interrogativas_pct` | Frases cuja pontuação final é «?». | frases terminadas em ? ÷ frases × 100 | % das frases | Mais alto = mais perguntas, em geral associadas ao diálogo. | Depende da segmentação de frases do modelo e da pontuação da edição. Perguntas indiretas não contam. | sim | — |
| **Frases exclamativas** <br>`frases_exclamativas_pct` | Frases cuja pontuação final é «!». | frases terminadas em ! ÷ frases × 100 | % das frases | Mais alto = mais exclamações, em geral associadas ao diálogo e à expressividade. | Depende da segmentação de frases do modelo e da pontuação da edição. | sim | — |

## Morfologia verbal e pessoa

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Verbos no presente** <br>`verbos_presente_pct` | Formas verbais finitas com o traço Tense=Pres. | — | % das formas verbais finitas com tempo anotado | Mais alto = narração ou diálogo mais ancorados no presente. | Depende do analisador morfológico; o presente histórico e o diálogo contam como presente. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Verbos no passado** <br>`verbos_passado_pct` | Formas verbais finitas no passado (Tense=Past, Imp ou Pqp: pretérito perfeito, imperfeito e mais-que-perfeito). | — | % das formas verbais finitas com tempo anotado | Mais alto = narração no passado, típica do romance. | Cada língua divide os tempos de forma diferente (o inglês não tem imperfeito morfológico). | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Verbos no futuro** <br>`verbos_futuro_pct` | Formas verbais finitas com o traço Tense=Fut. | — | % das formas verbais finitas com tempo anotado | Mais alto = mais projeção, promessa ou hipótese. | Não aplicável ao inglês (futuro com o auxiliar will). O futuro perifrástico (vou fazer) não conta. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Verbos no conjuntivo** <br>`verbos_conjuntivo_pct` | Formas verbais finitas com o traço Mood=Sub. | — | % das formas verbais finitas com modo anotado | Mais alto = mais hipótese, desejo, dúvida ou subordinação. | Não aplicável ao inglês (sem conjuntivo morfológico distinto no modelo). | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Pronomes de 1.ª pessoa** <br>`pronomes_1a_pessoa_por_1000` | Pronomes pessoais com o traço Person=1 (eu, me, nós…) por 1000 palavras. | — | ocorrências por 1000 palavras | Mais alto = narrador na 1.ª pessoa ou muito diálogo. | Nas línguas de sujeito nulo (português) o sujeito fica muitas vezes implícito no verbo. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Pronomes de 2.ª pessoa** <br>`pronomes_2a_pessoa_por_1000` | Pronomes pessoais com o traço Person=2 (tu, te, vós, you…) por 1000 palavras. | — | ocorrências por 1000 palavras | Mais alto = mais interpelação direta, sobretudo no diálogo. | As formas de tratamento (você, o senhor) são gramaticalmente de 3.ª pessoa em português. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Pronomes de 3.ª pessoa** <br>`pronomes_3a_pessoa_por_1000` | Pronomes pessoais com o traço Person=3 (ele, ela, lhe, se…) por 1000 palavras. | — | ocorrências por 1000 palavras | Mais alto = narração centrada em terceiros, típica do narrador heterodiegético. | Inclui pronomes reflexos e clíticos conforme a anotação do modelo. | não | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |

## Leis do vocabulário

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Expoente de Zipf** <br>`zipf_expoente` | Declive (com sinal trocado) da reta ajustada à frequência das formas em função da sua posição, em escala log-log. | f(r) ≈ C · r^−s; s = −declive de log f em log r | adimensional | Próximo de 1 na maior parte dos textos; mais alto = vocabulário mais concentrado nas palavras mais frequentes. | Depende do intervalo de frequências usado no ajuste (só formas com frequência mínima configurável) e da extensão do texto. | não | Zipf, G. K. (1949) |
| **Ajuste da lei de Zipf (R²)** <br>`zipf_r2` | Coeficiente de determinação da reta de Zipf em escala log-log. | — | 0–1 | Mais perto de 1 = a distribuição segue bem uma lei de potência. | Um R² alto em escala log-log não prova uma lei de potência; serve só para descrever o ajuste. | não | Zipf, G. K. (1949) |
| **Expoente de Heaps (β)** <br>`heaps_beta` | Ritmo de crescimento do vocabulário à medida que o texto avança. | V(N) ≈ K · N^β, ajustado em escala log-log | adimensional | Entre 0 e 1; mais alto = o livro continua a introduzir palavras novas. | Depende da extensão do texto e da morfologia da língua (línguas com mais flexão têm β maior). | não | Heaps, H. S. (1978) |
| **Constante de Heaps (K)** <br>`heaps_k` | Fator de escala da lei de Heaps. | V(N) ≈ K · N^β | adimensional | Interpreta-se em conjunto com β; sozinho tem pouco significado. | Muito sensível a β. | não | Heaps, H. S. (1978) |
| **Ajuste da lei de Heaps (R²)** <br>`heaps_r2` | Coeficiente de determinação do ajuste de Heaps. | — | 0–1 | Mais perto de 1 = o crescimento do vocabulário segue bem uma lei de potência. | Descreve só a qualidade do ajuste. | não | Heaps, H. S. (1978) |

## Sentimento

| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | Entre línguas | Referências |
|---|---|---|---|---|---|---|---|
| **Sentimento médio** <br>`sentimento_medio` | Média da pontuação «compound» do VADER nas frases com pelo menos 3 palavras. | média das pontuações compound por frase | −1 a +1 | Acima de 0 = vocabulário globalmente positivo; abaixo de 0 = negativo. Valores entre −0,05 e +0,05 são neutros. | Método de léxico e regras criado para redes sociais, não para literatura; não deteta ironia nem distingue a voz do narrador da das personagens; o léxico português foi criado para português do Brasil e cobre mal a ortografia antiga. Não validado com anotação humana neste projeto. Léxicos diferentes por língua. | não | Hutto, C., & Gilbert, E. (2014); rafjaa. (s.d.); Deprez, O., & Ek, T. (2021) |
| **Frases positivas** <br>`frases_positivas_pct` | Frases com compound ≥ 0,05. | frases com compound ≥ 0,05 ÷ frases pontuadas × 100 | % das frases pontuadas | Proporção de frases com vocabulário predominantemente positivo. | Ver «Sentimento médio». | não | Hutto, C., & Gilbert, E. (2014) |
| **Frases negativas** <br>`frases_negativas_pct` | Frases com compound ≤ −0,05. | frases com compound ≤ −0,05 ÷ frases pontuadas × 100 | % das frases pontuadas | Proporção de frases com vocabulário predominantemente negativo. | Ver «Sentimento médio». | não | Hutto, C., & Gilbert, E. (2014) |
| **Frases neutras** <br>`frases_neutras_pct` | Frases com compound entre −0,05 e 0,05. | — | % das frases pontuadas | Inclui frases sem nenhuma palavra do léxico. | Uma cobertura baixa do léxico aumenta esta percentagem. | não | Hutto, C., & Gilbert, E. (2014) |
| **Cobertura do léxico de sentimento** <br>`cobertura_lexico_pct` | Palavras do texto que existem no léxico de sentimento usado. | — | % das palavras | Indicador de qualidade: abaixo de ~5 %, o sentimento assenta em muito poucas palavras. | Conta formas exatas (sem lematização), como o próprio VADER. | não | — |

## Métodos com tabelas e gráficos

Métodos cujo resultado é uma tabela ou um gráfico, e não um único valor.

| Método | Definição | Fórmula | Interpretação | Limitações | Referências |
|---|---|---|---|---|---|
| **Arco de sentimento** | Sentimento médio e proporção de frases positivas e negativas em cada segmento do livro (segmentos com o mesmo número de palavras). | — | Mostra como a polaridade do vocabulário sobe e desce ao longo da narrativa. | Herda as limitações do léxico; com poucos segmentos, as oscilações podem dever-se a episódios isolados. | Reagan, A. J., Mitchell, L., Kiley, D., Danforth, C. M., & Dodds, P. S. (2016); Hutto, C., & Gilbert, E. (2014) |
| **Colocações** | Pares de palavras contíguas na mesma frase que ocorrem juntas muito mais do que o acaso faria prever; excluem-se os pares formados só por palavras gramaticais. | G² = 2 Σ O·ln(O/E) na tabela de contingência 2×2; PMI = log2(O11 ÷ E11) | G² alto = associação estatisticamente forte; PMI alto = associação exclusiva (mas instável em pares raros). | Formas, não lemas; não distingue expressões fixas de repetições de nomes («Carlos da Maia»). | Dunning, T. (1993); Church, K. W., & Hanks, P. (1990) |
| **Palavras-chave por segmento** | Lemas de conteúdo mais característicos de cada segmento, por comparação com os outros segmentos do mesmo livro. | tf × log(segmentos ÷ segmentos que contêm o lema) | Sugere os temas, lugares e personagens que dominam cada parte do livro. | Lemas presentes em todos os segmentos nunca aparecem (idf = 0); depende do número de segmentos. | Spärck Jones, K. (1972) |
| **Tempos e modos verbais** | Distribuição das formas verbais finitas por tempo e modo. | — | Ajuda a caracterizar a narração (passado) e o diálogo (presente, conjuntivo). | Traços morfológicos atribuídos automaticamente pelo spaCy. | Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020) |
| **Curvas de Zipf e de Heaps** | Frequência em função da posição (Zipf) e crescimento do vocabulário com a extensão do texto (Heaps), em escala log-log. | — | Leis empíricas observadas em quase todos os textos; os desvios dizem algo sobre o estilo e a língua. | Ver os indicadores do grupo. | Zipf, G. K. (1949); Heaps, H. S. (1978) |

## Exatidão da estimativa de sílabas

As fórmulas de legibilidade dependem do número de sílabas, estimado por regras ortográficas (grupos de vogais, ditongos e hiatos em português, «e» mudo em francês e inglês). A exatidão foi medida em listas anotadas à mão (`tests/silabas_anotadas.json`). As listas de **afinação** foram usadas para desenvolver as regras, pelo que sobrestimam a exatidão; as de **validação** foram escritas depois e não serviram para as ajustar. O viés é a diferença relativa entre o total de sílabas estimado e o anotado.

| Língua | Lista | Palavras certas | Viés no total | Erros |
|---|---|---|---|---|
| português | afinação | 34/35 | -1,1 % | juiz (1 em vez de 2) |
| francês | afinação | 28/30 | +0,0 % | voyage (1 em vez de 2), musique (3 em vez de 2) |
| inglês | afinação | 28/30 | +0,0 % | created (2 em vez de 3), everything (4 em vez de 3) |
| português | validação | 18/20 | -3,6 % | proibido (3 em vez de 4), cair (1 em vez de 2) |
| francês | validação | 17/20 | -7,5 % | oublier (2 em vez de 3), poésie (2 em vez de 3), nuage (1 em vez de 2) |
| inglês | validação | 16/20 | +6,7 % | sometimes (4 em vez de 2), quiet (1 em vez de 2), careful (3 em vez de 2), smile (2 em vez de 1) |

As listas são pequenas (20 a 35 palavras): estes valores indicam a ordem de grandeza do erro, não uma avaliação definitiva. Os erros em palavras isoladas compensam-se parcialmente no total de um livro, mas o viés sistemático afeta diretamente o índice de legibilidade (cada 0,01 sílabas por palavra altera o índice de Flesch em cerca de 0,85 pontos).

## Referências

- Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment, 2008*(10), P10008. https://doi.org/10.1088/1742-5468/2008/10/P10008
- Brysbaert, M. (2019). How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language, 109*, 104047. https://doi.org/10.1016/j.jml.2019.104047
- Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide to likely authorship. *Literary and Linguistic Computing, 17*(3), 267–287. https://doi.org/10.1093/llc/17.3.267
- Church, K. W., & Hanks, P. (1990). Word association norms, mutual information, and lexicography. *Computational Linguistics, 16*(1), 22–29. https://aclanthology.org/J90-1003
- Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). *Journal of Quantitative Linguistics, 17*(2), 94–100.
- Deprez, O., & Ek, T. (2021). *vaderSentiment-fr* (Versão 1.3.4) [Software]. PyPI. https://pypi.org/project/vaderSentiment-fr/
- Dunning, T. (1993). Accurate methods for the statistics of surprise and coincidence. *Computational Linguistics, 19*(1), 61–74. https://aclanthology.org/J93-1003
- Evert, S., Proisl, T., Jannidis, F., Reger, I., Pielström, S., Schöch, C., & Vitt, T. (2017). Understanding and explaining Delta measures for authorship attribution. *Digital Scholarship in the Humanities, 32*(suppl. 2), ii4–ii16. https://doi.org/10.1093/llc/fqx023
- Flesch, R. (1948). A new readability yardstick. *Journal of Applied Psychology, 32*(3), 221–233. https://doi.org/10.1037/h0057532
- Heaps, H. S. (1978). *Information retrieval: Computational and theoretical aspects*. Academic Press.
- Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). *spaCy: Industrial-strength natural language processing in Python* [Software]. Zenodo. https://doi.org/10.5281/zenodo.1212303
- Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1), 216–225. https://doi.org/10.1609/icwsm.v8i1.14550
- Kandel, L., & Moles, A. (1958). Application de l'indice de Flesch à la langue française. *Cahiers d'Études de Radio-Télévision, 19*.
- Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). *Derivation of new readability formulas (Automated Readability Index, Fog Count and Flesch Reading Ease Formula) for Navy enlisted personnel* (Research Branch Report 8-75). Naval Technical Training Command.
- Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. *Journal of Cognitive Science, 9*(2), 159–191. https://hdl.handle.net/10371/70907
- Martins, T. B. F., Ghiraldelo, C. M., Nunes, M. G. V., & Oliveira Jr., O. N. (1996). *Readability formulas applied to textbooks in Brazilian Portuguese* (Notas do ICMSC-USP, Série Computação, 28). ICMSC-USP.
- McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods, 42*(2), 381–392. https://doi.org/10.3758/BRM.42.2.381
- Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020). Universal Dependencies v2: An evergrowing multilingual treebank collection. In *Proceedings of the 12th Language Resources and Evaluation Conference* (pp. 4034–4043). European Language Resources Association. https://aclanthology.org/2020.lrec-1.497
- Reagan, A. J., Mitchell, L., Kiley, D., Danforth, C. M., & Dodds, P. S. (2016). The emotional arcs of stories are dominated by six basic shapes. *EPJ Data Science, 5*(1). https://doi.org/10.1140/epjds/s13688-016-0093-1
- Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. *Journal of Documentation, 28*(1), 11–21. https://doi.org/10.1108/eb026526
- Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? Measures of lexical richness in perspective. *Computers and the Humanities, 32*(5), 323–352. https://doi.org/10.1023/A:1001749303137
- Ure, J. (1971). Lexical density and register differentiation. In G. E. Perren & J. L. M. Trim (Eds.), *Applications of linguistics* (pp. 443–452). Cambridge University Press.
- Yule, G. U. (1944). *The statistical study of literary vocabulary*. Cambridge University Press.
- Zipf, G. K. (1949). *Human behavior and the principle of least effort*. Addison-Wesley.
- rafjaa. (s.d.). *LeIA: Léxico para Inferência Adaptada* [Software]. GitHub. https://github.com/rafjaa/LeIA
