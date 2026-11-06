# livros-pln

**Indicadores linguísticos, estilométricos, de sentimento e de rede de personagens para livros em TXT ou EPUB, em português, francês e inglês, com definições, limitações e referências para cada valor.**

[![processar livros](../../actions/workflows/processar.yml/badge.svg)](../../actions/workflows/processar.yml)

🇵🇹 [Português](#-português) · 🇬🇧 [English](#-english)

![Rede de personagens de Os Maias](resultados/livros/eca-de-queiros-os-maias/graficos/rede.png)

**[Resultados](resultados/README.md)** · **[Documentação dos indicadores](docs/indicadores.md)** · **[Painel interativo de comparação](https://joo2002vsc.github.io/livros-pln/resultados/painel.html)** · **[Painel de *Os Maias*](https://joo2002vsc.github.io/livros-pln/resultados/livros/eca-de-queiros-os-maias/painel.html)**

---

## 🇵🇹 Português

### Objetivo

Dado um livro (ficheiro ou link), o livros-pln extrai os metadados e calcula indicadores de processamento de linguagem natural (PLN) sobre o vocabulário, a extensão e a estrutura das frases, as classes gramaticais, a pontuação, o diálogo, as entidades nomeadas e a rede de personagens. Cada valor vem acompanhado da definição, da unidade, de uma interpretação prudente, das limitações e da referência bibliográfica do método.

O projeto descreve textos; não os avalia. Os indicadores servem para formular perguntas sobre um livro e comparar livros da mesma língua. Não servem para emitir juízos de qualidade, atribuir autoria ou provar relações entre personagens.

### Perguntas a que procura responder

- Quão variado é o vocabulário de um livro, independentemente da sua extensão?
- Como se distribui a extensão das frases, e quão complexa é a sua estrutura sintática?
- Que peso têm o diálogo, os nomes próprios e as diferentes classes gramaticais, e como variam ao longo do livro?
- Que personagens aparecem juntas no texto, e com que frequência?
- O livro é de leitura fácil ou difícil, segundo a fórmula de Flesch adaptada à sua língua?
- Como varia a polaridade do vocabulário (sentimento) ao longo da narrativa?
- Que pares de palavras e que palavras-chave caracterizam o livro e cada uma das suas partes?
- Que livros da mesma língua são estilisticamente mais próximos nas palavras mais frequentes?

### Num comando

```bash
python -m livros_pln analisar https://www.gutenberg.org/ebooks/40409      # link do Project Gutenberg
python -m livros_pln analisar https://exemplo.org/um-livro.epub           # link direto para .txt ou .epub
python -m livros_pln analisar livros/um-livro.txt --abrir                 # ficheiro local; abre o painel no fim
python -m livros_pln analisar https://www.gutenberg.org/ebooks/3333 --nome camoes-os-lusiadas   # escolhe o nome
python -m livros_pln                                                      # todos os livros de livros/ (só o que mudou)
python -m livros_pln --forcar                                             # reprocessa tudo
```

Resultados de cada livro, em `resultados/livros/<livro>/`:

| Ficheiro | Conteúdo |
| --- | --- |
| `README.md` | Relatório em 15 secções: identificação, qualidade dos dados, indicadores por grupo (com interpretação e limitações), legibilidade, sentimento, outros conceitos de PLN, gráficos, comentários automáticos descritivos, metodologia e referências |
| `painel.html` | Painel interativo (Plotly): ficha técnica no cabeçalho, veredicto de leitura (fácil ou difícil) e gráficos em 3D, cada um com uma vista 2D alternativa |
| `<livro>.xlsx` | Metadados (incluindo parâmetros, versões e exatidão do modelo), indicadores com estado e definição, avisos de qualidade e todas as tabelas |
| `indicadores.json`, `*.csv` | Os mesmos dados em formato aberto |
| `graficos/*.png`, `*.svg` | Gráficos estáticos em PNG (200 ppp) e SVG |

Ao nível do corpus: `resultados/README.md`, `indicadores.csv`/`.xlsx` (com um dicionário de indicadores), gráficos comparativos e um painel de comparação. Quando há livros suficientes, também a matriz de correlações e o Delta de Burrows.

### Indicadores

A lista completa está em **[docs/indicadores.md](docs/indicadores.md)**, com fórmulas, unidades, interpretação, limitações, comparabilidade entre línguas e referências. Esse ficheiro é gerado a partir de `livros_pln/catalogo.py`, a mesma fonte usada pelos relatórios e pelo Excel.

| Grupo | Indicadores principais | Referências |
| --- | --- | --- |
| Diversidade lexical | TTR, **MATTR** (janela configurável), **MTLD**, **HD-D**, K de Yule, hapax | Covington e McFall (2010); McCarthy e Jarvis (2010); Tweedie e Baayen (1998); Yule (1944) |
| Densidade lexical | Palavras de conteúdo ÷ palavras | Ure (1971) |
| Extensão das frases | Média, mediana, percentis 25 e 75, desvio-padrão, máximo, % de frases longas | — |
| Complexidade sintática | Profundidade da árvore de dependências, distância de dependência média, orações subordinadas por frase | Liu (2008); Nivre et al. (2020) |
| Classes gramaticais | 12 classes UPOS por 1000 palavras (valores absolutos e relativos), pronomes pessoais, verbos modais | Nivre et al. (2020) |
| Legibilidade | Flesch adaptado a cada língua, com faixas da língua e veredicto «fácil» ou «difícil»; Flesch–Kincaid só para inglês | Flesch (1948); Kandel e Moles (1958); Martins et al. (1996); Kincaid et al. (1975) |
| Sentimento | Pontuação por frase (VADER e adaptações), % de frases positivas e negativas, arco ao longo do livro, cobertura do léxico, frases mais extremas | Hutto e Gilbert (2014); LeIA; Deprez e Ek (2021); Reagan et al. (2016) |
| Tipos de frase e morfologia verbal | % de frases interrogativas e exclamativas; tempos e modos verbais; pronomes de 1.ª, 2.ª e 3.ª pessoa | Nivre et al. (2020) |
| Leis do vocabulário | Expoente de Zipf e expoente de Heaps, com qualidade do ajuste | Zipf (1949); Heaps (1978) |
| Colocações e palavras-chave | Pares de palavras associados (G² e PMI); palavras-chave de cada segmento (TF-IDF) | Dunning (1993); Church e Hanks (1990); Spärck Jones (1972) |
| Pontuação e discurso | 10 sinais por 1000 palavras; % de parágrafos de diálogo (heurística) | — |
| Entidades e rede | Pessoas, lugares e organizações (NER); rede de co-ocorrência com centralidade e comunidades | Blondel et al. (2008) |
| Estilometria | Delta de Burrows entre livros da mesma língua | Burrows (2002); Evert et al. (2017) |

### Metodologia

```text
ficheiro ou link ─▶ fontes ─▶ leitura ─▶ língua ─▶ qualidade ─▶ anotação (spaCy) ─▶ indicadores ─▶ relatórios
                    download   texto e    pt/fr/en  verificações  tokens e frases     catálogo,     Markdown, Excel,
                               metadados            do texto      em DataFrames       estados       PNG/SVG, Plotly
```

1. **Leitura e metadados.** Guardam-se só os metadados principais: título, autor, ano, idioma e fonte. TXT: UTF-8, Windows-1252 ou Latin-1; o cabeçalho e a licença do Project Gutenberg são retirados e `--` é convertido em travessão. EPUB: texto pela ordem de leitura e metadados Dublin Core.
2. **Língua.** Deteção pela frequência de palavras funcionais, com aviso quando a margem entre línguas é pequena ou quando diverge da língua declarada.
3. **Qualidade dos dados.** Verifica texto vazio ou curto, sinais de codificação errada, parágrafos duplicados e segmentação de frases suspeita.
4. **Anotação.** Modelos spaCy `pt_core_news_lg`, `fr_core_news_md` e `en_core_web_md` (versão 3.8.0). Para o português usa-se o modelo grande (`lg`), cuja exatidão declarada é ligeiramente superior à do médio na etiquetagem (97,2 % contra 97,0 %), na morfologia (96,1 % contra 95,6 %), na segmentação de frases (F 95,2 contra 94,1) e no reconhecimento de entidades (F 90,3 contra 89,6), e praticamente igual nas dependências (LAS 85,9 contra 86,0); ocupa cerca de 550 MB. O texto passa a duas tabelas pandas: uma com um token por linha e outra com uma frase por linha (extensão, profundidade, distâncias, subordinadas).
5. **Indicadores.** Cada indicador tem um estado: *válido*, *não aplicável* (com motivo), *desconhecido* ou *falha*. **Um valor ausente nunca é substituído por zero.**
6. **Comparação.** Os gráficos e relatórios de corpus agrupam os livros por língua e assinalam os indicadores que não são comparáveis entre línguas.

#### Escolhas metodológicas

- **Extensão não é complexidade.** A extensão das frases e a complexidade sintática são grupos separados. A complexidade mede-se na árvore de dependências.
- **Diversidade lexical independente da extensão.** O TTR diminui com o tamanho do texto, por isso os relatórios dão destaque ao MTLD e ao HD-D, que são menos sensíveis à extensão (McCarthy e Jarvis, 2010). Nos testes, as implementações são comparadas com o pacote `lexical-diversity`.
- **Legibilidade sem falsa equivalência.** Cada língua usa a sua adaptação da fórmula de Flesch, e os valores de línguas diferentes não se comparam. A adaptação portuguesa (Martins et al., 1996) foi calibrada com manuais escolares em português do Brasil e não foi validada para português europeu nem para prosa literária; os relatórios indicam-no. As sílabas são estimadas por regras, e a exatidão medida está em [docs/indicadores.md](docs/indicadores.md#exatidão-da-estimativa-de-sílabas).
- **Legibilidade: fácil ou difícil.** O veredicto usa as faixas da língua: em português, as de Martins et al. (1996), em que 50 ou mais é «fácil» (5.º ao 8.º ano de escolaridade no sistema brasileiro); em inglês e francês, a escala de Flesch (1948), em que 60 ou mais é «padrão» ou mais fácil. A fórmula só mede a extensão das frases e das palavras: um romance do século XIX pode ser classificado como «fácil» apesar do vocabulário antigo e da ironia.
- **Sentimento com cautela.** Cada língua usa uma adaptação do VADER (léxico e regras): vaderSentiment (inglês), LeIA (português do Brasil) e VADER-FR (francês). Os léxicos foram criados para mensagens curtas das redes sociais e não foram validados neste projeto com anotação humana; medem a polaridade do vocabulário, não o tom narrativo nem a ironia. A cobertura do léxico (percentagem de palavras do texto que existem no léxico) é registada como indicador de qualidade: em *Os Maias* é de cerca de 6 %, em parte por causa da ortografia anterior a 1911.
- **Exatidão dos modelos.** A exatidão declarada de cada modelo spaCy (classes gramaticais, dependências, segmentação, NER) fica registada nos resultados. Os modelos foram treinados com texto contemporâneo, por isso os erros são mais frequentes em textos antigos.
- **Co-ocorrência não é relação narrativa.** Uma ligação na rede significa que duas personagens aparecem no mesmo parágrafo, não que interagem. Não há resolução de correferência: pronomes e descrições («o rapaz») não contam.
- **Estilometria não é prova de autoria.** O Delta de Burrows mede distâncias nas palavras mais frequentes. Só é calculado com pelo menos três livros da mesma língua, porque os z-scores exigem uma amostra. Distâncias pequenas indicam semelhança no uso de palavras gramaticais, que também depende do género, da época, da edição e da tradução.
- **Sem modelação de tópicos.** LDA e BERTopic não foram incluídos. Com poucos livros, os tópicos são instáveis (mudam com a semente aleatória e com o número de tópicos escolhido) e difíceis de validar sem anotação humana. Acrescentariam resultados de aparência objetiva sem garantia de serem interpretáveis. As frequências de lemas de conteúdo, por segmento, cumprem a função descritiva com menos parâmetros arbitrários.
- **Correlações só com dados suficientes.** A matriz de correlações (Spearman) entre indicadores só é gerada com pelo menos 5 livros; abaixo disso, o relatório explica porquê.

### Exemplo: os dois livros incluídos

Valores do corpus de exemplo, gerados pela versão 3.3.0 (português com `pt_core_news_lg`). Os dois livros estão em línguas diferentes, por isso os indicadores não comparáveis entre línguas não devem ser lidos lado a lado.

| Indicador | *Os Maias* (pt, 1888) | *Alice's Adventures in Wonderland* (en, 1865) | Comparável entre línguas |
| --- | ---: | ---: | :---: |
| Palavras | 203 558 | 26 594 | sim |
| MTLD | 139,0 | 73,3 | não |
| HD-D | 0,884 | 0,849 | não |
| Extensão mediana das frases (palavras) | 9 | 12 | sim, com cautela |
| Frases com mais de 30 palavras | 7,5 % | 15,7 % | sim, com cautela |
| Profundidade sintática média | 3,22 | 4,14 | não |
| Distância de dependência média | 2,54 | 2,62 | não |
| Facilidade de leitura (Flesch adaptado) | 63,8 (fácil) | 79,7 (razoavelmente fácil) | **não** |
| Parágrafos de diálogo | 52,4 % | 78,8 % | sim, com cautela |
| Leitura | Fácil (5.º ao 8.º ano) | Fácil | **não** |
| Sentimento médio (−1 a +1) | −0,003 | 0,034 | **não** |
| Cobertura do léxico de sentimento | 6,2 % | 6,7 % | não |
| Verbos no passado | 72 % | 71 % | não |
| Expoente de Zipf · expoente de Heaps | 1,04 · 0,733 | 1,06 · 0,649 | não |

### Painel interativo

O painel de cada livro tem a ficha técnica (autor, ano, idioma e fonte) no cabeçalho, um índice fixo que assinala a secção em leitura, uma barra de progresso, um botão para voltar ao topo, os indicadores principais em destaque, uma régua com o veredicto de leitura e secções numeradas (Personagens, Vocabulário, Gramática, Frases e Evolução, Sentimento, Leis do Vocabulário, Lugares). Os gráficos são em 3D (barras em prisma, relevos e fitas) e rodam apenas quando o leitor os arrasta. Como a perspetiva dificulta a leitura exata dos valores, cada gráfico 3D tem um botão para a vista 2D com os mesmos dados, e os valores exatos aparecem ao passar o rato. As curvas de Zipf e de Heaps ficam em 2D: são as escalas logarítmicas que tornam as leis visíveis, e uma terceira dimensão não acrescentaria informação.

### Instalação e testes

```bash
python -m pip install -r requirements-dev.txt     # dependências e implementação de referência para os testes
bash .github/scripts/instalar_modelos.sh          # modelos pt, fr e en (com alternativa no Hugging Face)
python -m pytest                                   # testes unitários e de integração
python -m livros_pln.documentacao                  # regenera docs/indicadores.md a partir do catálogo
```

Os testes cobrem:

- valores de referência calculados à mão: fórmulas de legibilidade, K de Yule, MATTR, e profundidade e distância de dependência numa árvore construída;
- a comparação com a implementação de referência do MTLD, do HD-D e do MATTR;
- listas de sílabas anotadas à mão;
- casos-limite (textos vazios ou curtos dão «não aplicável», não zero);
- as verificações de qualidade;
- o Delta de Burrows com dados sintéticos;
- as faixas de legibilidade, o sentimento de frases de exemplo nas três línguas (e o estado «desconhecido» quando falta o pacote), Zipf e Heaps com dados sintéticos de expoente conhecido, colocações e palavras-chave;
- o pipeline completo.

### Reprodutibilidade

- Os parâmetros (janela do MATTR, limiar do MTLD, limiar de frase longa, número de segmentos, palavras do Delta, etc.) estão em [`config/parametros.toml`](config/parametros.toml).
- Cada resultado regista os parâmetros usados, as versões do Python, das bibliotecas e do modelo spaCy, a exatidão declarada do modelo, a impressão digital do código e o commit.
- Um livro é reprocessado quando muda o ficheiro, o dicionário de personagens, o código ou a configuração.

### Atualização automática no GitHub

O workflow [`processar.yml`](.github/workflows/processar.yml) corre quando muda o código, a configuração, os testes, as dependências ou o próprio workflow. Instala as dependências e os modelos, corre os testes, verifica que a documentação está sincronizada com o catálogo, reprocessa os livros e faz commit de `resultados/`. Acrescentar um livro não dispara o workflow: corra-o localmente ou use **Actions → processar livros → Run workflow**.

### Pastas de trabalho no computador

Para guardar os livros e os resultados fora do repositório, copiar `config/pastas.exemplo.toml` para `config/pastas.toml` e indicar as pastas:

```toml
livros = "~/Desktop/Projetos Pessoais/Análises de Livros/livros"
resultados = "~/Desktop/Projetos Pessoais/Análises de Livros/resultados"
```

`config/pastas.toml` não vai para o GitHub. Os comandos `python -m livros_pln` e `python -m livros_pln analisar` passam a usar essas pastas; `--pasta` e `--saida` continuam a sobrepor-se. O workflow do GitHub Actions usa sempre `livros/` e `resultados/` do repositório.

### Textos em verso

Os textos em verso (por exemplo, *Os Lusíadas*) são detetados pela extensão das linhas do ficheiro TXT. Nesse caso, o relatório indica o número de versos, de estrofes e de versos por estrofe; a legibilidade de Flesch e a percentagem de diálogo ficam «não aplicável», porque foram pensadas para prosa; e um aviso lembra que os modelos linguísticos e os léxicos de sentimento foram treinados com prosa contemporânea.

### Configuração

- `config/parametros.toml`: parâmetros metodológicos.
- `livros/metadados.csv`: completa ou corrige metadados e pode forçar a língua.
- `livros/personagens/<livro>.json`: dicionário de personagens ([instruções](livros/personagens/README.md)); *Os Maias* tem um com 35 personagens.
- `config/stopwords-<língua>.txt`: palavras a ignorar nas frequências (por exemplo, grafias anteriores a 1911: «elle», «ella»).

### Estrutura

```text
livros-pln/
├── livros/                 livros, metadados.csv e dicionários de personagens
├── livros_pln/
│   ├── catalogo.py         definições, fórmulas, limitações e referências de todos os indicadores
│   ├── configuracao.py     parâmetros (config/parametros.toml)
│   ├── qualidade.py        verificações de qualidade e estados dos valores
│   ├── indicadores.py      anotação spaCy, métricas lexicais, sintáticas e de legibilidade
│   ├── estilometria.py     Delta de Burrows
│   ├── sentimento.py       sentimento por frase (VADER, LeIA, VADER-FR)
│   ├── graficos3d.py       barras, relevos, fitas e dispersões 3D para os painéis
│   ├── personagens.py      rede de personagens (NER ou dicionário)
│   ├── tema.py             identidade visual comum (paleta, tipografia, formato numérico)
│   ├── graficos.py         gráficos estáticos (matplotlib, PNG e SVG)
│   ├── interativo.py       painéis Plotly
│   ├── relatorio.py        relatórios em Markdown
│   ├── exportar.py         Excel
│   ├── documentacao.py     gera docs/indicadores.md
│   ├── fontes.py, leitura.py, lingua.py
│   └── processar.py        linha de comandos, cache e registo do ambiente
├── config/                 parâmetros e stopwords
├── docs/indicadores.md     documentação gerada
├── tests/                  testes (pytest) e listas anotadas
└── resultados/             gerado automaticamente; não editar
```

### Limitações

- Só suporta português, francês e inglês; a deteção de língua escolhe entre estas três.
- Os modelos spaCy são treinados com texto contemporâneo (notícias, web). A etiquetagem, a análise sintática e o NER erram mais em grafias e sintaxe antigas.
- A estimativa de sílabas é heurística (ver a exatidão medida), e as fórmulas de legibilidade foram calibradas para textos escolares, não para literatura.
- A percentagem de diálogo é uma heurística tipográfica e depende das convenções da edição.
- O sentimento assenta em léxicos de redes sociais, com pouca cobertura em prosa literária e ortografias antigas; não deteta ironia nem distingue a voz do narrador da das personagens.
- A rede automática depende do NER. Para resultados fiáveis num livro concreto, use um dicionário de personagens.
- Com poucos livros, as comparações de corpus são descritivas; a matriz de correlações e o Delta só aparecem quando há dados suficientes.

### Referências

Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment, 2008*(10), P10008. https://doi.org/10.1088/1742-5468/2008/10/P10008

Brysbaert, M. (2019). How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language, 109*, 104047. https://doi.org/10.1016/j.jml.2019.104047

Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide to likely authorship. *Literary and Linguistic Computing, 17*(3), 267–287. https://doi.org/10.1093/llc/17.3.267

Church, K. W., & Hanks, P. (1990). Word association norms, mutual information, and lexicography. *Computational Linguistics, 16*(1), 22–29. https://aclanthology.org/J90-1003

Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). *Journal of Quantitative Linguistics, 17*(2), 94–100.

Deprez, O., & Ek, T. (2021). *vaderSentiment-fr* (Versão 1.3.4) [Software]. PyPI. https://pypi.org/project/vaderSentiment-fr/

Dunning, T. (1993). Accurate methods for the statistics of surprise and coincidence. *Computational Linguistics, 19*(1), 61–74. https://aclanthology.org/J93-1003

Evert, S., Proisl, T., Jannidis, F., Reger, I., Pielström, S., Schöch, C., & Vitt, T. (2017). Understanding and explaining Delta measures for authorship attribution. *Digital Scholarship in the Humanities, 32*(suppl. 2), ii4–ii16. https://doi.org/10.1093/llc/fqx023

Flesch, R. (1948). A new readability yardstick. *Journal of Applied Psychology, 32*(3), 221–233. https://doi.org/10.1037/h0057532

Heaps, H. S. (1978). *Information retrieval: Computational and theoretical aspects*. Academic Press.

Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). *spaCy: Industrial-strength natural language processing in Python* [Software]. Zenodo. https://doi.org/10.5281/zenodo.1212303

Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1), 216–225. https://doi.org/10.1609/icwsm.v8i1.14550

Kandel, L., & Moles, A. (1958). Application de l'indice de Flesch à la langue française. *Cahiers d'Études de Radio-Télévision, 19*.

Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). *Derivation of new readability formulas (Automated Readability Index, Fog Count and Flesch Reading Ease Formula) for Navy enlisted personnel* (Research Branch Report 8-75). Naval Technical Training Command.

Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. *Journal of Cognitive Science, 9*(2), 159–191. https://hdl.handle.net/10371/70907

Martins, T. B. F., Ghiraldelo, C. M., Nunes, M. G. V., & Oliveira Jr., O. N. (1996). *Readability formulas applied to textbooks in Brazilian Portuguese* (Notas do ICMSC-USP, Série Computação, 28). ICMSC-USP.

McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods, 42*(2), 381–392. https://doi.org/10.3758/BRM.42.2.381

Nivre, J., de Marneffe, M.-C., Ginter, F., Hajič, J., Manning, C. D., Pyysalo, S., Schuster, S., Tyers, F., & Zeman, D. (2020). Universal Dependencies v2: An evergrowing multilingual treebank collection. In *Proceedings of the 12th Language Resources and Evaluation Conference* (pp. 4034–4043). European Language Resources Association. https://aclanthology.org/2020.lrec-1.497

rafjaa. (s.d.). *LeIA: Léxico para Inferência Adaptada* [Software]. GitHub. https://github.com/rafjaa/LeIA

Reagan, A. J., Mitchell, L., Kiley, D., Danforth, C. M., & Dodds, P. S. (2016). The emotional arcs of stories are dominated by six basic shapes. *EPJ Data Science, 5*(1). https://doi.org/10.1140/epjds/s13688-016-0093-1

Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. *Journal of Documentation, 28*(1), 11–21. https://doi.org/10.1108/eb026526

Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? Measures of lexical richness in perspective. *Computers and the Humanities, 32*(5), 323–352. https://doi.org/10.1023/A:1001749303137

Ure, J. (1971). Lexical density and register differentiation. In G. E. Perren & J. L. M. Trim (Eds.), *Applications of linguistics* (pp. 443–452). Cambridge University Press.

Yule, G. U. (1944). *The statistical study of literary vocabulary*. Cambridge University Press.

Zipf, G. K. (1949). *Human behavior and the principle of least effort*. Addison-Wesley.

---

## 🇬🇧 English

Give it a book (a TXT or EPUB file, a Project Gutenberg link or a direct link) and it returns the metadata and a documented set of NLP indicators for Portuguese, French or English:

- length-independent lexical diversity (MTLD, HD-D, MATTR);
- the distribution of sentence length;
- dependency-based syntactic complexity;
- parts of speech per 1,000 words;
- language-specific readability formulas;
- punctuation and dialogue;
- named entities and a character co-occurrence network;
- Burrows's Delta across books in the same language;
- sentence-level sentiment (VADER and its Portuguese and French adaptations), a readability verdict (easy or difficult), Zipf's and Heaps' laws, collocations (G², PMI), TF-IDF keywords per segment, verb tense and mood, and grammatical person.

Every value has an explicit state (valid, not applicable, unknown or failed); missing values are never replaced by zero. Each also has a definition, limitations and an APA 7 reference.

Results come as Markdown reports, Excel, CSV/JSON, PNG/SVG charts with a shared visual identity, and interactive Plotly dashboards. A GitHub Actions workflow runs the tests and reprocesses the books whenever the code changes.

---

Código: © João Garção, todos os direitos reservados. Os livros incluídos como exemplo são do domínio público (Project Gutenberg).
