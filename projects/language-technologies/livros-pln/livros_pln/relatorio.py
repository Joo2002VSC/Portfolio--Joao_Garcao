"""Relatórios em Markdown, legíveis diretamente no GitHub.

Estrutura do relatório de cada livro: identificação; metadados e características do texto;
resumo; diversidade lexical; extensão das frases e complexidade sintática; análise
morfossintática; legibilidade; análise lexical e discursiva; evolução ao longo do texto;
sentimento; outros conceitos de PLN; visualizações; interpretação; limitações; referências. As definições vêm de `catalogo.py`.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import catalogo, qualidade
from .catalogo import INDICADORES
from .tema import num

CAMPOS_META = [("titulo", "Título"), ("autor", "Autor"), ("ano", "Ano"), ("idioma", "Idioma"), ("fonte", "Fonte")]


def _tabela(linhas: list[list], cabecalho: list[str]) -> str:
    def celula(c):
        return str(c).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(cabecalho) + " |", "| " + " | ".join("---" for _ in cabecalho) + " |"]
    out += ["| " + " | ".join(celula(c) for c in l) + " |" for l in linhas]
    return "\n".join(out)


def _valor(r: dict, chave: str) -> str:
    estado = r.get("estados", {}).get(chave)
    if estado:
        return f"*{qualidade.ROTULOS[estado['estado']]}* ({estado['motivo']})"
    v = r["indicadores"].get(chave)
    return num(v, INDICADORES[chave].casas) if chave in INDICADORES else str(v)


def _bloco(r: dict, chaves: list[str]) -> str:
    linhas = [[f"**{INDICADORES[k].nome}**", _valor(r, k), INDICADORES[k].unidade, INDICADORES[k].interpretacao]
              for k in chaves if k in INDICADORES and (k in r["indicadores"] or k in r.get("estados", {}))]
    return _tabela(linhas, ["Indicador", "Valor", "Unidade / escala", "Interpretação"])


def _definicoes(chaves: list[str]) -> str:
    itens = []
    for k in chaves:
        i = INDICADORES[k]
        itens.append(f"- **{i.nome}**: {i.definicao}" + (f" Fórmula: `{i.formula}`." if i.formula else ""))
    return "<details><summary>Definições</summary>\n\n" + "\n".join(itens) + "\n\n</details>"


def _figura(r: dict, nome: str, alt: str) -> list[str]:
    if f"{nome}.png" in r["graficos"]:
        return [f"![{alt}](graficos/{nome}.png)", f"<sub>[SVG](graficos/{nome}.svg)</sub>", ""]
    return []


# ---------------------------------------------------------------------------
# Comentários automáticos (descritivos, sem inferências causais)
# ---------------------------------------------------------------------------

def comentarios(r: dict, evol: pd.DataFrame) -> list[str]:
    i, e = r["indicadores"], r.get("estados", {})
    c = []
    if "frase_mediana" not in e and i.get("frase_mediana") is not None:
        c.append(f"Metade das frases tem até {num(i['frase_mediana'], 0)} palavras e a metade central das frases está entre "
                 f"{num(i['frase_p25'], 0)} e {num(i['frase_p75'], 0)} palavras; {num(i['frases_longas_pct'], 1)} % "
                 f"têm mais de {r['parametros']['frase_longa']} palavras.")
        if i.get("frase_desvio_padrao") and i.get("frase_media") and i["frase_desvio_padrao"] / i["frase_media"] > 0.9:
            c.append("A extensão das frases varia muito (desvio-padrão próximo da média): alternância marcada entre "
                     "frases curtas e longas.")
        if i["frase_media"] - i["frase_mediana"] > 3:
            c.append(f"A média ({num(i['frase_media'], 1)}) é bastante superior à mediana: algumas frases muito longas "
                     "puxam a média para cima, por isso a mediana descreve melhor a frase típica.")
    if "mtld" not in e and i.get("mtld") is not None:
        c.append(f"Diversidade lexical: MTLD de {num(i['mtld'], 1)} palavras por fator, ou seja, em média são "
                 f"precisas cerca de {num(i['mtld'], 0)} palavras até o TTR descer abaixo de 0,72. Este valor só é "
                 f"comparável com livros em {r['lingua_nome']}.")
    if i.get("dialogo_pct") is not None:
        c.append(f"Cerca de {num(i['dialogo_pct'], 0)} % dos parágrafos foram identificados como diálogo "
                 "(estimativa tipográfica).")
    if i.get("subordinadas_por_frase") is not None:
        c.append(f"Em média, {num(i['subordinadas_por_frase'], 2)} orações subordinadas por frase e uma profundidade "
                 f"sintática média de {num(i['profundidade_media'], 2)} níveis.")
    if len(evol) >= 3 and evol.mtld.notna().sum() >= 3:
        a, b = evol.mtld.dropna().iloc[0], evol.mtld.dropna().iloc[-1]
        fa, fb = evol.frase_media.iloc[0], evol.frase_media.iloc[-1]
        c.append(f"Do primeiro ao último segmento, o MTLD passa de {num(a, 1)} para {num(b, 1)} e a extensão média "
                 f"das frases de {num(fa, 1)} para {num(fb, 1)} palavras (variação descritiva; segmentos isolados são "
                 "instáveis).")
    if i.get("legibilidade_leitura") and "legibilidade" not in e:
        nivel = f", adequada ao {i['legibilidade_nivel']} segundo Martins et al. (1996)" if i.get("legibilidade_nivel") else ""
        c.append(f"Pelo índice de Flesch adaptado ({num(i['legibilidade'], 0)}, «{i['legibilidade_escala']}»), a leitura "
                 f"classifica-se como **{i['legibilidade_leitura']}**{nivel}. O índice só considera a extensão das "
                 "frases e das palavras: vocabulário antigo, ironia ou referências culturais não entram no cálculo.")
    if i.get("sentimento_medio") is not None and "sentimento_medio" not in e:
        tom = "positivo" if i["sentimento_medio"] >= 0.05 else "negativo" if i["sentimento_medio"] <= -0.05 else "neutro"
        c.append(f"Sentimento: média de {num(i['sentimento_medio'], 3)} (vocabulário globalmente {tom}); "
                 f"{num(i['frases_positivas_pct'], 0)} % das frases pontuadas são positivas e "
                 f"{num(i['frases_negativas_pct'], 0)} % negativas. Só {num(i['cobertura_lexico_pct'], 1)} % das "
                 "palavras existem no léxico, por isso estes valores devem ser lidos com cautela.")
        if len(evol) >= 3 and "sentimento" in evol and evol.sentimento.notna().sum() >= 3:
            baixo, alto = evol.loc[evol.sentimento.idxmin()], evol.loc[evol.sentimento.idxmax()]
            c.append(f"No arco de sentimento, o segmento mais negativo é o {int(baixo.segmento)} "
                     f"({num(baixo.sentimento, 3)}) e o mais positivo o {int(alto.segmento)} ({num(alto.sentimento, 3)}).")
    if i.get("verbos_passado_pct") is not None and "verbos_passado_pct" not in e:
        c.append(f"{num(i['verbos_passado_pct'], 0)} % das formas verbais finitas estão no passado e "
                 f"{num(i['verbos_presente_pct'], 0)} % no presente.")
    if i.get("personagens_na_rede"):
        c.append(f"A rede inclui {i['personagens_na_rede']} personagens; a mais central (PageRank) é "
                 f"{i.get('personagem_principal')}.")
    return c


# ---------------------------------------------------------------------------
# Relatório de um livro
# ---------------------------------------------------------------------------

def livro(r: dict, freq: pd.DataFrame, classes: pd.DataFrame, ents: pd.DataFrame, evol: pd.DataFrame,
          pers: pd.DataFrame, pasta: Path, extra: dict | None = None):
    extra = extra or {}
    i, m, p, amb = r["indicadores"], r["metadados"], r["processamento"], r.get("ambiente", {})
    lg = r["lingua"]
    s = [f"# {r['titulo']}", ""]
    if r.get("autor"):
        s += [f"**{r['autor']}**" + (f" · {r['ano']}" if r.get("ano") else ""), ""]
    s += ["[← Todos os livros](../../README.md) · **[Painel interativo](painel.html)** (rede de personagens em 3D) · "
          f"[Excel]({r['id']}.xlsx) · [JSON](indicadores.json)", ""]

    # 1–2. Identificação e metadados
    s += ["## 1. Identificação e metadados", ""]
    meta = [[rot, m.get(k) or "*desconhecido*"] for k, rot in CAMPOS_META]
    s += [_tabela(meta, ["Campo", "Valor"]), "",
          f"<sub>Ficheiro `{r['ficheiro']}` · modelo linguístico `{r['modelo_spacy']}`"
          + (f" {amb['modelo']['versao']}" if amb else "") + "</sub>", ""]
    dim = ["palavras", "frases", "paragrafos", "tempo_leitura_horas"]
    if r.get("forma") == "verso":
        dim += ["versos", "estrofes", "versos_por_estrofe"]
    s += ["## 2. Características do texto", "", f"Forma: **{r.get('forma', 'prosa')}**.", "", _bloco(r, dim), ""]
    if r.get("qualidade"):
        s += ["**Avisos de qualidade dos dados**", ""] + [f"- ⚠ {a['mensagem']}" for a in r["qualidade"]] + [""]
    else:
        s += ["Sem avisos de qualidade: texto não vazio, sem sinais de erro de codificação nem de duplicação, "
              "língua detetada com margem confortável e segmentação de frases sem anomalias.", ""]

    # 3. Resumo
    destaque = [("mtld", "Diversidade lexical (MTLD)"), ("frase_mediana", "Extensão mediana das frases"),
                ("profundidade_media", "Profundidade sintática"), ("densidade_lexical_pct", "Densidade lexical"),
                ("dialogo_pct", "Parágrafos de diálogo"), ("legibilidade", "Legibilidade (Flesch adaptado)")]
    s += ["## 3. Resumo dos principais resultados", "",
          _tabela([[rot, _valor(r, k), INDICADORES[k].unidade] for k, rot in destaque], ["Indicador", "Valor", "Unidade"]),
          ""]

    # 4. Diversidade lexical
    lex = ["mtld", "hdd", "mattr", "yule_k", "ttr", "hapax_pct", "vocabulario"]
    s += ["## 4. Diversidade lexical", "",
          "O TTR depende da extensão do texto e não deve ser usado sozinho para comparar livros de tamanhos diferentes; "
          "o MTLD e o HD-D são os índices de referência (McCarthy e Jarvis, 2010). Todos dependem da língua.", "",
          _bloco(r, lex), "", _definicoes(lex), ""]

    # 5. Frases e sintaxe
    ext = ["frase_mediana", "frase_media", "frase_p25", "frase_p75", "frase_desvio_padrao", "frase_maxima",
           "frases_longas_pct", "paragrafo_medio"]
    sint = ["profundidade_media", "distancia_dependencia", "subordinadas_por_frase"]
    s += ["## 5. Extensão das frases e complexidade sintática", "",
          "A extensão mede quantas palavras tem uma frase; a complexidade sintática mede como essas palavras se "
          "organizam (encaixamento, distância entre palavras relacionadas, subordinação). São dimensões distintas.", "",
          "### Extensão", "", _bloco(r, ext), ""] + _figura(r, "extensao-frases", "Extensão das frases")
    s += ["### Complexidade sintática", "",
          f"Calculada a partir da árvore de dependências do modelo `{r['modelo_spacy']}`"
          + (f" (exatidão declarada pelo modelo: LAS {num(amb['modelo']['exatidao'].get('dependencias_las', float('nan')), 2)})"
             if amb and amb["modelo"].get("exatidao", {}).get("dependencias_las") is not None else "")
          + ".", "", _bloco(r, sint), "", _definicoes(sint), ""]

    # 6. Morfossintaxe
    s += ["## 6. Análise morfossintática", "",
          f"Etiquetas UPOS do modelo `{r['modelo_spacy']}`"
          + (f" (exatidão declarada: {num(100 * amb['modelo']['exatidao']['pos'], 1)} %)"
             if amb and amb["modelo"].get("exatidao", {}).get("pos") is not None else "")
          + ". A exatidão é medida pelo próprio modelo em textos contemporâneos; em textos antigos será mais baixa.", "",
          _tabela([[c.nome, num(c.ocorrencias, 0), num(c.por_1000_palavras, 1)] for c in
                   classes.sort_values("por_1000_palavras", ascending=False).itertuples()],
                  ["Classe", "Ocorrências", "Por 1000 palavras"]), "",
          _bloco(r, ["densidade_lexical_pct", "pronomes_pessoais_por_1000", "modais_por_1000", "palavra_media_letras"]),
          ""] + _figura(r, "classes-gramaticais", "Classes gramaticais")

    # 7. Legibilidade
    s += ["## 7. Legibilidade", ""]
    if i.get("legibilidade_leitura") and "legibilidade" not in r.get("estados", {}):
        nivel = f" · nível escolar indicativo: {i['legibilidade_nivel']}" if i.get("legibilidade_nivel") else ""
        s += [f"**Leitura {i['legibilidade_leitura']}** · índice {num(i['legibilidade'], 1)} · faixa "
              f"«{i['legibilidade_escala']}»{nivel}", ""]
    s += [_bloco(r, ["legibilidade", "flesch_kincaid", "silabas_por_palavra"]), ""]
    aviso_lg = {"pt": "A fórmula usada é a adaptação de Martins et al. (1996), calibrada com manuais escolares em "
                      "português do Brasil. Não foi validada para o português europeu nem para prosa literária: o "
                      "valor serve para comparar livros em português entre si, não como medida absoluta.",
                "fr": "A fórmula usada é a adaptação de Kandel e Moles (1958); não é equivalente às de outras línguas.",
                "en": "Fórmulas originais de Flesch (1948) e Kincaid et al. (1975), calibradas para inglês."}[lg]
    s += [f"> {aviso_lg} As sílabas são estimadas por regras ortográficas (ver a exatidão medida em "
          "`docs/indicadores.md`).", "", _definicoes(["legibilidade", "silabas_por_palavra"]), ""]

    # 8. Lexical e discursiva
    pont = [k for k in INDICADORES if k.endswith("_por_1000") and INDICADORES[k].grupo == "Pontuação"]
    s += ["## 8. Análise lexical e discursiva", "", "### Palavras de conteúdo mais frequentes", ""]
    s += _figura(r, "frequencias", "Frequências")
    s += [_tabela([[l.lema, l.pos, num(l.ocorrencias, 0), num(l.por_1000_palavras, 2)] for l in freq.head(20).itertuples()],
                  ["Lema", "Classe", "Ocorrências", "Por 1000 palavras"]), ""]
    s += ["### Pontuação e diálogo", "", _bloco(r, pont + ["dialogo_pct"]), ""]
    s += ["### Entidades nomeadas", "", "Reconhecimento automático (NER): estimativas sujeitas a erro.", "",
          _bloco(r, ["entidades_pessoa", "entidades_lugar", "entidades_organizacao", "entidades_por_1000"]), ""]
    s += _figura(r, "entidades", "Entidades")
    if not pers.empty:
        s += ["### Rede de personagens", "", f"Identificação: {r.get('metodo_personagens')}. Duas personagens ligam-se "
              "quando aparecem no mesmo parágrafo: é uma co-ocorrência textual, não uma relação narrativa comprovada.", ""]
        s += _figura(r, "rede", "Rede de personagens")
        s += [_tabela([[x.personagem, num(x.mencoes, 0), x.grau, num(x.grau_ponderado, 0), num(x.intermediacao, 3),
                        num(x.pagerank, 3), x.comunidade] for x in pers.head(15).itertuples()],
                      ["Personagem", "Menções", "Ligações", "Parágrafos partilhados", "Intermediação", "PageRank",
                       "Comunidade"]), ""]

    # 9. Evolução
    s += ["## 9. Evolução ao longo do texto", ""]
    if len(evol) >= 3:
        s += [f"O livro foi dividido em {len(evol)} segmentos com o mesmo número de palavras.", ""]
        s += _figura(r, "evolucao", "Evolução")
        s += [_tabela([[int(e.segmento), num(e.palavras, 0), num(e.mtld, 1), num(e.frase_media, 1),
                        num(e.densidade_lexical_pct, 1), num(e.dialogo_pct, 0), num(e.pessoas_por_1000, 1)]
                       for e in evol.itertuples()],
                      ["Segmento", "Palavras", "MTLD", "Frase média", "Densidade lexical (%)", "Diálogo (%)",
                       "Pessoas / 1000"]), ""]
    else:
        s += ["*Não aplicável*: texto curto de mais para dividir em segmentos.", ""]

    # 10. Sentimento
    sen = ["sentimento_medio", "frases_positivas_pct", "frases_negativas_pct", "frases_neutras_pct",
           "cobertura_lexico_pct"]
    s += ["## 10. Sentimento", ""]
    if r.get("metodo_sentimento"):
        s += [f"Método: {r['metodo_sentimento']}, com léxico e regras (Hutto e Gilbert, 2014). Cada frase com pelo menos "
              f"{r['parametros']['sentimento_minimo_palavras']} palavras recebe uma pontuação entre −1 e +1. Os léxicos "
              "foram criados para mensagens curtas das redes sociais: os valores descrevem a polaridade do vocabulário, "
              "não o tom da narrativa, e não foram validados com anotação humana neste projeto.", ""]
    s += [_bloco(r, sen), ""] + _figura(r, "sentimento", "Arco de sentimento")
    ext_s = extra.get("extremos")
    if ext_s is not None and len(ext_s):
        s += ["**Frases com pontuação mais extrema** (entre 8 e 60 palavras)", "",
              _tabela([[x.polaridade, num(x.sentimento, 3), x.texto] for x in ext_s.itertuples()],
                      ["Polaridade", "Compound", "Frase"]), ""]
    s += [_definicoes(sen), ""]

    # 10.1 Tonalidade e emoções; 10.2 Género literário
    t = r.get("tonalidade") or {}
    tom_k = [k for k, x in INDICADORES.items() if x.grupo == "Tonalidade emocional"]
    emo_k = [k for k, x in INDICADORES.items() if x.grupo == "Emoções"]
    s += ["### Tonalidade emocional (experimental)", "",
          f"**{t.get('rotulo', 'Indeterminado')}**. " + " ".join(x[:1].upper() + x[1:] + "." for x in t.get("razoes", [])), "",
          "Classificação interpretativa: polaridade por frase do método de sentimento, média por capítulo e intervalo de "
          "confiança a 95 % por bootstrap dos capítulos. Positivo/negativo: intervalo inteiro acima de +0,05 / abaixo de "
          "−0,05; misto: pelo menos 10 % de frases fortemente positivas e 10 % fortemente negativas; neutro: intervalo "
          "entre −0,05 e +0,05; indeterminado nos restantes casos. Não validada com anotação humana.", "",
          _bloco(r, tom_k), ""]
    em = r.get("emocoes") or {}
    s += ["### Emoções (léxico NRC, modelo de Plutchik)", ""]
    if em.get("estado") == "valido":
        s += [f"Léxico: {r.get('metodo_emocoes')}. Emoção mais frequente: **{em.get('dominante') or '—'}**. Por "
              "capítulo, por fase (início, desenvolvimento, conclusão) e por canal (narração e discurso direto): "
              "[`emocoes-por-capitulo.csv`](emocoes-por-capitulo.csv), [`emocoes-por-fase.csv`](emocoes-por-fase.csv), "
              "[`emocoes-narracao-dialogo.csv`](emocoes-narracao-dialogo.csv).", "", _bloco(r, emo_k), ""]
    else:
        s += [f"Não calculadas: {em.get('motivo') or 'sem dados'}.", ""]
    g = r.get("genero") or {}
    if g:
        bib = g.get("bibliografico") or {}
        s += ["### Género literário inferido (exploratório)", "",
              f"Forma: **{g.get('forma_principal') or '—'}**. Género inferido: **{g.get('principal') or 'sem categoria clara'}**"
              + (f". Género bibliográfico ({bib.get('estado')}): **{bib.get('genero')}** — fonte: {bib.get('fonte')}"
                 if bib.get("genero") else "") + ".", ""]
        s += [f"- {x}" for x in g.get("tracos", [])] + [""]
        linhas = [[c["nome"], num(c["pontuacao"], 2), "; ".join(("✓ " if x["cumprido"] else "✗ " if x["cumprido"] is False
                                                                 else "– ") + x["criterio"] for x in c["criterios"])]
                  for c in g.get("formas", []) + g.get("generos", []) if c["pontuacao"]]
        s += [_tabela(linhas, ["Categoria", "Pontuação de regras", "Critérios"]), "",
              "Regras transparentes sobre indicadores do texto; a pontuação é a fração dos critérios cumpridos (0 se "
              "falhar um critério essencial), não uma probabilidade. Limiares de extensão: regras dos prémios Nebula "
              "(SFWA). O género bibliográfico não entra no cálculo.", ""]

    # 11. Outros conceitos de PLN
    s += ["## 11. Outros conceitos de PLN", "", "### Tipos de frase", "",
          _bloco(r, ["frases_interrogativas_pct", "frases_exclamativas_pct"]), ""]
    morf = ["verbos_passado_pct", "verbos_presente_pct", "verbos_futuro_pct", "verbos_conjuntivo_pct",
            "pronomes_1a_pessoa_por_1000", "pronomes_2a_pessoa_por_1000", "pronomes_3a_pessoa_por_1000"]
    s += ["### Tempos verbais e pessoa gramatical", "", _bloco(r, morf), ""]
    tempos = extra.get("tempos")
    if tempos is not None and len(tempos):
        s += [_tabela([[t.tempo, t.modo, num(t.ocorrencias, 0), num(t.pct, 1)] for t in tempos.head(12).itertuples()],
                      ["Tempo", "Modo", "Ocorrências", "% das formas finitas"]), ""]
    zh = ["zipf_expoente", "zipf_r2", "heaps_beta", "heaps_k", "heaps_r2"]
    s += ["### Leis de Zipf e de Heaps", "", "Duas regularidades estatísticas do vocabulário: poucas palavras são muito "
          "frequentes e muitas são raras (Zipf); o vocabulário cresce cada vez mais devagar à medida que o texto avança "
          "(Heaps).", "", _bloco(r, zh), ""] + _figura(r, "zipf-heaps", "Leis de Zipf e de Heaps") + [_definicoes(zh), ""]
    col = extra.get("colocacoes")
    if col is not None and len(col):
        s += ["### Colocações", "", f"{catalogo.METODOS['colocacoes'].definicao} Ordenadas pela razão de verosimilhança "
              "G² (Dunning, 1993); o PMI (Church e Hanks, 1990) mede a exclusividade da associação.", "",
              _tabela([[c.colocacao, num(c.ocorrencias, 0), num(c.g2, 1), num(c.pmi, 2)] for c in col.head(20).itertuples()],
                      ["Colocação", "Ocorrências", "G²", "PMI"]), ""]
    chave = extra.get("palavras_chave")
    if chave is not None and len(chave):
        s += ["### Palavras-chave por segmento", "", f"{catalogo.METODOS['palavras_chave'].definicao} Medida: TF-IDF "
              "(Spärck Jones, 1972), com os segmentos como documentos.", "",
              _tabela([[seg, ", ".join(g.lema)] for seg, g in chave.groupby("segmento")], ["Segmento", "Palavras-chave"]),
              ""]

    # 12. Visualizações
    s += ["## 12. Visualizações", "", "- [Painel interativo](painel.html): gráficos em 3D (com alternativa em 2D) da rede de "
          "personagens, centralidade, vocabulário, classes gramaticais, frases, sentimento, evolução, colocações, "
          "palavras-chave, tempos verbais e lugares (abrir num navegador).",
          "- Gráficos estáticos em PNG e SVG na pasta [`graficos/`](graficos/).", ""]

    # 11. Interpretação
    s += ["## 13. Interpretação", "", "Comentários gerados automaticamente a partir dos valores; descrevem o texto, "
          "não explicam as suas causas nem substituem a leitura crítica.", ""]
    s += [f"- {c}" for c in comentarios(r, evol)] + [""]

    # 12. Limitações
    usados = [k for k, x in INDICADORES.items() if x.grupo in ("Tonalidade emocional", "Emoções")] + \
        lex + ext + sint + ["legibilidade", "dialogo_pct", "entidades_pessoa", "densidade_lexical_pct"] + sen + \
        morf + zh + ["colocacoes", "palavras_chave", "arco_sentimento"]
    todos = {**INDICADORES, **catalogo.METODOS}
    s += ["## 14. Limitações metodológicas", ""]
    s += [f"- **{todos[k].nome}**: {todos[k].limitacoes}" for k in dict.fromkeys(usados) if todos[k].limitacoes]
    s += ["- **Modelos linguísticos**: os modelos spaCy foram treinados com texto contemporâneo; grafias antigas, "
          "diálogos e pontuação literária reduzem a exatidão da segmentação, da etiquetagem e da análise sintática.", ""]

    # 13. Referências
    s += ["## 15. Referências metodológicas", ""] + [f"- {x}" for x in catalogo.referencias_de(usados)] + \
         [f"- {catalogo.REFERENCIAS['honnibal2020']}", ""]
    bib = amb.get("bibliotecas", {}) if amb else {}
    s += [f"<sub>Processado em {p['data']} · livros_pln {p['versao']} · código `{p['versao_codigo']}`"
          + (f" · commit `{p['commit']}`" if p.get("commit") else "")
          + (f" · Python {amb['python']} · spaCy {bib.get('spacy')} · {amb['modelo']['nome']} {amb['modelo']['versao']}"
             if amb else "") + "</sub>", ""]
    (pasta / "README.md").write_text("\n".join(s), encoding="utf-8")


# ---------------------------------------------------------------------------
# Relatório do corpus
# ---------------------------------------------------------------------------

def corpus(t: pd.DataFrame, figs: list[str], resultado_delta: dict, saida: Path, versao: str, codigo: str):
    s = ["# Resultados", "",
         f"Gerado automaticamente por livros_pln {versao} (código `{codigo}`). Não editar à mão: estes ficheiros são "
         "reescritos sempre que o código ou os parâmetros mudam. A data, o commit e as versões dos modelos de cada "
         "livro estão no respetivo relatório.", ""]
    if t.empty:
        (saida / "README.md").write_text("\n".join(s + ["Ainda não há livros processados.", ""]), encoding="utf-8")
        return
    nomes = {"pt": "português", "fr": "francês", "en": "inglês"}
    s += [f"**{len(t)} livros · {num(int(t.palavras.sum()), 0)} palavras** · "
          + ", ".join(f"{n} em {nomes.get(lg, lg)}" for lg, n in t.lingua.value_counts().items()), "",
          "**[Painel interativo de comparação](painel.html)** · [`indicadores.csv`](indicadores.csv) · "
          "[`indicadores.xlsx`](indicadores.xlsx) (uma linha por livro; o Excel inclui o dicionário de indicadores)", ""]
    s += ["## Livros", "", "Os livros estão agrupados por língua: a maior parte dos indicadores só é comparável dentro "
          "da mesma língua (ver a coluna «comparável entre línguas» no dicionário de indicadores).", ""]
    for lg, sub in t.sort_values(["lingua", "titulo"]).groupby("lingua"):
        s += [f"### {nomes.get(lg, lg).capitalize()}", ""]
        s += [_tabela([[f"[{x.titulo}](livros/{x.id}/README.md)", x.autor or "—", x.ano or "—", num(x.palavras, 0),
                        num(x.mtld, 1), num(x.frase_mediana, 0), num(x.profundidade_media, 2),
                        num(x.densidade_lexical_pct, 1), num(x.legibilidade, 0)] for x in sub.itertuples()],
                      ["Livro", "Autor", "Ano", "Palavras", "MTLD", "Frase mediana", "Profundidade",
                       "Densidade lexical (%)", "Legibilidade"]), ""]
        if len(sub) >= 2:
            maior = sub.loc[sub.mtld.idxmax()] if sub.mtld.notna().any() else None
            if maior is not None:
                s += [f"Entre os livros em {nomes.get(lg, lg)}, o MTLD mais alto é o de *{maior.titulo}* "
                      f"({num(maior.mtld, 1)}).", ""]
    s += ["## Comparações", ""]
    rotulos = {"perfil-comparativo.png": "Perfil linguístico", "classes-comparadas.png": "Classes gramaticais",
               "frases-comparadas.png": "Extensão das frases", "evolucao-comparada.png": "Evolução",
               "correlacoes.png": "Correlações"}
    for g in figs:
        if g.startswith("delta-"):
            continue
        s += [f"![{rotulos.get(g, g)}](graficos/{g})", f"<sub>[SVG](graficos/{g[:-4]}.svg)</sub>", ""]
    if "correlacoes.png" not in figs:
        s += [f"*Matriz de correlação entre indicadores: não aplicável* ({len(t)} livros; são precisos pelo menos 5 "
              "para que as correlações tenham algum significado).", ""]
    s += ["## Estilometria (Delta de Burrows)", "",
          "Distância estilística a partir da frequência das palavras mais frequentes (sobretudo palavras gramaticais), "
          "calculada só entre livros da mesma língua. Uma distância pequena indica semelhança no uso dessas palavras; "
          "não é prova de autoria.", ""]
    for lg, r in resultado_delta.items():
        if r["estado"] == "valido":
            s += [f"### {nomes.get(lg, lg).capitalize()}", "", f"{r['motivo']}. Matriz: [`delta-{lg}.csv`](delta-{lg}.csv).",
                  "", f"![Delta de Burrows](graficos/delta-{lg}.png)", ""]
        else:
            s += [f"- **{nomes.get(lg, lg).capitalize()}**: *não aplicável* ({r['motivo']}).", ""]
    s += ["## Referências", "", f"- {catalogo.REFERENCIAS['burrows2002']}", f"- {catalogo.REFERENCIAS['evert2017']}",
          f"- {catalogo.REFERENCIAS['mccarthy2010']}", ""]
    (saida / "README.md").write_text("\n".join(s), encoding="utf-8")
