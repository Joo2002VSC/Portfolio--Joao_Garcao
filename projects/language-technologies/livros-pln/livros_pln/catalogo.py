"""Catálogo dos indicadores: definição, fórmula, unidade, interpretação, limitações e referências.

É a fonte única usada pelos relatórios, pela exportação para Excel e pela documentação
(docs/indicadores.md é gerado a partir daqui). As referências seguem a norma APA 7.
"""
from __future__ import annotations

from dataclasses import dataclass, field

REFERENCIAS = {
    "brysbaert2019": "Brysbaert, M. (2019). How many words do we read per minute? A review and meta-analysis of reading "
                     "rate. *Journal of Memory and Language, 109*, 104047. https://doi.org/10.1016/j.jml.2019.104047",
    "burrows2002": "Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide to likely authorship. "
                   "*Literary and Linguistic Computing, 17*(3), 267–287. https://doi.org/10.1093/llc/17.3.267",
    "blondel2008": "Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities "
                   "in large networks. *Journal of Statistical Mechanics: Theory and Experiment, 2008*(10), P10008. "
                   "https://doi.org/10.1088/1742-5468/2008/10/P10008",
    "covington2010": "Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token "
                     "ratio (MATTR). *Journal of Quantitative Linguistics, 17*(2), 94–100.",
    "evert2017": "Evert, S., Proisl, T., Jannidis, F., Reger, I., Pielström, S., Schöch, C., & Vitt, T. (2017). "
                 "Understanding and explaining Delta measures for authorship attribution. *Digital Scholarship in the "
                 "Humanities, 32*(suppl. 2), ii4–ii16. https://doi.org/10.1093/llc/fqx023",
    "flesch1948": "Flesch, R. (1948). A new readability yardstick. *Journal of Applied Psychology, 32*(3), 221–233. "
                  "https://doi.org/10.1037/h0057532",
    "kandel1958": "Kandel, L., & Moles, A. (1958). Application de l'indice de Flesch à la langue française. *Cahiers "
                  "d'Études de Radio-Télévision, 19*.",
    "kincaid1975": "Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). *Derivation of new "
                   "readability formulas (Automated Readability Index, Fog Count and Flesch Reading Ease Formula) for "
                   "Navy enlisted personnel* (Research Branch Report 8-75). Naval Technical Training Command.",
    "liu2008": "Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. *Journal of "
               "Cognitive Science, 9*(2), 159–191. https://hdl.handle.net/10371/70907",
    "martins1996": "Martins, T. B. F., Ghiraldelo, C. M., Nunes, M. G. V., & Oliveira Jr., O. N. (1996). *Readability "
                   "formulas applied to textbooks in Brazilian Portuguese* (Notas do ICMSC-USP, Série Computação, 28). "
                   "ICMSC-USP.",
    "mccarthy2010": "McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated "
                    "approaches to lexical diversity assessment. *Behavior Research Methods, 42*(2), 381–392. "
                    "https://doi.org/10.3758/BRM.42.2.381",
    "tweedie1998": "Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? Measures of lexical richness "
                   "in perspective. *Computers and the Humanities, 32*(5), 323–352. "
                   "https://doi.org/10.1023/A:1001749303137",
    "ure1971": "Ure, J. (1971). Lexical density and register differentiation. In G. E. Perren & J. L. M. Trim (Eds.), "
               "*Applications of linguistics* (pp. 443–452). Cambridge University Press.",
    "yule1944": "Yule, G. U. (1944). *The statistical study of literary vocabulary*. Cambridge University Press.",
    "honnibal2020": "Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). *spaCy: Industrial-strength "
                    "natural language processing in Python* [Software]. Zenodo. https://doi.org/10.5281/zenodo.1212303",
    "nivre2020": "Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., "
                 "Tyers, F., & Zeman, D. (2020). Universal Dependencies v2: An evergrowing multilingual treebank "
                 "collection. In *Proceedings of the 12th Language Resources and Evaluation Conference* (pp. 4034–4043). "
                 "European Language Resources Association. https://aclanthology.org/2020.lrec-1.497",
}


@dataclass(frozen=True)
class Indicador:
    nome: str
    grupo: str
    definicao: str
    unidade: str
    interpretacao: str
    limitacoes: str = ""
    formula: str = ""
    referencias: tuple[str, ...] = ()
    casas: int = 1
    entre_linguas: bool = True   # se valores de línguas diferentes são diretamente comparáveis


GRUPOS = ["Dimensão", "Diversidade lexical", "Densidade e extensão das palavras", "Extensão das frases",
          "Complexidade sintática", "Classes gramaticais", "Legibilidade", "Pontuação", "Discurso e entidades",
          "Rede de personagens"]

_D = "Dimensão"
_L = "Diversidade lexical"
_W = "Densidade e extensão das palavras"
_F = "Extensão das frases"
_S = "Complexidade sintática"
_P = "Classes gramaticais"
_R = "Legibilidade"
_U = "Pontuação"
_E = "Discurso e entidades"
_N = "Rede de personagens"

POR_1000 = "ocorrências por 1000 palavras"

INDICADORES: dict[str, Indicador] = {
    # --- Dimensão -----------------------------------------------------------------------------------------------
    "palavras": Indicador("Palavras", _D, "Tokens alfabéticos (sem pontuação nem números).", "palavras",
                          "Base de normalização de quase todos os indicadores.",
                          "Depende da tokenização do spaCy (contrações e hífenes variam entre línguas).", casas=0),
    "frases": Indicador("Frases", _D, "Frases segmentadas pelo analisador sintático do spaCy.", "frases",
                        "Base para as médias e distribuições por frase.", "A segmentação erra com abreviaturas, diálogos e pontuação pouco convencional.", casas=0),
    "paragrafos": Indicador("Parágrafos", _D, "Blocos de texto separados por linha em branco (TXT) ou por elementos de "
                            "bloco (EPUB).", "parágrafos", "Base para a proporção de diálogo e a extensão dos parágrafos.", "Inclui títulos de capítulos.", casas=0),
    "tempo_leitura_horas": Indicador("Tempo de leitura estimado", _D, "Palavras ÷ velocidade de leitura.", "horas",
                                     "Ordem de grandeza, não uma previsão individual.",
                                     "Velocidade de referência de leitura silenciosa de adultos em inglês; varia com a "
                                     "língua, o leitor e o texto.", "palavras / (238 × 60)", ("brysbaert2019",)),

    # --- Diversidade lexical ------------------------------------------------------------------------------------
    "vocabulario": Indicador("Vocabulário", _L, "Número de formas distintas (types), em minúsculas.", "formas",
                             "Mais alto = mais formas diferentes.",
                             "Cresce com a extensão do texto: não serve para comparar textos de tamanhos diferentes.",
                             casas=0, entre_linguas=False),
    "lemas_distintos": Indicador("Lemas distintos", _L, "Número de lemas diferentes atribuídos pelo spaCy às palavras.",
                                 "lemas", "Aproxima o vocabulário sem as flexões (cantar, cantou e cantava contam uma vez).",
                                 "Cresce com a extensão do texto e herda os erros de lematização do modelo.",
                                 referencias=("honnibal2020",), casas=0, entre_linguas=False),
    "ttr": Indicador("TTR (type-token ratio)", _L, "Formas distintas ÷ palavras.", "0–1",
                     "Mais alto = vocabulário mais variado, mas só para textos de extensão semelhante.",
                     "Diminui sistematicamente com a extensão do texto; não deve ser usado isoladamente para comparar "
                     "livros de dimensões diferentes.", "V / N", ("tweedie1998",), 3, False),
    "mattr": Indicador("MATTR", _L, "Média do TTR em todas as janelas consecutivas de W palavras (W = 500 por "
                       "omissão; configurável).", "0–1",
                       "Mais alto = vocabulário mais variado. Comparável entre textos da mesma língua com pelo menos W "
                       "palavras e a mesma janela.",
                       "Depende da janela escolhida; não aplicável a textos com menos de W palavras.",
                       "média sobre i de TTR(palavras i … i+W−1)", ("covington2010",), 3, False),
    "mtld": Indicador("MTLD", _L, "Extensão média (em palavras) dos segmentos sequenciais que mantêm um TTR acima de "
                      "0,72; média das passagens no sentido direto e inverso.", "palavras por fator",
                      "Mais alto = vocabulário mais variado. É o índice menos dependente da extensão do texto na "
                      "validação de McCarthy e Jarvis (2010).",
                      "Pouco fiável abaixo de cerca de 100 palavras; valores de línguas diferentes não são comparáveis "
                      "(a morfologia altera o número de formas).", "N / número de fatores (com fator parcial no fim)",
                      ("mccarthy2010",), 1, False),
    "hdd": Indicador("HD-D", _L, "Contributo médio de cada forma para o TTR esperado numa amostra aleatória de 42 "
                     "palavras, calculado pela distribuição hipergeométrica.", "0–1",
                     "Mais alto = vocabulário mais variado. Alternativa probabilística ao vocd-D.",
                     "Não aplicável a textos com menos de 42 palavras; não comparável entre línguas.",
                     "Σ_formas [1 − P(X = 0)] / 42, X ~ Hipergeométrica(N, f, 42)", ("mccarthy2010",), 3, False),
    "yule_k": Indicador("K de Yule", _L, "Concentração do vocabulário a partir do espetro de frequências.",
                        "índice (×10⁴)", "Mais baixo = vocabulário menos repetitivo.",
                        "Relativamente estável com a extensão, mas sensível às palavras muito frequentes.",
                        "10⁴ × (Σ_m m²·V(m) − N) / N²", ("yule1944", "tweedie1998"), 1, False),
    "hapax_pct": Indicador("Hapax legomena", _L, "Formas que ocorrem uma única vez, em % do vocabulário.",
                           "% do vocabulário", "Mais alto = mais vocabulário raro ou ocasional.",
                           "Depende da extensão do texto e da ortografia (grafias antigas e gralhas contam como formas "
                           "novas).", casas=1, entre_linguas=False),

    # --- Densidade e palavras -----------------------------------------------------------------------------------
    "densidade_lexical_pct": Indicador("Densidade lexical", _W, "Palavras de conteúdo (substantivos, verbos plenos, "
                                       "adjetivos, advérbios) em % das palavras.", "% das palavras",
                                       "Mais alto = texto mais informativo e menos marcado por palavras gramaticais.",
                                       "Depende da etiquetagem morfossintática; os verbos auxiliares não contam como "
                                       "conteúdo.", "(NOUN + VERB + ADJ + ADV) / palavras × 100", ("ure1971",), 1, False),
    "palavra_media_letras": Indicador("Extensão média das palavras", _W, "Média de letras por palavra.", "letras",
                                      "Mais alto = palavras mais longas, em geral mais raras ou mais derivadas.", "Muito dependente da língua.", casas=2, entre_linguas=False),

    # --- Frases -------------------------------------------------------------------------------------------------
    "frase_media": Indicador("Extensão média das frases", _F, "Média de palavras por frase.", "palavras",
                             "Medida de extensão, não de complexidade sintática.",
                             "Sensível a erros de segmentação e a frases muito longas (assimetria).", casas=1),
    "frase_mediana": Indicador("Extensão mediana das frases", _F, "Mediana de palavras por frase.", "palavras",
                               "Metade das frases tem esta extensão ou menos; mais robusta do que a média.",
                               "Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática.", casas=0),
    "frase_p25": Indicador("Percentil 25", _F, "25 % das frases têm esta extensão ou menos.", "palavras",
                           "Com o percentil 75, delimita a metade central das frases.", "Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática.", casas=0),
    "frase_p75": Indicador("Percentil 75", _F, "75 % das frases têm esta extensão ou menos.", "palavras",
                           "Com o percentil 25, delimita a metade central das frases.", "Depende da segmentação de frases do modelo spaCy e da pontuação da edição; extensão não é complexidade sintática.", casas=0),
    "frase_desvio_padrao": Indicador("Desvio-padrão da extensão", _F, "Dispersão da extensão das frases.", "palavras",
                                     "Mais alto = alternância maior entre frases curtas e longas.",
                                     "Sensível a frases extremas (incluindo erros de segmentação); a distribuição é "
                                     "assimétrica, por isso os percentis descrevem-na melhor.", casas=1),
    "frase_maxima": Indicador("Frase mais longa", _F, "Extensão máxima de uma frase.", "palavras",
                              "Uma única frase; não descreve o estilo do livro.",
                              "Valores muito altos indicam muitas vezes erros de segmentação (listas, versos, texto sem "
                              "pontuação final).", casas=0),
    "frases_longas_pct": Indicador("Frases longas", _F, "Frases com mais de 30 palavras, em % das frases.",
                                   "% das frases", "Mais alto = mais frases extensas, que exigem mais memória de trabalho na leitura.", "O limiar de 30 palavras é uma convenção (configurável).", casas=1),
    "paragrafo_medio": Indicador("Extensão média dos parágrafos", _F, "Média de palavras por parágrafo.", "palavras",
                                 "Mais alto = blocos de texto mais extensos (narração contínua).", "Depende da paginação da edição (diálogos geram muitos parágrafos curtos).", casas=1),

    # --- Sintaxe ------------------------------------------------------------------------------------------------
    "profundidade_media": Indicador("Profundidade sintática", _S, "Média, por frase, da profundidade máxima da árvore "
                                    "de dependências (raiz = 0).", "níveis",
                                    "Mais alto = mais encaixamento (subordinação, complementos aninhados).",
                                    "Depende da qualidade do analisador sintático e das convenções de anotação de "
                                    "cada modelo; correlaciona-se com a extensão das frases.",
                                    "média_frases(max_palavras profundidade(palavra))", ("nivre2020",), 2, False),
    "distancia_dependencia": Indicador("Distância de dependência média (MDD)", _S, "Média da distância, em palavras, "
                                       "entre cada palavra e a palavra de que depende (sem pontuação nem raiz).",
                                       "palavras", "Mais alto = dependências mais longas, associadas a maior esforço "
                                       "de processamento.", "Depende do analisador e da ordem das palavras de cada "
                                       "língua.", "Σ |posição(dependente) − posição(cabeça)| / número de dependências",
                                       ("liu2008",), 2, False),
    "subordinadas_por_frase": Indicador("Orações subordinadas por frase", _S, "Relações de dependência que introduzem "
                                        "orações subordinadas (advcl, ccomp, csubj, acl, acl:relcl / relcl), por frase.",
                                        "orações por frase", "Mais alto = mais subordinação.",
                                        "Estimativa a partir da anotação Universal Dependencies (modelos pt e fr) ou "
                                        "ClearNLP (modelo en); xcomp não conta.", referencias=("nivre2020",), casas=2,
                                        entre_linguas=False),

    # --- Legibilidade -------------------------------------------------------------------------------------------
    "silabas_por_palavra": Indicador("Sílabas por palavra", _R, "Estimativa por grupos de vogais, com regras para "
                                     "ditongos (pt) e vogais mudas (fr, en).", "sílabas", "Mais alto = palavras mais longas; entra nas fórmulas de legibilidade.",
                                     "Estimativa heurística; ver a exatidão medida nos testes.", casas=2,
                                     entre_linguas=False),
    "legibilidade": Indicador("Facilidade de leitura (Flesch adaptado)", _R, "Índice de Flesch com os coeficientes da "
                              "adaptação de cada língua.", "0–100 (aprox.)", "Mais alto = leitura mais fácil.",
                              "As adaptações não são equivalentes entre si: não comparar valores de línguas diferentes. "
                              "A adaptação portuguesa foi calibrada com manuais escolares em português do Brasil e não "
                              "foi validada para português europeu nem para prosa literária.",
                              "en: 206,835 − 1,015·PF − 84,6·SP; fr: 207 − 1,015·PF − 73,6·SP; "
                              "pt: 248,835 − 1,015·PF − 84,6·SP (PF = palavras/frase, SP = sílabas/palavra)",
                              ("flesch1948", "kandel1958", "martins1996"), 1, False),
    "flesch_kincaid": Indicador("Flesch-Kincaid (nível de escolaridade)", _R, "Ano de escolaridade norte-americano "
                                "estimado. Só para inglês.", "ano escolar (EUA)", "Mais alto = texto mais exigente.",
                                "Calibrado para inglês e para o sistema escolar norte-americano; não aplicável a "
                                "outras línguas.", "0,39·PF + 11,8·SP − 15,59", ("kincaid1975",), 1, False),

    # --- Pontuação ----------------------------------------------------------------------------------------------
    **{f"{k}_por_1000": Indicador(n, _U, f"{n} por 1000 palavras.", POR_1000,
                                  "Frequência relativa do sinal; compara o ritmo da pontuação entre livros da mesma língua.",
                                  "As convenções tipográficas variam com a edição e a língua (por exemplo, travessão "
                                  "ou aspas no diálogo).", casas=1, entre_linguas=False)
       for k, n in [("virgula", "Vírgulas"), ("ponto", "Pontos finais"), ("ponto_e_virgula", "Pontos e vírgulas"),
                    ("dois_pontos", "Dois pontos"), ("exclamacao", "Pontos de exclamação"),
                    ("interrogacao", "Pontos de interrogação"), ("reticencias", "Reticências"),
                    ("travessao", "Travessões"), ("aspas", "Aspas"), ("parenteses", "Parênteses")]},

    # --- Discurso e entidades -----------------------------------------------------------------------------------
    "dialogo_pct": Indicador("Parágrafos de diálogo (estimativa)", _E, "Parágrafos que começam por travessão, aspas ou "
                             "aspas angulares, ou que contêm uma fala entre aspas.", "% dos parágrafos",
                             "Aproximação do peso do discurso direto.",
                             "Heurística tipográfica: falha com convenções invulgares e conta citações como diálogo.",
                             casas=1, entre_linguas=False),
    "entidades_pessoa": Indicador("Pessoas distintas (NER)", _E, "Nomes distintos reconhecidos como pessoa.", "nomes",
                                  "Ordem de grandeza do elenco nomeado.", "Sobrestimado por variantes do mesmo nome e "
                                  "por erros do reconhecimento de entidades.", casas=0),
    "entidades_lugar": Indicador("Lugares distintos (NER)", _E, "Nomes distintos reconhecidos como lugar.", "nomes",
                                 "Ordem de grandeza dos espaços nomeados.", "Confusões frequentes entre pessoas e lugares (apelidos que são topónimos).", casas=0),
    "entidades_organizacao": Indicador("Organizações distintas (NER)", _E, "Nomes distintos reconhecidos como "
                                       "organização.", "nomes", "Ordem de grandeza das instituições nomeadas.", "Categoria com a menor exatidão nos modelos.", casas=0),
    "entidades_por_1000": Indicador("Menções de entidades", _E, "Menções a pessoas, lugares e organizações por 1000 "
                                    "palavras.", POR_1000, "Densidade de referências nomeadas.",
                                    "Depende da exatidão do NER, que varia entre línguas.", casas=1, entre_linguas=False),

    # --- Rede ---------------------------------------------------------------------------------------------------
    "personagens_na_rede": Indicador("Personagens na rede", _N, "Personagens com menções suficientes e pelo menos uma "
                                     "ligação.", "personagens", "Dimensão do elenco que interage no texto.", "Depende do método de identificação (NER ou "
                                     "dicionário).", casas=0),
    "ligacoes_na_rede": Indicador("Ligações", _N, "Pares de personagens que aparecem no mesmo parágrafo.", "ligações",
                                  "Mais alto = mais pares de personagens partilham parágrafos.",
                                  "Co-ocorrência textual, não relação narrativa comprovada; depende da lista de "
                                  "personagens e do limiar mínimo de menções.", casas=0),
    "densidade_da_rede": Indicador("Densidade da rede", _N, "Ligações existentes ÷ ligações possíveis.", "0–1",
                                   "Mais alto = elenco mais interligado.", "Depende do número de personagens incluídas.",
                                   "2L / (n(n − 1))", ("blondel2008",), 3),
}

CLASSES = ["NOUN", "VERB", "ADJ", "ADV", "PRON", "PROPN", "DET", "ADP", "CCONJ", "SCONJ", "AUX", "NUM"]
NOMES_CLASSES = {"NOUN": "Substantivos", "VERB": "Verbos", "ADJ": "Adjetivos", "ADV": "Advérbios",
                 "PRON": "Pronomes", "PROPN": "Nomes próprios", "DET": "Determinantes", "ADP": "Preposições",
                 "CCONJ": "Conjunções coordenativas", "SCONJ": "Conjunções subordinativas", "AUX": "Verbos auxiliares",
                 "NUM": "Numerais"}
for _c in CLASSES:
    INDICADORES[f"pos_{_c.lower()}_por_1000"] = Indicador(
        NOMES_CLASSES[_c], _P, f"{NOMES_CLASSES[_c]} (etiqueta UPOS {_c}) por 1000 palavras.", POR_1000,
        "Frequência relativa da classe; comparar só entre livros da mesma língua.",
        "A exatidão da etiquetagem varia entre modelos e é menor em textos antigos.", referencias=("nivre2020",),
        casas=1, entre_linguas=False)
INDICADORES["pronomes_pessoais_por_1000"] = Indicador(
    "Pronomes pessoais", _P, "Pronomes com o traço morfológico PronType=Prs por 1000 palavras.", POR_1000,
    "Mais alto = narração mais centrada em pessoas e no diálogo.", "Depende da anotação morfológica do modelo; as "
    "línguas de sujeito nulo (português) usam menos pronomes sujeito.", casas=1, entre_linguas=False)
INDICADORES["modais_por_1000"] = Indicador(
    "Verbos modais", _P, "pt: poder, dever; fr: pouvoir, devoir; en: can, could, may, might, must, shall, should, will, "
    "would (etiqueta MD).", POR_1000, "Mais alto = mais expressão de possibilidade, obrigação ou hipótese.",
    "Listas fechadas; não distinguem os valores (epistémico, deôntico) nem usos não modais.", casas=1,
    entre_linguas=False)


def referencias_de(chaves) -> list[str]:
    usadas = []
    for k in chaves:
        for r in INDICADORES[k].referencias if k in INDICADORES else ():
            if r not in usadas:
                usadas.append(r)
    return [REFERENCIAS[r] for r in sorted(usadas, key=lambda r: REFERENCIAS[r])]


def por_grupo() -> dict[str, list[str]]:
    grupos = {g: [] for g in GRUPOS}
    for k, ind in INDICADORES.items():
        grupos[ind.grupo].append(k)
    return grupos
