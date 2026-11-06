# Alterações

## 3.4.0 · 2026-11-06

- **Pastas de trabalho locais**: `config/pastas.toml` (fora do GitHub, ver `config/pastas.exemplo.toml`) indica onde ficam os livros e os resultados no computador. Sem esse ficheiro, continuam a usar-se `livros/` e `resultados/`; o workflow do GitHub Actions não muda. O ficheiro não entra na impressão digital do código.
- **`analisar --nome`**: escolhe o nome do ficheiro descarregado (por exemplo, `camoes-os-lusiadas` em vez de `gutenberg-3333`), que é também o nome do dicionário de personagens e da pasta de resultados.
- **Textos em verso**: deteção automática (pela extensão das linhas do TXT), com os indicadores versos, estrofes e versos por estrofe. Em verso, a legibilidade de Flesch e a heurística de diálogo ficam «não aplicável» (foram pensadas para prosa) e há um aviso de qualidade sobre a fiabilidade dos modelos e dos léxicos.

## 3.3.0 · 2026-11-06

- **Modelo português grande**: `pt_core_news_lg` 3.8.0 em vez de `pt_core_news_md`. Exatidão declarada ligeiramente superior na etiquetagem, morfologia, segmentação e entidades; dependências praticamente iguais. Os indicadores de *Os Maias* mudam pouco (por exemplo, profundidade sintática 3,29 → 3,22; nomes próprios por 1000 palavras 81 → 90; frases 16 759 → 16 527).
- **Só os metadados principais**: título, autor, ano, idioma e fonte. O ano vem de `metadados.csv`, da publicação original indicada pelo Project Gutenberg ou da data do EPUB (nunca da data de publicação digital); a fonte inclui o número do Project Gutenberg. A coluna `fonte` passou a ser aceite em `metadados.csv`. Os dados técnicos (ficheiro, codificação, modelos) passaram para a folha «Processamento» do Excel e para o rodapé do painel.
- Corrigida a leitura do número do Project Gutenberg nos cabeçalhos recentes («[eBook #40409]»).
- **Painel**: cabeçalho maior e a negrito (título, autor, ficha técnica e barra superior); botão para voltar ao topo, que aparece ao fazer scroll; barra de progresso de leitura; o índice assinala a secção em leitura; estilos de impressão; respeito pela preferência de movimento reduzido. A rede de personagens em barras 3D mostra as 15 personagens principais, para que os nomes não se sobreponham.

## 3.2.0 · 2026-11-06

**Novos conceitos de PLN**
- Análise de sentimento por frase com o método VADER (léxico e regras): vaderSentiment (inglês), LeIA (português) e VADER-FR (francês). Indicadores: sentimento médio, % de frases positivas, negativas e neutras, cobertura do léxico; arco de sentimento por segmento; frases mais positivas e mais negativas. Sem o pacote instalado, o estado fica «desconhecido», nunca zero.
- Legibilidade com faixas por língua: Martins et al. (1996) para português (com nível escolar, verificado na fonte primária) e Flesch (1948) para inglês e francês; veredicto «fácil» ou «difícil».
- Tipos de frase (interrogativas, exclamativas), tempos e modos verbais, pronomes de 1.ª, 2.ª e 3.ª pessoa.
- Leis de Zipf e de Heaps (expoentes e qualidade do ajuste), colocações (G² de Dunning e PMI) e palavras-chave por segmento (TF-IDF).
- Catálogo com 79 indicadores e 5 métodos de tabela ou gráfico; novas referências verificadas (APA 7).

**Painel HTML**
- Ficha técnica (metadados) no cabeçalho; régua de legibilidade com o veredicto de leitura.
- Gráficos em 3D (barras em prisma, relevo da extensão das frases, fitas da evolução, dispersão das colocações), sem rotação automática; cada um tem uma vista 2D com os mesmos dados. Zipf e Heaps ficam em 2D (escalas logarítmicas).
- Novas secções: Vocabulário, Gramática, Sentimento e Leis do Vocabulário; citações das frases mais extremas.

**Relatórios e dados**
- Relatório com 15 secções (novas: Sentimento e Outros conceitos de PLN); gráficos estáticos do arco de sentimento e das leis de Zipf e Heaps.
- Novos ficheiros: `colocacoes.csv`, `palavras-chave.csv`, `tempos-verbais.csv`, `sentimento-frases-extremas.csv`; o Excel inclui as novas tabelas.
- Novas dependências: `vaderSentiment`, `leia-br`, `vaderSentiment-fr`.

## 3.1.0 · 2026-11-06

**Painéis interativos (HTML)**
- Aspeto editorial com a paleta bege, preto e castanho: cabeçalho com o ícone num selo dourado, título em Cormorant Garamond, autoria em itálico e dados principais do livro; índice fixo com secções numeradas em romano.
- Indicadores principais em números grandes, numa grelha com filetes, sem cartões; ficha técnica com linhas pontilhadas e notas sobre a qualidade dos dados.
- Gráficos sem caixas, sobre o fundo da página, com título e subtítulo escritos no HTML; títulos e subtítulos com maiúscula inicial em cada palavra (exceto artigos, preposições e conjunções curtas).
- Rodapé com descrição do projeto, ligações (relatório, todos os livros, Excel, repositório) e dados técnicos da análise.
- Ícone do projeto no separador do navegador (favicon) e no cabeçalho, embutido no próprio HTML para funcionar no GitHub Pages e em ficheiros abertos localmente.
- A rede de personagens em 3D deixou de rodar automaticamente e já não tem botões de animação: é o leitor que a roda, arrastando com o rato ou com o dedo. Nós e nomes maiores; comunidades distinguidas por cor e por forma.
- Os gráficos estáticos (PNG/SVG) mantêm a paleta de `tema.py`.

## 3.0.0 · 2026-11-05

Revisão científica, técnica e visual. Inclui também as funcionalidades da 2.0.0, que não chegou a ser publicada no repositório.

**Indicadores**
- Diversidade lexical: **MTLD** e **HD-D** (McCarthy e Jarvis, 2010), MATTR com janela configurável. Abaixo do mínimo de palavras, os índices ficam «não aplicável» em vez de devolverem um valor enganador. As implementações coincidem com o pacote `lexical-diversity` nos testes.
- Frases: mediana, percentis 25 e 75, desvio-padrão e % de frases longas, separados da complexidade sintática.
- Complexidade sintática: profundidade da árvore de dependências, distância de dependência média (Liu, 2008) e orações subordinadas por frase.
- Classes gramaticais por 1000 palavras (12 classes UPOS, com valores absolutos), pronomes pessoais e verbos modais. A exatidão declarada do modelo spaCy fica registada.
- Legibilidade: coeficientes verificados nas fontes, Flesch–Kincaid só para inglês, aviso sobre a calibração brasileira da fórmula portuguesa. Estimativa de sílabas revista (hiatos e ditongos nasais em português, «e» mudo em francês e inglês), com a exatidão medida em listas anotadas.
- Diálogo: o `--` do Project Gutenberg passa a ser reconhecido como travessão.
- **Delta de Burrows** entre livros da mesma língua (pelo menos 3), apresentado como medida de distância estilística e não como prova de autoria.
- Matriz de correlações (Spearman) com pelo menos 5 livros.

**Qualidade e reprodutibilidade**
- Estados explícitos: válido, não aplicável, desconhecido, falha. Os valores ausentes nunca são substituídos por zero.
- Avisos de qualidade: texto vazio ou curto, erros de codificação, parágrafos duplicados, língua incerta ou divergente, segmentação suspeita.
- Parâmetros em `config/parametros.toml`. Cada resultado regista os parâmetros, as versões das bibliotecas e do modelo, e a exatidão do modelo.
- Catálogo único de indicadores (`catalogo.py`), com definição, fórmula, unidade, interpretação, limitações, comparabilidade entre línguas e referências APA 7. `docs/indicadores.md` é gerado a partir dele.

**Gráficos e relatórios**
- Identidade visual comum (`tema.py`): paleta azul-petróleo, azul-escuro e verde-acinzentado, título e subtítulo informativos, formato numérico português, PNG e SVG.
- As séries distinguem-se por cor e forma; sem gráficos circulares; comparações agrupadas por língua; rede de personagens com filtragem das ligações fracas.
- Relatórios em 13 secções, com interpretação, limitações e comentários automáticos apenas descritivos; Excel com folhas de qualidade e um dicionário de indicadores.

**Testes e workflow**
- Testes novos: valores de referência calculados à mão, comparação com a implementação de referência, sílabas, árvore de dependências construída, casos-limite, qualidade, Delta e sincronização da documentação.
- `requirements-dev.txt`; o workflow instala-o e verifica se `docs/` está sincronizado.

## 2.0.0 · 2026-11-05

- **Links como entrada:** `python -m livros_pln analisar <ficheiro ou link>` aceita links do Project Gutenberg (com recurso automático ao EPUB quando o texto não está disponível) e ligações diretas para `.txt` ou `.epub`; mostra um resumo no terminal.
- **Rede de personagens** para qualquer livro: automática (NER, com normalização de títulos, fusão de variantes do nome e exclusão de lugares) ou por dicionário (`livros/personagens/<livro>.json`); menções, ligações, intermediação, PageRank e comunidades. Dicionário de *Os Maias* incluído.
- **Painéis interativos (Plotly):** um por livro, com a rede de personagens em 3D (botão para rodar), e um de comparação entre livros, com perfil em radar.
- **Exportação para Excel:** um ficheiro por livro (uma folha por tabela) e um do corpus.
- Rede de personagens estática nos relatórios; novos indicadores: personagens, ligações e densidade da rede.
- A cache passa a considerar também o dicionário de personagens.
- 37 testes (eram 18).

## 1.0.0 · 2026-11-05

Primeira versão.

- Leitura de TXT (com metadados do Project Gutenberg) e EPUB (metadados Dublin Core); metadados manuais em `livros/metadados.csv`.
- Deteção automática de português, francês e inglês.
- Indicadores de dimensão, léxico, sintaxe, legibilidade, classes gramaticais, pontuação, entidades, frequências e evolução ao longo do livro, calculados com spaCy e pandas.
- Gráficos por livro e de comparação entre livros; relatórios em Markdown.
- Cache por livro e por versão do código.
- Workflow do GitHub Actions que testa, reprocessa e publica os resultados quando o código muda.
