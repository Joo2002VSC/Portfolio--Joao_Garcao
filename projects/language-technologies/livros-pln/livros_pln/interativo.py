"""Painéis interativos em HTML (Plotly): um por livro, com a rede de personagens em 3D, e um do corpus."""
from __future__ import annotations

import html
import math
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from .catalogo import CLASSES, NOMES_CLASSES

from . import graficos3d as g3d
from . import tema

# Paleta dos painéis HTML: papel bege, tinta quase preta e castanhos (os gráficos estáticos usam tema.py).
TINTA = "#1E1915"          # quase preto, castanho muito escuro
SUAVE = "#6E5E4E"          # texto secundário
FUNDO = "#FBF8F2"          # fundo dos cartões e gráficos
GRELHA = "#E2D6C2"
CASTANHO = "#7A4E2D"
OCRE = "#B8893E"
CAQUI = "#8A8466"
FERRUGEM = "#A0583A"
AREIA = "#D9C7A3"
SEPIA = "#5C4A3A"
AZUL, VERMELHO, VERDE, OURO = CASTANHO, FERRUGEM, CAQUI, OCRE
COMUNIDADES = [CASTANHO, TINTA, OCRE, CAQUI, FERRUGEM, "#A89270", SEPIA, "#C9A66B"]
# forma do marcador por comunidade, para não depender só da cor
SIMBOLOS_3D = ["circle", "square", "diamond", "cross", "circle-open", "square-open", "diamond-open", "x"]
CORES_CLASSES = {"NOUN": CASTANHO, "VERB": TINTA, "ADJ": OCRE, "ADV": CAQUI}
CORES_LINGUA = {"pt": CASTANHO, "fr": TINTA, "en": OCRE}
SIMBOLOS_LINGUA = {"pt": "circle", "fr": "square", "en": "triangle-up"}
FONTE = "Source Sans 3, Helvetica Neue, Arial, sans-serif"
FONTE_TITULOS = "Cormorant Garamond, Georgia, Times New Roman, serif"
PAPEL = "#F4EEE3"
REPOSITORIO = "https://github.com/Joo2002VSC/livros-pln"
RECURSOS = Path(__file__).parent / "recursos"


MENORES = {"a", "o", "as", "os", "e", "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas", "por", "para",
           "com", "ao", "à", "aos", "às", "um", "uma", "ou", "que", "até", "sem", "entre", "pelo", "pela"}


def maiusculas(texto: str) -> str:
    """Cada palavra começa por maiúscula, exceto artigos, preposições e conjunções curtas a meio do texto.

    Só se altera a primeira letra: siglas e nomes como «MTLD», «PageRank» ou «UPOS» ficam como estão."""
    palavras = texto.split(" ")
    saida = []
    for k, p in enumerate(palavras):
        inicio = k == 0 or (saida and saida[-1].endswith((":", "·", "—", ";")))
        letras = [ch for ch in p if ch.isalpha()]
        if not inicio and (p.lower() in MENORES or len(letras) == 1):
            saida.append(p if len(letras) == 1 else p.lower())
            continue
        for j, ch in enumerate(p):
            if ch.isalpha():
                p = p[:j] + ch.upper() + p[j + 1:]
                break
        saida.append(p)
    return " ".join(saida)


def _layout(fig: go.Figure, titulo: str, altura: int = 420, nota: str = "", topo: int = 12, **extra) -> go.Figure:
    """Aplica o tema. O título e o subtítulo («Título<br><sup>Subtítulo</sup>») são escritos no HTML, não no gráfico."""
    principal, _, resto = titulo.partition("<br>")
    subtitulo = resto.replace("<sup>", "").replace("</sup>", "")
    fig.update_layout(meta=dict(titulo=maiusculas(principal), subtitulo=maiusculas(subtitulo) if subtitulo else "",
                                nota=nota),
                      font=dict(family=FONTE, color=TINTA, size=13), paper_bgcolor=PAPEL, plot_bgcolor=PAPEL,
                      margin=dict(l=8, r=8, t=topo, b=8), height=altura,
                      hoverlabel=dict(font_family=FONTE, bgcolor=TINTA, font_color="#F3EADB", bordercolor=TINTA),
                      separators=", ", **extra)  # vírgula decimal e espaço como separador de milhares
    fig.update_xaxes(gridcolor=GRELHA, zeroline=False, linecolor=SUAVE, tickfont=dict(color=SUAVE),
                     title_font=dict(color=SUAVE))
    fig.update_yaxes(gridcolor=GRELHA, zeroline=False, linecolor=GRELHA, tickfont=dict(color=SUAVE),
                     title_font=dict(color=SUAVE), automargin=True)
    # barras horizontais: margem esquerda à medida dos rótulos, para não cortar nomes compridos
    rotulos = [str(y) for t in fig.data if getattr(t, "orientation", None) == "h" and t.y is not None for y in t.y]
    if rotulos:
        fig.update_layout(margin=dict(l=int(7.4 * max(map(len, rotulos))) + 18))
    return fig


# ---------------------------------------------------------------------------
# Rede 3D
# ---------------------------------------------------------------------------

def rede_3d(g: nx.Graph, titulo: str = "Rede de personagens em 3D") -> go.Figure | None:
    if g.number_of_nodes() < 2:
        return None
    # Kamada-Kawai em 3D com distâncias logarítmicas: as ligações fortes aproximam os nós sem os colapsar no centro
    h = nx.Graph()
    h.add_weighted_edges_from([(a, b, 1 / math.log1p(d["peso"]) + 0.6) for a, b, d in g.edges(data=True)], weight="w")
    try:
        pos = nx.kamada_kawai_layout(g, dist=dict(nx.all_pairs_dijkstra_path_length(h, weight="w")), dim=3)
    except Exception:
        pos = nx.spring_layout(g, dim=3, seed=7)
    pesos = np.array([d["peso"] for _, _, d in g.edges(data=True)])
    limites = np.quantile(pesos, [0.6, 0.9]) if len(pesos) > 2 else [pesos.max(), pesos.max()]
    traces = []
    for nivel, (minimo, maximo, largura, opacidade) in enumerate([(0, limites[0], 1.2, 0.18),
                                                                  (limites[0], limites[1], 2.8, 0.35),
                                                                  (limites[1], math.inf, 5.5, 0.6)]):
        xs, ys, zs = [], [], []
        for a, b, d in g.edges(data=True):
            if (minimo < d["peso"] <= maximo) or (nivel == 0 and d["peso"] <= minimo):
                for v in (pos[a], pos[b], (None, None, None)):
                    xs.append(v[0]), ys.append(v[1]), zs.append(v[2])
        if xs:
            traces.append(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", hoverinfo="skip", showlegend=False,
                                       line=dict(color=f"rgba(110,80,55,{opacidade + 0.05})", width=largura)))
    maximo = max(d["mencoes"] for _, d in g.nodes(data=True))
    for com in sorted({d.get("comunidade", 1) for _, d in g.nodes(data=True)}):
        nos = [n for n, d in g.nodes(data=True) if d.get("comunidade", 1) == com]
        traces.append(go.Scatter3d(
            x=[pos[n][0] for n in nos], y=[pos[n][1] for n in nos], z=[pos[n][2] for n in nos],
            mode="markers+text", name=f"Comunidade {com}", text=nos, textposition="top center",
            textfont=dict(size=13, color=TINTA, family=FONTE),
            marker=dict(size=[11 + 38 * math.sqrt(g.nodes[n]["mencoes"] / maximo) for n in nos],
                        color=COMUNIDADES[(com - 1) % len(COMUNIDADES)], opacity=0.93,
                        symbol=SIMBOLOS_3D[(com - 1) % len(SIMBOLOS_3D)],
                        line=dict(color=PAPEL, width=1.5)),
            customdata=[[g.nodes[n]["mencoes"], g.degree(n), g.degree(n, weight="peso")] for n in nos],
            hovertemplate="<b>%{text}</b><br>Menções: %{customdata[0]}<br>Ligações: %{customdata[1]}"
                          "<br>Parágrafos partilhados: %{customdata[2]}<extra></extra>"))
    eixo = dict(visible=False, showbackground=False, showspikes=False)
    fig = go.Figure(traces)
    # sem animação nem rotação automática: é o leitor que roda a rede com o rato ou o dedo
    _layout(fig, titulo + "<br><sup>Tamanho = número de menções; cor e forma = comunidade</sup>", altura=760,
            nota="Arraste para rodar · use a roda do rato para aproximar · duplo clique repõe a vista.",
            scene=dict(xaxis=eixo, yaxis=eixo, zaxis=eixo, bgcolor=PAPEL, aspectmode="cube", dragmode="orbit",
                       camera=dict(eye=dict(x=1.15, y=1.15, z=0.7))),
            legend=dict(orientation="h", y=0.02, x=0, font=dict(size=13)))
    return fig


# ---------------------------------------------------------------------------
# Gráficos por livro, agrupados em secções
# ---------------------------------------------------------------------------

SECCOES = {
    "personagens": ("Personagens", "Rede de co-ocorrência: duas personagens ligam-se quando surgem no mesmo parágrafo. "
                                   "É uma relação textual, não uma relação narrativa comprovada."),
    "vocabulario": ("Vocabulário", "Que palavras dominam o livro, que pares de palavras aparecem juntos mais do que o "
                                   "acaso faria prever (colocações) e que palavras caracterizam cada parte do texto "
                                   "(palavras-chave por TF-IDF)."),
    "gramatica": ("Gramática", "Etiquetagem morfossintática: classes de palavras, tempos e modos verbais, pessoa "
                               "gramatical e tipos de frase, segundo o modelo linguístico spaCy."),
    "frases": ("Frases e evolução", "Como se distribui a extensão das frases em cada parte do livro e como vários "
                                    "indicadores variam do início ao fim."),
    "sentimento": ("Sentimento", "Análise de sentimento por frase com léxico e regras (VADER e adaptações): cada frase "
                                 "recebe uma pontuação entre −1 (negativa) e +1 (positiva). Mede a polaridade do "
                                 "vocabulário, não o tom narrativo nem a ironia."),
    "leis": ("Leis do vocabulário", "Duas regularidades estatísticas de quase todos os textos: poucas palavras são "
                                    "muito frequentes e muitas são raras (lei de Zipf), e o vocabulário cresce cada vez "
                                    "mais devagar à medida que se lê (lei de Heaps)."),
    "lugares": ("Lugares", "Espaços nomeados, identificados automaticamente pelo reconhecimento de entidades; contam "
                           "como estimativa."),
}
NOTA_3D = "Arraste para rodar · roda do rato para aproximar · duplo clique repõe a vista · valores exatos ao passar o rato."


def _item(seccao: str, fig, alt=None, largo: bool = True) -> dict:
    return {"seccao": seccao, "fig": fig, "alt": alt, "largo": largo}


def _fmt(v, casas=1) -> str:
    return tema.num(v, casas)


def figuras_livro(freq, classes, comprimentos, evol, ents, pers, g, extra: dict | None = None,
                  lingua: str = "pt") -> list[dict]:
    extra = extra or {}
    itens: list[dict] = []

    # Personagens ---------------------------------------------------------------------------------------------------
    f3d = rede_3d(g)
    if f3d is not None:
        itens.append(_item("personagens", f3d))
    if not pers.empty:
        top = pers.head(15)
        com = [f"Comunidade {c}" for c in top.comunidade]
        f3 = g3d.barras_3d(
            list(top.personagem), com, list(top.pagerank), [COMUNIDADES[(c - 1) % len(COMUNIDADES)] for c in top.comunidade],
            nomes=com, titulo_z="PageRank", ordem_y=sorted(set(com), key=lambda s: int(s.split()[-1])),
            hover=[f"<b>{x.personagem}</b><br>PageRank: {_fmt(x.pagerank, 3)}<br>Menções: {x.mencoes}<br>"
                   f"Ligações: {x.grau}<br>Comunidade {x.comunidade}" for x in top.itertuples()])
        _layout(f3, "Personagens mais centrais<br><sup>As 15 personagens com maior PageRank na rede de co-ocorrência; cada fila é uma comunidade"
                    "</sup>", altura=640, nota=NOTA_3D, legend=dict(orientation="h", y=0.02, x=0))
        t2 = top.iloc[::-1]
        f2 = go.Figure(go.Bar(x=t2.pagerank, y=t2.personagem, orientation="h",
                              marker=dict(color=[COMUNIDADES[(c - 1) % len(COMUNIDADES)] for c in t2.comunidade]),
                              text=[f"C{c}" for c in t2.comunidade], textposition="inside",
                              insidetextfont=dict(color=FUNDO, size=10),
                              hovertemplate="<b>%{y}</b><br>PageRank: %{x:.3f}<extra></extra>"))
        _layout(f2, "Personagens mais centrais", altura=560)
        itens.append(_item("personagens", f3, f2))

    # Vocabulário ---------------------------------------------------------------------------------------------------
    top = freq.head(20)
    nomes_classes = [NOMES_CLASSES.get(c, c) for c in top.pos]
    f3 = g3d.barras_3d(
        list(top.lema), nomes_classes, list(top.por_1000_palavras), [CORES_CLASSES.get(c, SUAVE) for c in top.pos],
        nomes=nomes_classes, titulo_z="por 1000 palavras",
        hover=[f"<b>{x.lema}</b> ({NOMES_CLASSES.get(x.pos, x.pos).lower()})<br>{_fmt(x.por_1000_palavras, 2)} por "
               f"1000 palavras<br>{x.ocorrencias} ocorrências" for x in top.itertuples()])
    _layout(f3, "Palavras de conteúdo mais frequentes<br><sup>Os 20 lemas mais frequentes; cada fila é uma classe "
                "gramatical</sup>", altura=640, nota=NOTA_3D, legend=dict(orientation="h", y=0.02, x=0))
    t2 = freq.head(30).iloc[::-1]
    f2 = go.Figure()
    for classe, sub in t2.groupby("pos", observed=True, sort=False):
        f2.add_bar(x=sub.por_1000_palavras, y=sub.lema, orientation="h", name=NOMES_CLASSES.get(classe, classe),
                   marker=dict(color=CORES_CLASSES.get(classe, SUAVE)),
                   hovertemplate="<b>%{y}</b>: %{x:.2f} por 1000 palavras<extra></extra>")
    f2.update_yaxes(categoryorder="array", categoryarray=list(t2.lema))
    f2.update_xaxes(title="ocorrências por 1000 palavras")
    _layout(f2, "Palavras de conteúdo mais frequentes", altura=680, barmode="stack",
            legend=dict(orientation="h", y=-0.08, x=0, yanchor="top"))
    itens.append(_item("vocabulario", f3, f2))

    col = extra.get("colocacoes")
    if col is not None and len(col) >= 3:
        c = col.head(25)
        f3 = g3d.dispersao(
            list(c.pmi), list(np.log10(c.g2)), list(c.ocorrencias), texto=list(c.colocacao),
            tamanho=list(6 + 14 * np.sqrt(c.ocorrencias / c.ocorrencias.max())), cores=OCRE,
            titulos=("PMI (exclusividade)", "log₁₀ G² (força)", "ocorrências"),
            customdata=np.c_[c.g2, c.pmi, c.ocorrencias],
            hover="<b>%{text}</b><br>G²: %{customdata[0]:.1f}<br>PMI: %{customdata[1]:.2f}<br>"
                  "Ocorrências: %{customdata[2]}<extra></extra>")
        _layout(f3, "Colocações<br><sup>Pares de palavras com associação mais forte (razão de verosimilhança G² de "
                    "Dunning e informação mútua pontual)</sup>", altura=640, nota=NOTA_3D)
        c2 = col.head(20).iloc[::-1]
        f2 = go.Figure(go.Bar(x=c2.g2, y=c2.colocacao, orientation="h", marker=dict(color=OCRE),
                              customdata=np.c_[c2.pmi, c2.ocorrencias],
                              hovertemplate="<b>%{y}</b><br>G²: %{x:.1f}<br>PMI: %{customdata[0]:.2f}<br>"
                                            "Ocorrências: %{customdata[1]}<extra></extra>"))
        f2.update_xaxes(title="G² (razão de verosimilhança)")
        _layout(f2, "Colocações", altura=600)
        itens.append(_item("vocabulario", f3, f2))

    chave = extra.get("palavras_chave")
    if chave is not None and len(chave):
        k3 = chave.groupby("segmento").head(3).copy()
        k3["posicao"] = k3.groupby("segmento").cumcount() + 1
        segs = sorted(k3.segmento.unique())
        f3 = g3d.barras_3d(
            [f"{s}" for s in k3.segmento], [f"{p}.ª" for p in k3.posicao], list(k3.tfidf),
            [{1: CASTANHO, 2: OCRE, 3: AREIA}[p] for p in k3.posicao], titulo_x="segmento", titulo_y="posição",
            titulo_z="TF-IDF", ordem_x=[f"{s}" for s in segs], ordem_y=["1.ª", "2.ª", "3.ª"], rotulos=list(k3.lema),
            hover=[f"<b>{x.lema}</b><br>segmento {x.segmento}<br>TF-IDF: {_fmt(x.tfidf, 2)}<br>{x.ocorrencias} "
                   "ocorrências no segmento" for x in k3.itertuples()], largura=0.55, profundidade=0.55)
        _layout(f3, "Palavras-chave por segmento<br><sup>As três palavras mais características de cada parte do livro "
                    "(TF-IDF, com os segmentos como documentos)</sup>", altura=640, nota=NOTA_3D)
        tabela = "".join(f'<li><b>{s}</b><span>{html.escape(", ".join(g.lema))}</span></li>'
                         for s, g in chave.groupby("segmento"))
        itens.append(_item("vocabulario", f3, f'<ol class="chaves">{tabela}</ol>'))

    # Gramática -----------------------------------------------------------------------------------------------------
    c = classes.sort_values("por_1000_palavras", ascending=False)
    f3 = g3d.barras_3d(list(c.nome), [""] * len(c), list(c.por_1000_palavras), [CASTANHO] * len(c),
                       titulo_z="por 1000 palavras", rotulos=[_fmt(v, 0) for v in c.por_1000_palavras],
                       hover=[f"<b>{x.nome}</b><br>{_fmt(x.por_1000_palavras, 1)} por 1000 palavras<br>"
                              f"{x.ocorrencias} ocorrências" for x in c.itertuples()], profundidade=0.7)
    f3.update_layout(scene_aspectratio=dict(x=2.1, y=0.45, z=0.8), scene_camera=dict(eye=dict(x=0.3, y=-1.85, z=0.7)))
    _layout(f3, "Classes gramaticais<br><sup>Etiquetas UPOS por 1000 palavras</sup>", altura=560, nota=NOTA_3D)
    c2 = c.iloc[::-1]
    f2 = go.Figure(go.Bar(x=c2.por_1000_palavras, y=c2.nome, orientation="h", marker=dict(color=CASTANHO),
                          hovertemplate="<b>%{y}</b>: %{x:.1f} por 1000 palavras<extra></extra>"))
    f2.update_xaxes(title="ocorrências por 1000 palavras")
    _layout(f2, "Classes gramaticais", altura=480)
    itens.append(_item("gramatica", f3, f2))

    tempos = extra.get("tempos")
    if tempos is not None and len(tempos):
        t = tempos[tempos.pct >= 0.5]
        modos = list(dict.fromkeys(t.modo))
        cores_modo = {m: [CASTANHO, TINTA, OCRE, CAQUI, FERRUGEM, AREIA][k % 6] for k, m in enumerate(modos)}
        f3 = g3d.barras_3d(
            [maiusculas(x) for x in t.tempo], [maiusculas(m) for m in t.modo], list(t.pct),
            [cores_modo[m] for m in t.modo], nomes=[maiusculas(m) for m in t.modo], titulo_z="% das formas finitas",
            rotulos=[_fmt(v, 0) + " %" for v in t.pct],
            hover=[f"<b>{x.tempo} do {x.modo}</b><br>{_fmt(x.pct, 1)} % das formas finitas<br>{x.ocorrencias} "
                   "ocorrências" for x in t.itertuples()])
        _layout(f3, "Tempos e modos verbais<br><sup>Formas verbais finitas por tempo (largura) e modo (profundidade)"
                    "</sup>", altura=600, nota=NOTA_3D, legend=dict(orientation="h", y=0.02, x=0))
        f2 = go.Figure()
        for m in modos:
            sub = t[t.modo == m]
            f2.add_bar(x=[maiusculas(x) for x in sub.tempo], y=sub.pct, name=maiusculas(m), marker=dict(color=cores_modo[m]),
                       hovertemplate="%{x}: %{y:.1f} %<extra></extra>")
        f2.update_yaxes(title="% das formas finitas")
        _layout(f2, "Tempos e modos verbais", altura=480, barmode="group",
                legend=dict(orientation="h", y=-0.15, x=0, yanchor="top"))
        itens.append(_item("gramatica", f3, f2))

    # Frases e evolução ---------------------------------------------------------------------------------------------
    fr = extra.get("frases")
    c = comprimentos[comprimentos > 0]
    if len(c):
        limite = max(int(c.quantile(0.95)), 5)
        f2 = go.Figure(go.Histogram(x=c.clip(upper=int(c.quantile(0.99))), xbins=dict(start=0.5, size=1),
                                    marker=dict(color="#B08B68", line=dict(color=PAPEL, width=0.6)),
                                    hovertemplate="%{x} palavras: %{y} frases<extra></extra>"))
        f2.add_vline(x=c.median(), line=dict(color=TINTA, width=2, dash="dot"),
                     annotation_text=f"mediana {c.median():.0f}", annotation_position="top right")
        f2.update_xaxes(title="palavras por frase (até ao percentil 99)")
        f2.update_yaxes(title="frases")
        _layout(f2, "Extensão das frases", altura=480, bargap=0.04)
        if fr is not None and fr.segmento.notna().any() and fr.segmento.nunique() >= 3:
            f = fr[(fr.palavras > 0) & fr.segmento.notna()]
            segs = sorted(f.segmento.unique().astype(int))
            xs = list(range(1, limite + 1))
            z = np.array([[100 * (sub.palavras == L).mean() for L in xs] for _, sub in f.groupby("segmento")])
            fora = 100 * (f.palavras > limite).mean()
            f3 = g3d.superficie(xs, segs, z, cores=[[0, PAPEL], [0.25, AREIA], [0.6, "#B08B68"], [1, CASTANHO]],
                                titulo_x="palavras por frase", titulo_y="segmento", titulo_z="% das frases",
                                hover="Segmento %{y}<br>%{x} palavras: %{z:.1f} % das frases<extra></extra>")
            _layout(f3, f"Extensão das frases ao longo do livro<br><sup>Distribuição em cada segmento, até {limite} "
                        f"palavras (percentil 95); a mediana do livro é {c.median():.0f}</sup>", altura=640,
                    nota=NOTA_3D + f" Frases com mais de {limite} palavras ({tema.num(fora, 1)} %) não aparecem no relevo; "
                    "estão na vista 2D.")
            itens.append(_item("frases", f3, f2))
        else:
            itens.append(_item("frases", f2))

    if len(evol) >= 3:
        from plotly.subplots import make_subplots

        series = [("mtld", "Diversidade lexical (MTLD)", ".1f", CASTANHO),
                  ("frase_media", "Extensão média das frases", ".1f", TINTA),
                  ("dialogo_pct", "Parágrafos de diálogo (%)", ".0f", OCRE)]
        if "sentimento" in evol and evol.sentimento.notna().sum() >= 3:
            series.append(("sentimento", "Sentimento médio", ".3f", CAQUI))
        series = [s for s in series if evol[s[0]].notna().sum() >= 3]
        fitas = []
        for col_, rot, fmt, cor in series:
            v = evol[col_].astype(float)
            dp = v.std()
            fitas.append((maiusculas(rot), list(((v - v.mean()) / dp).fillna(0) if dp else v * 0), list(v), cor, fmt))
        f3 = g3d.fitas(list(evol.segmento), fitas, titulo_x="segmento (início → fim)",
                       titulo_z="desvio face à média (desvios-padrão)")
        _layout(f3, "Evolução ao longo do livro<br><sup>Cada fita é um indicador, normalizado para a mesma escala; "
                    "acima de 0 = acima da média do livro</sup>", altura=640, nota=NOTA_3D + " A vista 2D mostra os "
                    "valores originais.")
        f2 = make_subplots(rows=len(series), cols=1, shared_xaxes=True, vertical_spacing=0.08,
                           subplot_titles=[maiusculas(rot) for _, rot, _, _ in series])
        for k, (col_, rot, fmt, cor) in enumerate(series, start=1):
            f2.add_scatter(x=evol.segmento, y=evol[col_], mode="lines+markers", showlegend=False,
                           line=dict(color=cor, width=2.5), marker=dict(size=7, color=cor), row=k, col=1,
                           hovertemplate=f"{rot}<br>segmento %{{x}}: %{{y:{fmt}}}<extra></extra>")
        f2.update_xaxes(dtick=1)
        _layout(f2, "Evolução ao longo do livro", altura=170 * len(series) + 120)
        f2.update_layout(margin=dict(t=34))
        for a in f2.layout.annotations:
            a.update(x=0, xanchor="left", font=dict(size=12, color=SUAVE))
        itens.append(_item("frases", f3, f2))

    # Sentimento ----------------------------------------------------------------------------------------------------
    if len(evol) >= 3 and "frases_positivas_pct" in evol and evol.frases_positivas_pct.notna().sum() >= 3:
        neutras = 100 - evol.frases_positivas_pct - evol.frases_negativas_pct
        cats = [("Positivas", evol.frases_positivas_pct, CASTANHO), ("Neutras", neutras, AREIA),
                ("Negativas", evol.frases_negativas_pct, TINTA)]
        xs, ys, zs, cs, hv = [], [], [], [], []
        for nome, vals, cor in cats:
            for sgm, v in zip(evol.segmento, vals):
                xs.append(str(sgm)); ys.append(nome); zs.append(v); cs.append(cor)
                hv.append(f"<b>Segmento {sgm}</b><br>Frases {nome.lower()}: {_fmt(v, 1)} %")
        f3 = g3d.barras_3d(xs, ys, zs, cs, nomes=ys, hover=hv, titulo_x="segmento", titulo_z="% das frases",
                           ordem_y=["Negativas", "Positivas", "Neutras"])
        f3.update_layout(scene_camera=dict(eye=dict(x=0.45, y=-1.55, z=1.35), center=dict(x=0, y=0, z=-0.15)))
        _layout(f3, "Sentimento ao longo do livro<br><sup>Proporção de frases positivas, neutras e negativas em cada "
                    "segmento</sup>", altura=620, nota=NOTA_3D, legend=dict(orientation="h", y=0.02, x=0))
        f2 = go.Figure()
        f2.add_hrect(y0=-0.05, y1=0.05, fillcolor=GRELHA, opacity=0.6, line_width=0)
        f2.add_scatter(x=evol.segmento, y=evol.sentimento, mode="lines+markers", line=dict(color=CASTANHO, width=3),
                       marker=dict(size=8, color=CASTANHO), name="sentimento médio",
                       hovertemplate="Segmento %{x}: %{y:.3f}<extra></extra>")
        f2.update_xaxes(title="segmento (início → fim)", dtick=1)
        f2.update_yaxes(title="sentimento médio (−1 a +1)", zeroline=True, zerolinecolor=SUAVE)
        _layout(f2, "Arco de sentimento", altura=460)
        itens.append(_item("sentimento", f3, f2))

    # Leis do vocabulário (2D: escalas logarítmicas) ----------------------------------------------------------------
    zipf_t, heaps_t = extra.get("zipf"), extra.get("heaps")
    if zipf_t is not None and len(zipf_t) > 10:
        f2 = go.Figure(go.Scatter(x=zipf_t.posicao, y=zipf_t.frequencia, mode="markers",
                                  marker=dict(size=4, color=CASTANHO, opacity=0.6), text=zipf_t.forma,
                                  hovertemplate="<b>%{text}</b><br>posição %{x}: %{y} ocorrências<extra></extra>"))
        from .graficos import reta_zipf
        ajuste = reta_zipf(zipf_t)
        if ajuste is not None:
            r, f, s_ = ajuste
            f2.add_scatter(x=r, y=f, mode="lines", line=dict(color=TINTA, width=2, dash="dash"), hoverinfo="skip",
                           name=f"ajuste: s = {tema.num(s_, 2)}")
            f2.update_layout(legend=dict(x=0.02, y=0.05))
        f2.update_xaxes(type="log", title="posição (1 = forma mais frequente)")
        f2.update_yaxes(type="log", title="ocorrências")
        _layout(f2, "Lei de Zipf<br><sup>Frequência em função da posição, escala log-log; só formas com pelo menos "
                    f"{int(zipf_t.frequencia.min())} ocorrências</sup>", altura=460,
                nota="Gráfico em 2D: as escalas logarítmicas são o que torna a lei visível, e uma terceira dimensão "
                     "não acrescentaria informação.")
        itens.append(_item("leis", f2, largo=False))
    if heaps_t is not None and len(heaps_t) > 5:
        f2 = go.Figure(go.Scatter(x=heaps_t.palavras, y=heaps_t.vocabulario, mode="lines", line=dict(color=TINTA, width=3),
                                  hovertemplate="%{x} palavras lidas: %{y} formas distintas<extra></extra>"))
        f2.update_xaxes(type="log", title="palavras lidas (N)")
        f2.update_yaxes(type="log", title="formas distintas (V)")
        _layout(f2, "Lei de Heaps<br><sup>Crescimento do vocabulário, escala log-log</sup>", altura=460)
        itens.append(_item("leis", f2, largo=False))

    # Lugares -------------------------------------------------------------------------------------------------------
    lugares = ents[ents.tipo == "lugar"].head(12) if not ents.empty else ents
    if len(lugares):
        f3 = g3d.barras_3d(list(lugares.entidade), [""] * len(lugares), list(lugares.ocorrencias), [CAQUI] * len(lugares),
                           titulo_z="menções", rotulos=[str(v) for v in lugares.ocorrencias], profundidade=0.7,
                           hover=[f"<b>{x.entidade}</b><br>{x.ocorrencias} menções" for x in lugares.itertuples()])
        f3.update_layout(scene_aspectratio=dict(x=2.1, y=0.45, z=0.8), scene_camera=dict(eye=dict(x=0.3, y=-1.85, z=0.7)))
        _layout(f3, "Lugares mais mencionados<br><sup>Estimativa do reconhecimento de entidades (NER)</sup>",
                altura=540, nota=NOTA_3D)
        l2 = lugares.iloc[::-1]
        f2 = go.Figure(go.Bar(x=l2.ocorrencias, y=l2.entidade, orientation="h", marker=dict(color=CAQUI),
                              hovertemplate="<b>%{y}</b>: %{x} menções<extra></extra>"))
        f2.update_xaxes(title="menções")
        _layout(f2, "Lugares mais mencionados", altura=460)
        itens.append(_item("lugares", f3, f2))
    return itens


# ---------------------------------------------------------------------------
# Página HTML
# ---------------------------------------------------------------------------

FONTES_WEB = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
              '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&'
              'family=Source+Serif+4:ital,opsz,wght@0,8..60,400;1,8..60,400&family=Source+Sans+3:wght@400;600&'
              'display=swap" rel="stylesheet">')

ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

CSS = """
:root{--papel:#F4EEE3;--papel2:#EDE4D3;--tinta:#1E1915;--suave:#6E5E4E;--linha:#D8CBB4;--castanho:#7A4E2D;
--ocre:#B8893E;--areia:#D9C7A3;--creme:#F3EADB;
--display:"Cormorant Garamond",Georgia,"Times New Roman",serif;--texto:"Source Serif 4",Georgia,serif;
--ui:"Source Sans 3","Helvetica Neue",Arial,sans-serif;--largura:1200px}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--papel);color:var(--tinta);font-family:var(--texto);font-size:17px;line-height:1.6;
-webkit-font-smoothing:antialiased}
a{color:var(--castanho);text-decoration:none;border-bottom:1px solid var(--areia)}a:hover{color:var(--tinta);border-color:var(--tinta)}
.envolve{max-width:var(--largura);margin:0 auto;padding:0 32px}

/* cabeçalho */
.cabecalho{background:var(--tinta);color:var(--creme);position:relative;overflow:hidden}
.cabecalho:before{content:"";position:absolute;inset:0;background:
radial-gradient(900px 420px at 88% -10%,rgba(184,137,62,.20),transparent 60%),
radial-gradient(600px 300px at -5% 110%,rgba(122,78,45,.35),transparent 60%);pointer-events:none}
.barra{position:relative;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:16px 0;
border-bottom:1px solid rgba(243,234,219,.14);font-family:var(--ui);font-size:15px;font-weight:600;letter-spacing:.06em;
color:var(--areia)}
.barra a{color:var(--areia);border:0}.barra a:hover{color:var(--creme)}
.marca{display:flex;align-items:center;gap:10px;font-family:var(--display);font-size:25px;letter-spacing:.02em;
color:var(--creme);font-weight:700}
.marca img{width:30px;height:30px;border-radius:50%}
.rosto{position:relative;display:grid;grid-template-columns:auto 1fr;gap:44px;align-items:center;padding:64px 0 56px}
.selo{width:188px;height:188px;border-radius:50%;padding:7px;background:conic-gradient(from 210deg,var(--ocre),#6b4b26,var(--ocre),#e2c58f,var(--ocre));
box-shadow:0 18px 50px rgba(0,0,0,.45)}
.selo img{width:100%;height:100%;border-radius:50%;display:block}
.antetitulo{font-family:var(--display);font-style:italic;font-weight:700;font-size:27px;color:var(--ocre);margin:0 0 6px}
.rosto h1{font-family:var(--display);font-weight:700;font-size:clamp(54px,8.4vw,112px);line-height:.96;margin:0;
letter-spacing:-.015em}
.autoria{font-family:var(--display);font-style:italic;font-weight:700;font-size:clamp(27px,3.2vw,38px);color:var(--areia);
margin:14px 0 0}
.ornamento{display:flex;align-items:center;gap:14px;color:var(--ocre);margin:26px 0 18px;max-width:520px}
.ornamento:before,.ornamento:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--ocre),transparent)}
.dados-rosto{display:flex;flex-wrap:wrap;gap:8px 30px;font-family:var(--ui);font-size:17px;font-weight:600;
color:var(--areia);letter-spacing:.02em;margin:0;padding:0;list-style:none}
.dados-rosto b{color:var(--creme);font-weight:700}

/* índice */
.indice{position:sticky;top:0;z-index:10;background:var(--papel);border-bottom:1px solid var(--linha)}
.indice .envolve{display:flex;gap:0;overflow-x:auto;scrollbar-width:none}
.indice a{flex:none;border:0;padding:15px 18px 13px;font-family:var(--ui);font-size:14px;color:var(--suave);
border-bottom:2px solid transparent}
.indice a span{font-family:var(--display);font-style:italic;color:var(--ocre);margin-right:6px;font-size:16px}
.indice a:hover,.indice a.ativo{color:var(--tinta);border-bottom-color:var(--castanho)}
.indice a.ativo{font-weight:600}
.progresso{position:absolute;left:0;bottom:-1px;height:2px;width:0;background:var(--ocre)}
.voltar-topo{position:fixed;right:24px;bottom:24px;z-index:20;width:54px;height:54px;border-radius:50%;
display:grid;place-items:center;background:var(--tinta);color:var(--creme);border:2px solid var(--ocre);
box-shadow:0 10px 26px rgba(30,25,21,.28);opacity:0;transform:translateY(14px);pointer-events:none;
transition:opacity .25s,transform .25s,background .2s}
.voltar-topo.visivel{opacity:1;transform:none;pointer-events:auto}
.voltar-topo:hover{background:var(--castanho);color:#fff;border-color:var(--ocre)}
.voltar-topo:focus-visible{outline:3px solid var(--ocre);outline-offset:3px}
.voltar-topo svg{width:22px;height:22px}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.voltar-topo{transition:none}}
@media print{.indice,.voltar-topo,.vista{display:none}.cabecalho{-webkit-print-color-adjust:exact;print-color-adjust:exact}}

/* resumo */
main{padding:8px 0 40px}
.numeros{display:grid;grid-template-columns:repeat(3,1fr);margin:48px 0 8px;border-top:2px solid var(--tinta)}
.numero{padding:28px 28px 26px;border-bottom:1px solid var(--linha)}
.numero:not(:nth-child(3n+1)){border-left:1px solid var(--linha)}
.numero b{display:block;font-family:var(--display);font-weight:600;font-size:clamp(46px,5.6vw,72px);line-height:1;
font-variant-numeric:lining-nums tabular-nums;color:var(--tinta)}
.numero b small{font-size:.42em;font-weight:500;color:var(--castanho);margin-left:6px;font-style:italic}
.numero span{display:block;margin-top:12px;font-family:var(--display);font-size:22px;font-style:italic;color:var(--castanho)}
.numero em{display:block;font-style:normal;font-family:var(--ui);font-size:13px;color:var(--suave);margin-top:4px}
.ficha{display:grid;grid-template-columns:1fr 1fr;gap:48px;margin:44px 0 0}
.ficha h3,.figura h3{font-family:var(--display);font-weight:600;font-size:28px;margin:0 0 10px;line-height:1.15}
.ficha dl{margin:0}
.ficha dl div{display:flex;align-items:baseline;gap:10px;padding:7px 0}
.ficha dt{font-family:var(--ui);font-size:14px;color:var(--suave);white-space:nowrap}
.ficha dl div:after{content:"";order:2;flex:1;border-bottom:1px dotted var(--linha);transform:translateY(-4px)}
.ficha dd{order:3;margin:0;text-align:right;font-size:16px}
.notas{border-left:3px solid var(--ocre);padding:2px 0 2px 20px;font-size:16px;color:var(--suave)}
.notas ul{margin:0;padding-left:18px}.notas li{margin:4px 0}

/* secções e gráficos */
.seccao{margin:88px 0 0;scroll-margin-top:60px}
.cab-seccao{display:grid;grid-template-columns:auto 1fr;gap:22px;align-items:end;border-bottom:2px solid var(--tinta);
padding-bottom:14px}
.cab-seccao .num{font-family:var(--display);font-style:italic;font-size:64px;line-height:.8;color:var(--ocre)}
.cab-seccao h2{font-family:var(--display);font-weight:600;font-size:clamp(34px,4.2vw,50px);line-height:1;margin:0}
.lede{font-size:19px;color:var(--suave);max-width:820px;margin:18px 0 8px;font-style:italic}
.figura{margin:40px 0 0;padding-top:16px;border-top:1px solid var(--linha)}
.figura .sub{font-family:var(--ui);font-size:14px;color:var(--suave);margin:0 0 10px}
.figura .nota{font-family:var(--ui);font-size:13px;color:var(--castanho);margin:6px 0 0}
.par{display:grid;grid-template-columns:1fr 1fr;gap:48px}
.tabela{overflow-x:auto;margin:44px 0 0}
table{border-collapse:collapse;width:100%;font-family:var(--ui);font-size:15px}
th{font-weight:600;text-align:left;color:var(--suave);font-size:13px;letter-spacing:.06em;padding:10px 12px;
border-bottom:2px solid var(--tinta)}
td{padding:12px;border-bottom:1px solid var(--linha)}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
td a{font-family:var(--display);font-size:20px;font-weight:600}

/* rodapé */
.rodape{background:var(--tinta);color:var(--areia);margin-top:110px;font-family:var(--ui);font-size:14px}
.rodape .topo{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:48px;padding:56px 0 40px}
.rodape .marca{font-size:28px}.rodape .marca img{width:44px;height:44px}
.rodape p{margin:12px 0 0;line-height:1.55;max-width:380px}
.rodape h4{font-family:var(--display);font-style:italic;font-weight:500;font-size:20px;color:var(--ocre);margin:0 0 12px}
.rodape ul{list-style:none;margin:0;padding:0}.rodape li{margin:0 0 8px}
.rodape a{color:var(--creme);border-bottom-color:rgba(243,234,219,.25)}.rodape a:hover{border-color:var(--creme)}
.rodape .base{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px 24px;padding:18px 0 26px;
border-top:1px solid rgba(243,234,219,.14);font-size:12.5px;color:#a8977f}
.rodape code{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:var(--areia)}

/* ficha técnica no cabeçalho */
.rosto.com-ficha{grid-template-columns:auto 1fr minmax(280px,340px)}
.ficha-topo{position:relative;border:1px solid rgba(243,234,219,.18);border-top:3px solid var(--ocre);
background:rgba(243,234,219,.05);padding:20px 24px 12px}
.ficha-topo h2{font-family:var(--display);font-style:italic;font-weight:700;font-size:28px;color:var(--ocre);margin:0 0 10px}
.ficha-topo dl{margin:0}.ficha-topo dl div{display:grid;grid-template-columns:auto 1fr;gap:12px;padding:6px 0;
border-bottom:1px solid rgba(243,234,219,.10)}.ficha-topo dl div:last-child{border:0}
.ficha-topo dt{font-family:var(--ui);font-size:15px;font-weight:600;color:var(--areia);letter-spacing:.02em}
.ficha-topo dd{margin:0;text-align:right;font-family:var(--ui);font-size:17px;font-weight:700;color:var(--creme);
overflow-wrap:anywhere}
.ficha-topo dl div{padding:9px 0}

/* legibilidade */
.leitura{display:grid;grid-template-columns:minmax(220px,300px) 1fr;gap:18px 44px;align-items:center;margin:44px 0 0;
padding:28px 0;border-top:1px solid var(--linha);border-bottom:1px solid var(--linha)}
.veredicto span{display:block;font-family:var(--display);font-style:italic;font-size:22px;color:var(--castanho)}
.veredicto b{display:block;font-family:var(--display);font-weight:700;font-size:clamp(54px,7vw,84px);line-height:.95}
.veredicto small{display:block;font-family:var(--ui);font-size:13px;color:var(--suave);margin-top:8px}
.regua{position:relative;padding-top:6px}
.faixas{position:relative;height:46px;border:1px solid var(--tinta)}
.faixas span{position:absolute;top:0;bottom:0;display:flex;align-items:center;justify-content:center;overflow:hidden;
border-right:1px solid rgba(244,238,227,.6)}
.faixas em{font-style:normal;font-family:var(--ui);font-size:11.5px;color:#fff;white-space:nowrap;padding:0 4px;
text-shadow:0 1px 1px rgba(0,0,0,.35)}
.regua i{position:absolute;top:-4px;width:4px;height:60px;margin-left:-2px;background:var(--tinta);
box-shadow:0 0 0 2px var(--papel)}
.regua i:after{content:"";position:absolute;top:-9px;left:-6px;border:8px solid transparent;border-top-color:var(--tinta)}
.marcas{display:flex;justify-content:space-between;font-family:var(--ui);font-size:12px;color:var(--suave);margin-top:8px}
.leitura .nota{grid-column:1/-1;font-family:var(--ui);font-size:13px;color:var(--suave);margin:0}
.notas-bloco{margin:36px 0 0;max-width:860px}.notas-bloco h3{font-family:var(--display);font-weight:600;font-size:26px;margin:0 0 10px}

/* cabeçalho das figuras e alternador 3D/2D */
.cab-fig{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.vista{flex:none;display:inline-flex;border:1px solid var(--tinta);margin-top:4px}
.vista button{font-family:var(--ui);font-size:13px;font-weight:600;letter-spacing:.06em;padding:6px 14px;border:0;
background:transparent;color:var(--tinta);cursor:pointer}
.vista button.ativo{background:var(--tinta);color:var(--creme)}
.vista button:focus-visible{outline:2px solid var(--ocre);outline-offset:2px}
.v2[hidden],.v3[hidden]{display:none}

/* pequenos indicadores, citações e listas */
.mini{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:26px 0 0;border-top:1px solid var(--tinta)}
.mini div{padding:16px 18px 14px;border-bottom:1px solid var(--linha)}
.mini div+div{border-left:1px solid var(--linha)}
.mini b{display:block;font-family:var(--display);font-weight:600;font-size:36px;line-height:1.05;font-variant-numeric:lining-nums}
.mini span{display:block;font-family:var(--ui);font-size:13px;color:var(--suave);margin-top:4px}
.citacoes{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin:36px 0 0}
.citacoes h3{font-family:var(--display);font-weight:600;font-size:24px;margin:0 0 6px}
blockquote{margin:14px 0 0;padding:4px 0 4px 18px;border-left:3px solid var(--castanho)}
blockquote.negativa{border-left-color:var(--tinta)}
blockquote p{margin:0;font-family:var(--texto);font-style:italic;font-size:16.5px;line-height:1.55}
blockquote cite{display:block;margin-top:4px;font-family:var(--ui);font-style:normal;font-size:12.5px;color:var(--suave)}
.chaves{list-style:none;margin:8px 0 0;padding:0;columns:2;column-gap:48px}
.chaves li{display:grid;grid-template-columns:42px 1fr;gap:10px;padding:9px 0;border-bottom:1px solid var(--linha);break-inside:avoid}
.chaves b{font-family:var(--display);font-size:22px;color:var(--ocre);font-weight:600}
.aviso-estado{border-left:3px solid var(--ocre);padding-left:16px;color:var(--suave)}
.leitura-na{margin:40px 0 0;font-size:17px}

@media(max-width:1080px){.rosto.com-ficha{grid-template-columns:auto 1fr}.ficha-topo{grid-column:1/-1}}
@media(max-width:860px){.leitura,.citacoes{grid-template-columns:1fr}.chaves{columns:1}
.rosto.com-ficha{grid-template-columns:1fr}.mini div+div{border-left:0}.faixas em{font-size:0}}
@media(max-width:860px){.envolve{padding:0 18px}.rosto{grid-template-columns:1fr;gap:24px;padding:40px 0}
.selo{width:112px;height:112px}.numeros{grid-template-columns:1fr 1fr}
.numero:not(:nth-child(3n+1)){border-left:0}.numero:nth-child(even){border-left:1px solid var(--linha)}
.numero{padding:22px 16px}.ficha,.par{grid-template-columns:1fr;gap:28px}.rodape .topo{grid-template-columns:1fr;gap:28px}
.cab-seccao .num{font-size:46px}.seccao{margin-top:64px}.barra .lema{display:none}}
@media(max-width:420px){.numeros{grid-template-columns:1fr}.numero:nth-child(even){border-left:0}}
"""


def _icone(tamanho: int) -> str:
    """Ícone do projeto embutido em base64, para funcionar no GitHub Pages e em ficheiros abertos localmente."""
    import base64

    f = RECURSOS / f"icone-{tamanho}.png"
    return "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode() if f.exists() else ""


def _num(v, casas=1):
    if v is None or (isinstance(v, float) and v != v):
        return "—"
    if isinstance(v, (int, np.integer)) or float(v).is_integer() and abs(v) >= 100:
        return f"{int(v):,}".replace(",", " ")
    texto = f"{v:.{casas}f}".replace(".", ",")
    return "−" + texto[1:] if texto.startswith("-") else texto


def _div(fig: go.Figure, primeira: bool, offline: bool) -> str:
    return pio.to_html(fig, full_html=False, include_plotlyjs=("inline" if offline else "cdn") if primeira else False,
                       config={"displaylogo": False, "responsive": True, "scrollZoom": False,
                               "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
                               "toImageButtonOptions": {"format": "png", "scale": 2}})


def _figura(item: dict, primeira: bool, offline: bool) -> tuple[str, bool]:
    """Devolve (html, primeira). Com alternativa, mostra a vista 3D e um botão para a vista 2D."""
    fig, alt = item["fig"], item.get("alt")
    meta = fig.layout.meta or {}
    e = html.escape
    principal = _div(fig, primeira, offline)
    primeira = False
    cabeca = (f'<div class="cab-fig"><div><h3>{e(meta.get("titulo", ""))}</h3>'
              + (f'<p class="sub">{e(meta["subtitulo"])}</p>' if meta.get("subtitulo") else "") + "</div>")
    if alt is None:
        corpo = cabeca + "</div>" + principal
    else:
        segunda = alt if isinstance(alt, str) else _div(alt, primeira, offline)
        corpo = (cabeca + '<div class="vista" role="group" aria-label="Vista do gráfico">'
                 '<button type="button" class="ativo" data-vista="v3">3D</button>'
                 '<button type="button" data-vista="v2">2D</button></div></div>'
                 f'<div class="v3">{principal}</div><div class="v2" hidden>{segunda}</div>')
    nota = f'<p class="nota">{e(meta["nota"])}</p>' if meta.get("nota") else ""
    return f'<figure class="figura">{corpo}{nota}</figure>', primeira


def _mini(valores: list[tuple[str, str]]) -> str:
    """Fila de pequenos indicadores (valor, rótulo)."""
    return '<div class="mini">' + "".join(
        f'<div><b>{html.escape(v)}</b><span>{html.escape(maiusculas(r))}</span></div>' for v, r in valores) + "</div>"


JS = """
document.addEventListener("click",ev=>{const b=ev.target.closest(".vista button");if(!b)return;
const fig=b.closest(".figura");fig.querySelectorAll(".vista button").forEach(x=>x.classList.toggle("ativo",x===b));
const v=b.dataset.vista;fig.querySelector(".v3").hidden=v!=="v3";fig.querySelector(".v2").hidden=v!=="v2";
if(window.Plotly)fig.querySelectorAll(".js-plotly-plot").forEach(g=>{if(g.offsetParent)Plotly.Plots.resize(g)});});
// No GitHub Pages, os relatórios em Markdown e os ficheiros Excel abrem-se no GitHub (onde o Markdown é formatado).
if(location.hostname.endsWith(".github.io")){const u=location.hostname.split(".")[0],p=location.pathname.split("/").filter(Boolean);
if(p.length){const repo=p[0];document.querySelectorAll("a[href]").forEach(a=>{const h=a.getAttribute("href");
if(/^(https?:|#|mailto:|data:)/.test(h)||!/\\.(md|xlsx|csv|json)$/.test(h))return;
const alvo=new URL(h,location.href).pathname.split("/").filter(Boolean).slice(1).join("/");
a.href=`https://github.com/${u}/${repo}/blob/main/${alvo}`;});}}
window.addEventListener("load",()=>{if(window.Plotly)document.querySelectorAll(".js-plotly-plot").forEach(g=>{if(g.offsetParent)Plotly.Plots.resize(g)})});
(()=>{const topo=document.querySelector(".voltar-topo"),barra=document.querySelector(".progresso");
const atualizar=()=>{const y=window.scrollY,h=document.documentElement.scrollHeight-innerHeight;
if(topo)topo.classList.toggle("visivel",y>600);if(barra)barra.style.width=(h>0?100*y/h:0)+"%";};
addEventListener("scroll",atualizar,{passive:true});atualizar();
const ligacoes=[...document.querySelectorAll(".indice a")];
if("IntersectionObserver" in window){const obs=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){
ligacoes.forEach(a=>a.classList.toggle("ativo",a.getAttribute("href")==="#"+e.target.id));}})},{rootMargin:"-45% 0px -50% 0px"});
document.querySelectorAll("main section[id]").forEach(s=>obs.observe(s));}})();
"""


def pagina(titulo: str, autoria: str, numeros: list[tuple[str, str, str]], itens: list[dict], resumo_html: str,
           rodape: dict, offline: bool, destino: Path, antetitulo: str = "Análise do Livro",
           dados_rosto: list[tuple[str, str]] | None = None, ficha: list[tuple[str, str]] | None = None,
           seccoes: dict | None = None, extras: dict | None = None, ligacao_corpus: str | None = None):
    """Escreve a página. `numeros` = (valor, unidade, rótulo); `extras` = HTML a inserir no início de cada secção."""
    e = html.escape
    seccoes, extras = seccoes or {}, extras or {}
    ordem = [k for k in seccoes if any(i["seccao"] == k for i in itens) or k in extras]
    ordem += [k for k in dict.fromkeys(i["seccao"] for i in itens) if k not in ordem]
    corpo, primeira = [], True
    for n, chave in enumerate(ordem, start=2):
        nome, lede = seccoes.get(chave, (chave.capitalize(), ""))
        blocos, pares = [], []
        for it in (i for i in itens if i["seccao"] == chave):
            bloco, primeira = _figura(it, primeira, offline)
            (blocos if it["largo"] else pares).append(bloco)
        if len(pares) == 1:          # um gráfico pequeno sozinho ocupa a largura toda
            blocos, pares = blocos + pares, []
        miolo = extras.get(chave, "") + "".join(blocos) + (f'<div class="par">{"".join(pares)}</div>' if pares else "")
        corpo.append(f'<section class="seccao" id="{chave}"><div class="cab-seccao"><span class="num">'
                     f'{ROMANOS[(n - 1) % 10]}</span><h2>{e(maiusculas(nome))}</h2></div>'
                     + (f'<p class="lede">{e(lede)}</p>' if lede else "") + miolo + "</section>")
    indice = '<a href="#resumo"><span>I</span>Resumo</a>' + "".join(
        f'<a href="#{k}"><span>{ROMANOS[n - 1]}</span>{e(maiusculas(seccoes.get(k, (k.capitalize(),))[0]))}</a>'
        for n, k in enumerate(ordem, start=2))
    blocos = "".join(f'<div class="numero"><b>{e(v)}{f"<small>{e(u)}</small>" if u else ""}</b>'
                     f'<span>{e(maiusculas(r))}</span></div>' for v, u, r in numeros)
    rosto = "".join(f"<li>{e(r)} <b>{e(v)}</b></li>" for r, v in (dados_rosto or []))
    ficha_html = ("" if not ficha else '<aside class="ficha-topo"><h2>Ficha Técnica</h2><dl>'
                  + "".join(f"<div><dt>{e(r)}</dt><dd>{e(str(v))}</dd></div>" for r, v in ficha) + "</dl></aside>")
    icone32, icone128, icone256 = _icone(32), _icone(128), _icone(256)
    cabeca = (f'<link rel="icon" type="image/png" sizes="32x32" href="{icone32}">'
              f'<link rel="apple-touch-icon" href="{icone256 or icone128}">') if icone32 else ""
    voltar = f'<a href="{ligacao_corpus}">Todos os Livros</a>' if ligacao_corpus else ""
    ligacoes = "".join(f'<li><a href="{e(u)}">{e(t)}</a></li>' for t, u in rodape["ligacoes"])
    tecnico = "".join(f"<li>{e(t)} <code>{e(v)}</code></li>" for t, v in rodape["tecnico"])
    destino.write_text(f"""<!doctype html>
<html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)} · Livros-PLN</title><meta name="theme-color" content="#1E1915">
<meta name="description" content="{e(antetitulo)}: {e(titulo)}. Indicadores linguísticos, sentimento, rede de personagens e estilo.">
{cabeca}{FONTES_WEB}<style>{CSS}</style></head>
<body>
<header class="cabecalho" id="topo"><div class="envolve">
 <div class="barra"><span class="marca"><img src="{icone32}" alt="">Livros-PLN</span>
  <span class="lema">Análise Computacional de Textos Literários</span>{voltar}</div>
 <div class="rosto{' com-ficha' if ficha else ''}"><div class="selo"><img src="{icone256 or icone128}" alt="Ícone do Livros-PLN"></div>
  <div class="titulos"><p class="antetitulo">{e(antetitulo)}</p><h1>{e(titulo)}</h1>
  {f'<p class="autoria">{e(autoria)}</p>' if autoria else ''}
  <div class="ornamento">❦</div><ul class="dados-rosto">{rosto}</ul></div>{ficha_html}</div>
</div></header>
<nav class="indice" aria-label="Índice"><div class="envolve">{indice}</div><span class="progresso" aria-hidden="true"></span></nav>
<main class="envolve"><section id="resumo"><div class="numeros">{blocos}</div>{resumo_html}</section>{''.join(corpo)}</main>
<footer class="rodape"><div class="envolve">
 <div class="topo">
  <div><span class="marca"><img src="{icone128}" alt="">Livros-PLN</span>
   <p>{e(rodape["descricao"])}</p></div>
  <div><h4>Explorar</h4><ul>{ligacoes}</ul></div>
  <div><h4>Esta Análise</h4><ul>{tecnico}</ul></div>
 </div>
 <div class="base"><span>{e(rodape["autoria"])}</span><span>{e(rodape["aviso"])}</span></div>
</div></footer>
<a href="#topo" class="voltar-topo" aria-label="Voltar ao topo" title="Voltar ao topo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg></a>
<script>{JS}</script>
</body></html>
""", encoding="utf-8")


DESCRICAO = ("Indicadores linguísticos, estilométricos, de sentimento e de rede de personagens para livros em "
             "português, francês e inglês, com definição, limitações e referência para cada valor.")
AUTORIA = "© João Garção · Código com todos os direitos reservados"


def _escala_leitura(i: dict, lingua: str) -> str:
    """Régua da legibilidade com as faixas da língua e o marcador do livro."""
    from .indicadores import FAIXAS_FLESCH, FAIXAS_MARTINS, FRONTEIRA_LEITURA

    v = i.get("legibilidade")
    if v is None or not i.get("legibilidade_leitura"):
        return ""
    if lingua == "pt":
        limites = [(lim, rot) for lim, rot, _ in FAIXAS_MARTINS]
        fonte = "Faixas de Martins et al. (1996), calibradas com manuais escolares em português do Brasil"
    else:
        limites = FAIXAS_FLESCH
        fonte = "Faixas de Flesch (1948)" + (" mantidas por Kandel e Moles (1958)" if lingua == "fr" else "")
    pontos = sorted({0, 100, *[max(0, min(100, l)) for l, _ in limites]})
    faixas = []
    for lim, rot in sorted(limites, key=lambda x: x[0]):
        ini = max(0, lim)
        fim = min([l for l, _ in limites if l > lim] + [100])
        if fim > ini:
            faixas.append((ini, fim, rot))
    tons = ["#5C4A3A", "#7A4E2D", "#9C6B45", "#B08B68", "#C9A66B", "#D9C7A3", "#E8DCC2"]
    barras = "".join(f'<span style="left:{a}%;width:{b - a}%;background:{tons[k % len(tons)]}" title="{html.escape(r)}">'
                     f'<em>{html.escape(maiusculas(r))}</em></span>' for k, (a, b, r) in enumerate(faixas))
    pos = max(0, min(100, v))
    nivel = f' Nível escolar indicativo: {html.escape(i["legibilidade_nivel"])}.' if i.get("legibilidade_nivel") else ""
    return (f'<div class="leitura"><div class="veredicto"><span>Leitura</span><b>{html.escape(maiusculas(i["legibilidade_leitura"]))}</b>'
            f'<small>Índice de Flesch adaptado: {_num(v, 1)} · faixa «{html.escape(i["legibilidade_escala"])}»</small></div>'
            f'<div class="regua"><div class="faixas">{barras}</div><i style="left:{pos}%"></i>'
            f'<div class="marcas"><span>0 · difícil</span><span>fronteira fácil/difícil: {FRONTEIRA_LEITURA.get(lingua, 60)}</span>'
            f'<span>100 · fácil</span></div></div>'
            f'<p class="nota">{fonte}.{nivel} O índice só mede a extensão das frases e das palavras: ignora o vocabulário '
            "raro, a sintaxe, a ironia e o conhecimento que o texto pressupõe.</p></div>")


def painel_livro(registo: dict, freq, classes, comprimentos, evol, ents, pers, g, destino: Path, offline: bool = False,
                 extra: dict | None = None):
    extra = extra or {}
    i, m, e = registo["indicadores"], registo["metadados"], registo["estados"]
    lg = registo["lingua"]

    def v(chave, casas=1):
        return "n.a." if chave in e else tema.num(i.get(chave), casas)

    numeros = [(v("palavras", 0), "", "palavras"),
               (v("mtld"), "", "diversidade lexical (MTLD)"),
               (v("frase_mediana", 0), "palavras", "extensão mediana das frases"),
               (v("legibilidade", 0), maiusculas(i.get("legibilidade_leitura") or ""), "legibilidade (Flesch adaptado)"),
               (v("sentimento_medio", 3), "", "sentimento médio (−1 a +1)"),
               (v("personagens_na_rede", 0), "", "personagens na rede")]
    ficha = [(r, m.get(k) or "desconhecido") for k, r in [("autor", "Autor"), ("ano", "Ano"), ("idioma", "Idioma"),
                                                           ("fonte", "Fonte")]]
    avisos = [a["mensagem"] for a in registo.get("qualidade", [])]
    notas = ("<ul>" + "".join(f"<li>{html.escape(a)}</li>" for a in avisos) + "</ul>" if avisos else
             "<p>Sem avisos: o texto passou todas as verificações automáticas de qualidade.</p>")
    leitura_html = _escala_leitura(i, lg)
    if not leitura_html and "legibilidade" in e:
        leitura_html = (f'<p class="aviso-estado leitura-na">Legibilidade não aplicável: '
                        f'{html.escape(e["legibilidade"]["motivo"])}.</p>')
    resumo = (leitura_html + '<div class="notas-bloco"><h3>Notas sobre os Dados</h3><div class="notas">'
              f'{notas}<p>Cada indicador tem definição, unidade e limitações no <a href="README.md">relatório '
              "completo</a>.</p></div></div>")

    extras = {}
    extras["gramatica"] = _mini([(v("frases_interrogativas_pct", 1) + " %", "frases interrogativas"),
                                 (v("frases_exclamativas_pct", 1) + " %", "frases exclamativas"),
                                 (v("verbos_passado_pct", 0) + " %", "verbos no passado"),
                                 (v("verbos_presente_pct", 0) + " %", "verbos no presente"),
                                 (v("pronomes_1a_pessoa_por_1000", 1), "pronomes de 1.ª pessoa / 1000"),
                                 (v("pronomes_3a_pessoa_por_1000", 1), "pronomes de 3.ª pessoa / 1000")])
    extras["leis"] = _mini([(v("zipf_expoente", 2), "expoente de Zipf (s)"), (v("zipf_r2", 3), "ajuste de Zipf (R²)"),
                            (v("heaps_beta", 3), "expoente de Heaps (β)"), (v("heaps_r2", 3), "ajuste de Heaps (R²)")])
    if "sentimento_medio" in e:
        extras["sentimento"] = (f'<p class="aviso-estado">Sentimento não calculado: '
                                f'{html.escape(e["sentimento_medio"]["motivo"])}.</p>')
    else:
        citacoes = ""
        ext = extra.get("extremos")
        if ext is not None and len(ext):
            for pol, rot in [("positiva", "Frases Mais Positivas"), ("negativa", "Frases Mais Negativas")]:
                sub = ext[ext.polaridade == pol]
                if len(sub):
                    citacoes += (f'<div><h3>{rot}</h3>' + "".join(
                        f'<blockquote class="{pol}"><p>{html.escape(x.texto)}</p><cite>{_num(x.sentimento, 3)}</cite>'
                        "</blockquote>" for x in sub.itertuples()) + "</div>")
            citacoes = f'<div class="citacoes">{citacoes}</div>'
        extras["sentimento"] = _mini([(v("sentimento_medio", 3), "sentimento médio"),
                                      (v("frases_positivas_pct", 1) + " %", "frases positivas"),
                                      (v("frases_negativas_pct", 1) + " %", "frases negativas"),
                                      (v("cobertura_lexico_pct", 1) + " %", "palavras cobertas pelo léxico")]) + citacoes

    itens = figuras_livro(freq, classes, comprimentos, evol, ents, pers, g, extra, lg)
    p = registo["processamento"]
    tecnico = [("Modelo linguístico", registo["modelo_spacy"]),
               ("Sentimento", registo.get("metodo_sentimento") or "—"),
               ("Personagens", registo.get("metodo_personagens") or "—"),
               ("Versão", p["versao"]), ("Código", p["versao_codigo"])]
    tecnico += [("Commit", p["commit"])] if p.get("commit") else []
    tecnico += [("Processado em", p["data"])]
    rodape = dict(descricao=DESCRICAO, autoria=AUTORIA,
                  aviso="Ligações entre personagens indicam co-ocorrência, não relações narrativas comprovadas.",
                  ligacoes=[("Relatório Completo do Livro", "README.md"), ("Todos os Livros Analisados", "../../painel.html"),
                            ("Dados em Excel", f"{destino.parent.name}.xlsx"), ("Repositório no GitHub", REPOSITORIO)],
                  tecnico=tecnico)
    rosto = [(r, x) for r, x in [("Forma", "Verso" if registo.get("forma") == "verso" else ""),
                                  ("Versos", v("versos", 0) if registo.get("forma") == "verso" else ""),
                                  ("Palavras", v("palavras", 0)), ("Leitura", maiusculas(i.get("legibilidade_leitura") or "")),
                                  ("Tempo de leitura", f"{v('tempo_leitura_horas', 1)} h")] if x]
    pagina(registo["titulo"], registo.get("autor") or "", numeros, itens, resumo, rodape, offline, destino,
           antetitulo="Análise do Livro", dados_rosto=rosto, ficha=ficha, seccoes=SECCOES, extras=extras,
           ligacao_corpus="../../painel.html")


def painel_corpus(t: pd.DataFrame, destino: Path, offline: bool = False):
    if t.empty:
        return
    t = t.copy()
    t["rotulo"] = t.titulo.fillna(t.id).str.slice(0, 45)
    validos = t.dropna(subset=["frase_mediana", "mtld", "profundidade_media"])
    f2 = go.Figure()
    for lg, sub in t.groupby("lingua"):
        f2.add_scatter(x=sub.frase_mediana, y=sub.mtld, mode="markers+text", text=sub.rotulo, textposition="top center",
                       name=tema.LINGUAS.get(lg, (0, 0, lg))[2],
                       marker=dict(size=13 + 40 * np.sqrt(sub.palavras / t.palavras.max()), symbol=SIMBOLOS_LINGUA.get(lg),
                                   color=CORES_LINGUA.get(lg, SUAVE), opacity=0.9, line=dict(color=PAPEL, width=1.5)),
                       hovertemplate="<b>%{text}</b><br>Frase mediana: %{x:.0f} palavras<br>MTLD: %{y:.1f}<extra></extra>")
    fx = max((t.frase_mediana.max() - t.frase_mediana.min()) * 0.25, 1)
    fy = max((t.mtld.max() - t.mtld.min()) * 0.2, 5) if t.mtld.notna().any() else 5
    f2.update_xaxes(title="extensão mediana das frases (palavras)", range=[t.frase_mediana.min() - fx, t.frase_mediana.max() + fx])
    f2.update_yaxes(title="diversidade lexical (MTLD)", range=[(t.mtld.min() or 0) - fy, (t.mtld.max() or 0) + fy])
    _layout(f2, "Extensão das frases e diversidade lexical", altura=560,
            legend=dict(orientation="h", y=-0.16, x=0, yanchor="top"))
    itens = []
    if len(validos):
        simb3d = {"pt": "circle", "fr": "square", "en": "diamond"}
        f3 = g3d.dispersao(list(validos.frase_mediana), list(validos.mtld), list(validos.profundidade_media),
                           texto=list(validos.rotulo), tamanho=list(9 + 22 * np.sqrt(validos.palavras / t.palavras.max())),
                           cores=[CORES_LINGUA.get(l, SUAVE) for l in validos.lingua],
                           simbolos=[simb3d.get(l, "circle") for l in validos.lingua],
                           titulos=("frase mediana (palavras)", "MTLD", "profundidade sintática"),
                           customdata=np.c_[validos.palavras, validos.lingua],
                           hover="<b>%{text}</b><br>Frase mediana: %{x:.0f}<br>MTLD: %{y:.1f}<br>Profundidade: %{z:.2f}"
                                 "<br>Palavras: %{customdata[0]}<br>Língua: %{customdata[1]}<extra></extra>")
        _layout(f3, "Extensão das frases, diversidade lexical e profundidade sintática<br><sup>Tamanho = número de "
                    "palavras; cor e forma = língua</sup>", altura=640,
                nota=NOTA_3D + " Os níveis de MTLD e de profundidade não são comparáveis entre línguas.")
        itens.append(_item("comparacao", f3, f2))
    else:
        itens.append(_item("comparacao", f2))
    e = html.escape
    linhas = "".join(
        f'<tr><td><a href="livros/{r.id}/painel.html">{e(str(r.titulo))}</a></td><td>{e(str(r.autor or "—"))}</td>'
        f'<td>{r.lingua}</td><td class="n">{_num(r.palavras, 0)}</td><td class="n">{_num(r.mtld)}</td>'
        f'<td class="n">{_num(r.frase_mediana, 0)}</td><td class="n">{_num(getattr(r, "sentimento_medio", None), 3)}</td>'
        f'<td class="n">{_num(r.legibilidade, 0)}</td><td>{e(maiusculas(str(getattr(r, "legibilidade_leitura", "") or "—")))}</td></tr>'
        for r in t.sort_values(["lingua", "titulo"]).itertuples())
    tabela = ('<div class="tabela"><table><tr><th>Livro</th><th>Autor</th><th>Língua</th><th class="n">Palavras</th>'
              '<th class="n">MTLD</th><th class="n">Frase Mediana</th><th class="n">Sentimento</th>'
              f'<th class="n">Legibilidade</th><th>Leitura</th></tr>{linhas}</table></div>')
    numeros = [(str(len(t)), "", "livros analisados"), (_num(int(t.palavras.sum()), 0), "", "palavras no total"),
               (str(t.lingua.nunique()), "", "línguas")]
    seccoes = {"comparacao": ("Comparação", "Cada ponto é um livro. Compare apenas livros da mesma língua: a "
                                            "legibilidade, o MTLD e o sentimento dependem da língua.")}
    rodape = dict(descricao=DESCRICAO, autoria=AUTORIA,
                  aviso="A legibilidade e o sentimento usam fórmulas e léxicos diferentes em cada língua.",
                  ligacoes=[("Relatório do Corpus", "README.md"), ("Dados em Excel", "indicadores.xlsx"),
                            ("Repositório no GitHub", REPOSITORIO)],
                  tecnico=[("Livros", str(len(t))), ("Línguas", ", ".join(sorted(t.lingua.unique())))])
    pagina("Livros Analisados", "", numeros, itens, tabela, rodape, offline, destino, antetitulo="Corpus",
           dados_rosto=[("Livros", str(len(t))), ("Palavras", _num(int(t.palavras.sum()), 0))], seccoes=seccoes)
