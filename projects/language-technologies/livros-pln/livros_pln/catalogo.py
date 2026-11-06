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
    "church1990": "Church, K. W., & Hanks, P. (1990). Word association norms, mutual information, and lexicography. "
                  "*Computational Linguistics, 16*(1), 22–29. https://aclanthology.org/J90-1003",
    "deprez2021": "Deprez, O., & Ek, T. (2021). *vaderSentiment-fr* (Versão 1.3.4) [Software]. PyPI. "
                  "https://pypi.org/project/vaderSentiment-fr/",
    "dunning1993": "Dunning, T. (1993). Accurate methods for the statistics of surprise and coincidence. *Computational "
                   "Linguistics, 19*(1), 61–74. https://aclanthology.org/J93-1003",
    "heaps1978": "Heaps, H. S. (1978). *Information retrieval: Computational and theoretical aspects*. Academic Press.",
    "hutto2014": "Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of "
                 "social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1), "
                 "216–225. https://doi.org/10.1609/icwsm.v8i1.14550",
    "leia": "rafjaa. (s.d.). *LeIA: Léxico para Inferência Adaptada* [Software]. GitHub. https://github.com/rafjaa/LeIA",
    "reagan2016": "Reagan, A. J., Mitchell, L., Kiley, D., Danforth, C. M., & Dodds, P. S. (2016). The emotional arcs of "
                  "stories are dominated by six basic shapes. *EPJ Data Science, 5*(1). "
                  "https://doi.org/10.1140/epjds/s13688-016-0093-1",
    "sparckjones1972": "Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application "
                       "in retrieval. *Journal of Documentation, 28*(1), 11–21. https://doi.org/10.1108/eb026526",
    "zipf1949": "Zipf, G. K. (1949). *Human behavior and the principle of least effort*. Addison-Wesley.",
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
          "Rede de personagens", "Tipos de frase", "Morfologia verbal e pessoa", "Leis do vocabulário",
          "Sentimento"]

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
_T = "Tipos de frase"
_M = "Morfologia verbal e pessoa"
_Z = "Leis do vocabulário"
_SE = "Sentimento"

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
                              "adaptação de cada língua.", "0–100 (aprox.)",
                              "Mais alto = leitura mais fácil. Faixas em português (Martins et al., 1996): 75–100 muito "
                              "fácil (1.º–4.º ano de escolaridade), 50–75 fácil (5.º–8.º ano), 25–50 razoavelmente "
                              "difícil (ensino secundário e superior), abaixo de 25 muito difícil (textos académicos). "
                              "Em inglês e francês, escala de Flesch (1948): 90 muito fácil, 80 fácil, 70 razoavelmente "
                              "fácil, 60 padrão, 50 razoavelmente difícil, 30 difícil, abaixo muito difícil. O painel "
                              "resume em «fácil» (pt ≥ 50; en e fr ≥ 60) ou «difícil».",
                              "As adaptações não são equivalentes entre si: não comparar valores de línguas diferentes. "
                              "A adaptação portuguesa foi calibrada com manuais escolares em português do Brasil e não "
                              "foi validada para português europeu nem para prosa literária; os níveis escolares são os "
                              "do sistema brasileiro de 1996. O índice só mede a extensão das frases e das palavras: "
                              "ignora o vocabulário raro, a sintaxe, a ironia e o conhecimento que o texto pressupõe.",
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

_SEG = "Depende da segmentação de frases do modelo e da pontuação da edição."
_FIN = "formas verbais finitas com tempo anotado"
INDICADORES.update({
    # Tipos de frase
    "frases_interrogativas_pct": Indicador(
        "Frases interrogativas", _T, "Frases cuja pontuação final é «?».", "% das frases",
        "Mais alto = mais perguntas, em geral associadas ao diálogo.", _SEG + " Perguntas indiretas não contam.",
        "frases terminadas em ? ÷ frases × 100", casas=1),
    "frases_exclamativas_pct": Indicador(
        "Frases exclamativas", _T, "Frases cuja pontuação final é «!».", "% das frases",
        "Mais alto = mais exclamações, em geral associadas ao diálogo e à expressividade.", _SEG,
        "frases terminadas em ! ÷ frases × 100", casas=1),
    # Morfologia verbal e pessoa
    "verbos_presente_pct": Indicador(
        "Verbos no presente", _M, "Formas verbais finitas com o traço Tense=Pres.", f"% das {_FIN}",
        "Mais alto = narração ou diálogo mais ancorados no presente.",
        "Depende do analisador morfológico; o presente histórico e o diálogo contam como presente.",
        referencias=("nivre2020",), casas=1, entre_linguas=False),
    "verbos_passado_pct": Indicador(
        "Verbos no passado", _M, "Formas verbais finitas no passado (Tense=Past, Imp ou Pqp: pretérito perfeito, "
        "imperfeito e mais-que-perfeito).", f"% das {_FIN}",
        "Mais alto = narração no passado, típica do romance.",
        "Cada língua divide os tempos de forma diferente (o inglês não tem imperfeito morfológico).",
        referencias=("nivre2020",), casas=1, entre_linguas=False),
    "verbos_futuro_pct": Indicador(
        "Verbos no futuro", _M, "Formas verbais finitas com o traço Tense=Fut.", f"% das {_FIN}",
        "Mais alto = mais projeção, promessa ou hipótese.",
        "Não aplicável ao inglês (futuro com o auxiliar will). O futuro perifrástico (vou fazer) não conta.",
        referencias=("nivre2020",), casas=1, entre_linguas=False),
    "verbos_conjuntivo_pct": Indicador(
        "Verbos no conjuntivo", _M, "Formas verbais finitas com o traço Mood=Sub.", "% das formas verbais finitas com "
        "modo anotado", "Mais alto = mais hipótese, desejo, dúvida ou subordinação.",
        "Não aplicável ao inglês (sem conjuntivo morfológico distinto no modelo).", referencias=("nivre2020",),
        casas=1, entre_linguas=False),
    "pronomes_1a_pessoa_por_1000": Indicador(
        "Pronomes de 1.ª pessoa", _M, "Pronomes pessoais com o traço Person=1 (eu, me, nós…) por 1000 palavras.",
        POR_1000, "Mais alto = narrador na 1.ª pessoa ou muito diálogo.",
        "Nas línguas de sujeito nulo (português) o sujeito fica muitas vezes implícito no verbo.",
        referencias=("nivre2020",), casas=1, entre_linguas=False),
    "pronomes_2a_pessoa_por_1000": Indicador(
        "Pronomes de 2.ª pessoa", _M, "Pronomes pessoais com o traço Person=2 (tu, te, vós, you…) por 1000 palavras.",
        POR_1000, "Mais alto = mais interpelação direta, sobretudo no diálogo.",
        "As formas de tratamento (você, o senhor) são gramaticalmente de 3.ª pessoa em português.",
        referencias=("nivre2020",), casas=1, entre_linguas=False),
    "pronomes_3a_pessoa_por_1000": Indicador(
        "Pronomes de 3.ª pessoa", _M, "Pronomes pessoais com o traço Person=3 (ele, ela, lhe, se…) por 1000 palavras.",
        POR_1000, "Mais alto = narração centrada em terceiros, típica do narrador heterodiegético.",
        "Inclui pronomes reflexos e clíticos conforme a anotação do modelo.", referencias=("nivre2020",), casas=1,
        entre_linguas=False),
    # Leis do vocabulário
    "zipf_expoente": Indicador(
        "Expoente de Zipf", _Z, "Declive (com sinal trocado) da reta ajustada à frequência das formas em função da "
        "sua posição, em escala log-log.", "adimensional",
        "Próximo de 1 na maior parte dos textos; mais alto = vocabulário mais concentrado nas palavras mais "
        "frequentes.", "Depende do intervalo de frequências usado no ajuste (só formas com frequência mínima "
        "configurável) e da extensão do texto.", "f(r) ≈ C · r^−s; s = −declive de log f em log r",
        ("zipf1949",), 2, False),
    "zipf_r2": Indicador(
        "Ajuste da lei de Zipf (R²)", _Z, "Coeficiente de determinação da reta de Zipf em escala log-log.", "0–1",
        "Mais perto de 1 = a distribuição segue bem uma lei de potência.",
        "Um R² alto em escala log-log não prova uma lei de potência; serve só para descrever o ajuste.",
        referencias=("zipf1949",), casas=3, entre_linguas=False),
    "heaps_beta": Indicador(
        "Expoente de Heaps (β)", _Z, "Ritmo de crescimento do vocabulário à medida que o texto avança.",
        "adimensional", "Entre 0 e 1; mais alto = o livro continua a introduzir palavras novas.",
        "Depende da extensão do texto e da morfologia da língua (línguas com mais flexão têm β maior).",
        "V(N) ≈ K · N^β, ajustado em escala log-log", ("heaps1978",), 3, False),
    "heaps_k": Indicador(
        "Constante de Heaps (K)", _Z, "Fator de escala da lei de Heaps.", "adimensional",
        "Interpreta-se em conjunto com β; sozinho tem pouco significado.", "Muito sensível a β.",
        "V(N) ≈ K · N^β", ("heaps1978",), 1, False),
    "heaps_r2": Indicador(
        "Ajuste da lei de Heaps (R²)", _Z, "Coeficiente de determinação do ajuste de Heaps.", "0–1",
        "Mais perto de 1 = o crescimento do vocabulário segue bem uma lei de potência.",
        "Descreve só a qualidade do ajuste.", referencias=("heaps1978",), casas=3, entre_linguas=False),
    # Sentimento
    "sentimento_medio": Indicador(
        "Sentimento médio", _SE, "Média da pontuação «compound» do VADER nas frases com pelo menos 3 palavras.",
        "−1 a +1", "Acima de 0 = vocabulário globalmente positivo; abaixo de 0 = negativo. Valores entre −0,05 e "
        "+0,05 são neutros.",
        "Método de léxico e regras criado para redes sociais, não para literatura; não deteta ironia nem distingue "
        "a voz do narrador da das personagens; o léxico português foi criado para português do Brasil e cobre mal "
        "a ortografia antiga. Não validado com anotação humana neste projeto. Léxicos diferentes por língua.",
        "média das pontuações compound por frase", ("hutto2014", "leia", "deprez2021"), 3, False),
    "frases_positivas_pct": Indicador(
        "Frases positivas", _SE, "Frases com compound ≥ 0,05.", "% das frases pontuadas",
        "Proporção de frases com vocabulário predominantemente positivo.", "Ver «Sentimento médio».",
        "frases com compound ≥ 0,05 ÷ frases pontuadas × 100", ("hutto2014",), 1, False),
    "frases_negativas_pct": Indicador(
        "Frases negativas", _SE, "Frases com compound ≤ −0,05.", "% das frases pontuadas",
        "Proporção de frases com vocabulário predominantemente negativo.", "Ver «Sentimento médio».",
        "frases com compound ≤ −0,05 ÷ frases pontuadas × 100", ("hutto2014",), 1, False),
    "frases_neutras_pct": Indicador(
        "Frases neutras", _SE, "Frases com compound entre −0,05 e 0,05.", "% das frases pontuadas",
        "Inclui frases sem nenhuma palavra do léxico.", "Uma cobertura baixa do léxico aumenta esta percentagem.",
        referencias=("hutto2014",), casas=1, entre_linguas=False),
    "cobertura_lexico_pct": Indicador(
        "Cobertura do léxico de sentimento", _SE, "Palavras do texto que existem no léxico de sentimento usado.",
        "% das palavras", "Indicador de qualidade: abaixo de ~5 %, o sentimento assenta em muito poucas palavras.",
        "Conta formas exatas (sem lematização), como o próprio VADER.", casas=1, entre_linguas=False),
})

# Métodos que produzem tabelas ou gráficos em vez de um único valor
METODOS = {
    "arco_sentimento": Indicador(
        "Arco de sentimento", _SE, "Sentimento médio e proporção de frases positivas e negativas em cada segmento do "
        "livro (segmentos com o mesmo número de palavras).", "−1 a +1 e %",
        "Mostra como a polaridade do vocabulário sobe e desce ao longo da narrativa.",
        "Herda as limitações do léxico; com poucos segmentos, as oscilações podem dever-se a episódios isolados.",
        referencias=("reagan2016", "hutto2014")),
    "colocacoes": Indicador(
        "Colocações", "Vocabulário", "Pares de palavras contíguas na mesma frase que ocorrem juntas muito mais do que "
        "o acaso faria prever; excluem-se os pares formados só por palavras gramaticais.", "G² e PMI",
        "G² alto = associação estatisticamente forte; PMI alto = associação exclusiva (mas instável em pares raros).",
        "Formas, não lemas; não distingue expressões fixas de repetições de nomes («Carlos da Maia»).",
        "G² = 2 Σ O·ln(O/E) na tabela de contingência 2×2; PMI = log2(O11 ÷ E11)",
        ("dunning1993", "church1990")),
    "palavras_chave": Indicador(
        "Palavras-chave por segmento", "Vocabulário", "Lemas de conteúdo mais característicos de cada segmento, por "
        "comparação com os outros segmentos do mesmo livro.", "TF-IDF por 1000 palavras",
        "Sugere os temas, lugares e personagens que dominam cada parte do livro.",
        "Lemas presentes em todos os segmentos nunca aparecem (idf = 0); depende do número de segmentos.",
        "tf × log(segmentos ÷ segmentos que contêm o lema)", ("sparckjones1972",)),
    "tempos_verbais": Indicador(
        "Tempos e modos verbais", _M, "Distribuição das formas verbais finitas por tempo e modo.",
        "% das formas finitas", "Ajuda a caracterizar a narração (passado) e o diálogo (presente, conjuntivo).",
        "Traços morfológicos atribuídos automaticamente pelo spaCy.", referencias=("nivre2020",)),
    "zipf_heaps": Indicador(
        "Curvas de Zipf e de Heaps", _Z, "Frequência em função da posição (Zipf) e crescimento do vocabulário com a "
        "extensão do texto (Heaps), em escala log-log.", "—",
        "Leis empíricas observadas em quase todos os textos; os desvios dizem algo sobre o estilo e a língua.",
        "Ver os indicadores do grupo.", referencias=("zipf1949", "heaps1978")),
}


def referencias_de(chaves) -> list[str]:
    usadas = []
    for k in chaves:
        fonte = INDICADORES.get(k) or METODOS.get(k)
        for r in fonte.referencias if fonte else ():
            if r not in usadas:
                usadas.append(r)
    return [REFERENCIAS[r] for r in sorted(usadas, key=lambda r: REFERENCIAS[r])]


def por_grupo() -> dict[str, list[str]]:
    grupos = {g: [] for g in GRUPOS}
    for k, ind in INDICADORES.items():
        grupos[ind.grupo].append(k)
    return grupos
