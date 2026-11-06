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
        if p.lower() in MENORES and not inicio:
            saida.append(p.lower())
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
    "personagens": ("Personagens", "Quem aparece com quem. Uma ligação significa que as duas personagens surgem no mesmo "
                                   "parágrafo; não prova uma relação narrativa."),
    "vocabulario": ("Vocabulário e gramática", "As palavras de conteúdo mais frequentes e o peso de cada classe "
                                               "gramatical, por 1000 palavras."),
    "frases": ("Frases e evolução", "Como se distribui a extensão das frases e como alguns indicadores variam do "
                                    "início ao fim do livro."),
    "lugares": ("Lugares", "Espaços nomeados, identificados automaticamente; contam como estimativa."),
}


def figuras_livro(freq, classes, comprimentos, evol, ents, pers, g) -> list[tuple[str, go.Figure]]:
    figs: list[tuple[str, go.Figure]] = []
    f3d = rede_3d(g)
    if f3d is not None:
        figs.append(("personagens", f3d))
    if not pers.empty:
        top = pers.head(20).iloc[::-1]
        fig = go.Figure(go.Bar(x=top.pagerank, y=top.personagem, orientation="h",
                               marker=dict(color=[COMUNIDADES[(c - 1) % len(COMUNIDADES)] for c in top.comunidade],
                                           line=dict(width=0)),
                               text=[f"C{c}" for c in top.comunidade], textposition="inside",
                               insidetextfont=dict(color=FUNDO, size=10),
                               customdata=top[["mencoes", "grau", "intermediacao", "comunidade"]],
                               hovertemplate="<b>%{y}</b><br>PageRank: %{x:.3f}<br>Menções: %{customdata[0]}"
                                             "<br>Ligações: %{customdata[1]}<br>Intermediação: %{customdata[2]:.3f}"
                                             "<br>Comunidade: %{customdata[3]}<extra></extra>"))
        figs.append(("personagens", _layout(fig, "Personagens mais centrais<br><sup>PageRank na rede de co-ocorrência; "
                                                 "C1, C2… = comunidade</sup>", altura=560)))

    top = freq.head(30).iloc[::-1]
    fig = go.Figure()
    for classe, sub in top.groupby("pos", observed=True, sort=False):
        fig.add_bar(x=sub.por_1000_palavras, y=sub.lema, orientation="h", name=NOMES_CLASSES.get(classe, classe),
                    marker=dict(color=CORES_CLASSES.get(classe, SUAVE), line=dict(width=0)),
                    hovertemplate="<b>%{y}</b>: %{x:.2f} por 1000 palavras<extra></extra>")
    fig.update_yaxes(categoryorder="array", categoryarray=list(top.lema))
    fig.update_xaxes(title="ocorrências por 1000 palavras")
    figs.append(("vocabulario", _layout(fig, "Palavras de conteúdo mais frequentes<br><sup>Lemas de substantivos, "
                                             "verbos, adjetivos e advérbios</sup>", altura=680, barmode="stack",
                                        legend=dict(orientation="h", y=-0.08, x=0, yanchor="top"))))

    c = classes.sort_values("por_1000_palavras")
    fig = go.Figure(go.Bar(x=c.por_1000_palavras, y=c.nome, orientation="h", marker=dict(color=CASTANHO, line=dict(width=0)),
                           customdata=c.ocorrencias, hovertemplate="<b>%{y}</b><br>%{x:.1f} por 1000 palavras"
                                                                  "<br>%{customdata:,} ocorrências<extra></extra>"))
    fig.update_xaxes(title="ocorrências por 1000 palavras")
    figs.append(("vocabulario", _layout(fig, "Classes gramaticais<br><sup>Etiquetas UPOS por 1000 palavras</sup>",
                                        altura=480)))

    c = comprimentos[comprimentos > 0]
    if len(c):
        limite = max(int(c.quantile(0.99)), 1)
        fig = go.Figure(go.Histogram(x=c.clip(upper=limite), xbins=dict(start=0.5, end=limite + 0.5, size=1),
                                     marker=dict(color="#B08B68", line=dict(color=PAPEL, width=0.6)),
                                     hovertemplate="%{x} palavras: %{y} frases<extra></extra>"))
        fig.add_vline(x=c.median(), line=dict(color=TINTA, width=2, dash="dot"),
                      annotation_text=f"mediana {c.median():.0f}", annotation_position="top right",
                      annotation_font=dict(color=TINTA))
        fig.update_xaxes(title="palavras por frase (até ao percentil 99)")
        fig.update_yaxes(title="frases")
        figs.append(("frases", _layout(fig, "Extensão das frases<br><sup>Distribuição; extensão não equivale a "
                                            "complexidade sintática</sup>", altura=480, bargap=0.04)))

    if len(evol) >= 3:
        from plotly.subplots import make_subplots

        series = [("mtld", "Diversidade lexical (MTLD)", ".1f", CASTANHO),
                  ("frase_media", "Extensão média das frases", ".1f", TINTA),
                  ("dialogo_pct", "Parágrafos de diálogo (%)", ".0f", OCRE)]
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=[maiusculas(rot) for _, rot, _, _ in series])
        for k, (col, rot, fmt, cor) in enumerate(series, start=1):
            fig.add_scatter(x=evol.segmento, y=evol[col], mode="lines+markers", name=rot, showlegend=False,
                            line=dict(color=cor, width=2.5), marker=dict(size=7, color=cor, line=dict(color=FUNDO, width=1)),
                            row=k, col=1, hovertemplate=f"{rot}<br>segmento %{{x}}: %{{y:{fmt}}}<extra></extra>")
        fig.update_xaxes(dtick=1)
        fig.update_xaxes(title="segmento do livro (início → fim)", row=3, col=1)
        _layout(fig, "Evolução ao longo do livro<br><sup>O livro é dividido em segmentos com o mesmo número de "
                     "palavras</sup>", altura=600)
        fig.update_layout(margin=dict(t=34))
        for a in fig.layout.annotations:
            a.update(x=0, xanchor="left", font=dict(size=12, color=SUAVE))
        figs.append(("frases", fig))

    lugares = ents[ents.tipo == "lugar"].head(15).iloc[::-1] if not ents.empty else ents
    if len(lugares):
        fig = go.Figure(go.Bar(x=lugares.ocorrencias, y=lugares.entidade, orientation="h",
                               marker=dict(color=CAQUI, line=dict(width=0)),
                               hovertemplate="<b>%{y}</b>: %{x} menções<extra></extra>"))
        fig.update_xaxes(title="menções")
        figs.append(("lugares", _layout(fig, "Lugares mais mencionados<br><sup>Estimativa do reconhecimento de "
                                             "entidades (NER)</sup>", altura=500)))
    return figs


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
.barra{position:relative;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:14px 0;
border-bottom:1px solid rgba(243,234,219,.14);font-family:var(--ui);font-size:13px;letter-spacing:.08em;color:var(--areia)}
.barra a{color:var(--areia);border:0}.barra a:hover{color:var(--creme)}
.marca{display:flex;align-items:center;gap:10px;font-family:var(--display);font-size:20px;letter-spacing:.02em;
color:var(--creme);font-weight:600}
.marca img{width:26px;height:26px}
.rosto{position:relative;display:grid;grid-template-columns:auto 1fr;gap:44px;align-items:center;padding:64px 0 56px}
.selo{width:168px;height:168px;border-radius:50%;padding:7px;background:conic-gradient(from 210deg,var(--ocre),#6b4b26,var(--ocre),#e2c58f,var(--ocre));
box-shadow:0 18px 50px rgba(0,0,0,.45)}
.selo img{width:100%;height:100%;border-radius:50%;display:block}
.antetitulo{font-family:var(--display);font-style:italic;font-size:22px;color:var(--ocre);margin:0 0 4px}
.rosto h1{font-family:var(--display);font-weight:600;font-size:clamp(46px,7.4vw,92px);line-height:.98;margin:0;
letter-spacing:-.01em}
.autoria{font-family:var(--display);font-style:italic;font-size:clamp(22px,2.6vw,30px);color:var(--areia);margin:12px 0 0}
.ornamento{display:flex;align-items:center;gap:14px;color:var(--ocre);margin:26px 0 18px;max-width:520px}
.ornamento:before,.ornamento:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--ocre),transparent)}
.dados-rosto{display:flex;flex-wrap:wrap;gap:6px 26px;font-family:var(--ui);font-size:14px;color:var(--areia);
letter-spacing:.03em;margin:0;padding:0;list-style:none}
.dados-rosto b{color:var(--creme);font-weight:600}

/* índice */
.indice{position:sticky;top:0;z-index:10;background:var(--papel);border-bottom:1px solid var(--linha)}
.indice .envolve{display:flex;gap:0;overflow-x:auto;scrollbar-width:none}
.indice a{flex:none;border:0;padding:15px 18px 13px;font-family:var(--ui);font-size:14px;color:var(--suave);
border-bottom:2px solid transparent}
.indice a span{font-family:var(--display);font-style:italic;color:var(--ocre);margin-right:6px;font-size:16px}
.indice a:hover{color:var(--tinta);border-bottom-color:var(--castanho)}

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
    return f"{v:.{casas}f}".replace(".", ",")


def _div(fig: go.Figure, primeira: bool, offline: bool) -> str:
    return pio.to_html(fig, full_html=False, include_plotlyjs=("inline" if offline else "cdn") if primeira else False,
                       config={"displaylogo": False, "responsive": True, "scrollZoom": False,
                               "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
                               "toImageButtonOptions": {"format": "png", "scale": 2}})


def _figura(fig: go.Figure, primeira: bool, offline: bool) -> str:
    meta = fig.layout.meta or {}
    e = html.escape
    return (f'<figure class="figura"><h3>{e(meta.get("titulo", ""))}</h3>'
            + (f'<p class="sub">{e(meta["subtitulo"])}</p>' if meta.get("subtitulo") else "")
            + _div(fig, primeira, offline)
            + (f'<p class="nota">{e(meta["nota"])}</p>' if meta.get("nota") else "") + "</figure>")


def pagina(titulo: str, autoria: str, numeros: list[tuple[str, str, str]], figs: list[tuple[str, go.Figure]],
           ficha_html: str, rodape: dict, offline: bool, destino: Path, antetitulo: str = "Análise do Livro",
           dados_rosto: list[tuple[str, str]] | None = None, seccoes: dict | None = None,
           ligacao_corpus: str | None = None):
    """Escreve a página. `numeros` = (valor, unidade, rótulo); `rodape` = ligações e dados técnicos."""
    e = html.escape
    seccoes = seccoes or {}
    ordem = list(dict.fromkeys(chave for chave, _ in figs))
    corpo, primeira = [], True
    for n, chave in enumerate(ordem, start=2):
        nome, lede = seccoes.get(chave, (chave.capitalize(), ""))
        largos, pares = [], []
        for k, f in figs:
            if k != chave:
                continue
            bloco = _figura(f, primeira, offline)
            primeira = False
            (largos if (f.layout.height or 0) >= 560 else pares).append(bloco)
        if len(pares) == 1:          # um gráfico pequeno sozinho ocupa a largura toda
            largos, pares = largos + pares, []
        miolo = "".join(largos) + (f'<div class="par">{"".join(pares)}</div>' if pares else "")
        corpo.append(f'<section class="seccao" id="{chave}"><div class="cab-seccao"><span class="num">'
                     f'{ROMANOS[(n - 1) % 10]}</span><h2>{e(maiusculas(nome))}</h2></div>'
                     + (f'<p class="lede">{e(lede)}</p>' if lede else "") + miolo + "</section>")
    indice = '<a href="#resumo"><span>I</span>Resumo</a>' + "".join(
        f'<a href="#{k}"><span>{ROMANOS[n - 1]}</span>{e(maiusculas(seccoes.get(k, (k.capitalize(),))[0]))}</a>'
        for n, k in enumerate(ordem, start=2))
    blocos = "".join(f'<div class="numero"><b>{e(v)}{f"<small>{e(u)}</small>" if u else ""}</b>'
                     f'<span>{e(maiusculas(r))}</span></div>' for v, u, r in numeros)
    rosto = "".join(f"<li>{e(r)} <b>{e(v)}</b></li>" for r, v in (dados_rosto or []))
    icone32, icone128 = _icone(32), _icone(128)
    cabeca = (f'<link rel="icon" type="image/png" sizes="32x32" href="{icone32}">'
              f'<link rel="apple-touch-icon" href="{icone128}">') if icone32 else ""
    voltar = f'<a href="{ligacao_corpus}">Todos os Livros</a>' if ligacao_corpus else ""
    ligacoes = "".join(f'<li><a href="{e(u)}">{e(t)}</a></li>' for t, u in rodape["ligacoes"])
    tecnico = "".join(f"<li>{e(t)} <code>{e(v)}</code></li>" for t, v in rodape["tecnico"])
    destino.write_text(f"""<!doctype html>
<html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)} · Livros-PLN</title><meta name="theme-color" content="#1E1915">
<meta name="description" content="{e(antetitulo)}: {e(titulo)}. Indicadores linguísticos, rede de personagens e estilo.">
{cabeca}{FONTES_WEB}<style>{CSS}</style></head>
<body>
<header class="cabecalho"><div class="envolve">
 <div class="barra"><span class="marca"><img src="{icone32}" alt="">Livros-PLN</span>
  <span class="lema">Análise Computacional de Textos Literários</span>{voltar}</div>
 <div class="rosto"><div class="selo"><img src="{icone128}" alt="Ícone do Livros-PLN"></div>
  <div><p class="antetitulo">{e(antetitulo)}</p><h1>{e(titulo)}</h1>
  {f'<p class="autoria">{e(autoria)}</p>' if autoria else ''}
  <div class="ornamento">❦</div><ul class="dados-rosto">{rosto}</ul></div></div>
</div></header>
<nav class="indice" aria-label="Índice"><div class="envolve">{indice}</div></nav>
<main class="envolve"><section id="resumo"><div class="numeros">{blocos}</div>{ficha_html}</section>{''.join(corpo)}</main>
<footer class="rodape"><div class="envolve">
 <div class="topo">
  <div><span class="marca"><img src="{icone128}" alt="">Livros-PLN</span>
   <p>{e(rodape["descricao"])}</p></div>
  <div><h4>Explorar</h4><ul>{ligacoes}</ul></div>
  <div><h4>Esta Análise</h4><ul>{tecnico}</ul></div>
 </div>
 <div class="base"><span>{e(rodape["autoria"])}</span><span>{e(rodape["aviso"])}</span></div>
</div></footer>
<script>window.addEventListener("load",()=>{{if(window.Plotly)document.querySelectorAll(".js-plotly-plot").forEach(g=>Plotly.Plots.resize(g))}});</script>
</body></html>
""", encoding="utf-8")


DESCRICAO = ("Indicadores linguísticos, estilométricos e de rede de personagens para livros em português, francês e "
             "inglês, com definição, limitações e referência para cada valor.")
AUTORIA = "© João Garção · Código com todos os direitos reservados"


def painel_livro(registo: dict, freq, classes, comprimentos, evol, ents, pers, g, destino: Path, offline: bool = False):
    i, m, e = registo["indicadores"], registo["metadados"], registo["estados"]

    def v(chave, casas=1):
        return "n.a." if chave in e else tema.num(i.get(chave), casas)

    escala = i.get("legibilidade_escala")
    numeros = [(v("palavras", 0), "", "palavras"),
               (v("mtld"), "", "diversidade lexical (MTLD)"),
               (v("frase_mediana", 0), "palavras", "extensão mediana das frases"),
               (v("profundidade_media", 2), "", "profundidade sintática média"),
               (v("legibilidade", 0), escala or "", "legibilidade (Flesch adaptado)"),
               (v("personagens_na_rede", 0), "", "personagens na rede")]
    ficha = [(r, m.get(k)) for k, r in [("autor", "Autor"), ("ano", "Ano"), ("data", "Data"), ("editora", "Editora"),
                                         ("tradutor", "Tradutor"), ("identificador", "Identificador"), ("fonte", "Fonte")]
             if m.get(k)]
    ficha += [("Língua", maiusculas(registo["lingua_nome"])), ("Modelo linguístico", registo["modelo_spacy"]),
              ("Personagens", registo.get("metodo_personagens", "—"))]
    avisos = [a["mensagem"] for a in registo.get("qualidade", [])]
    notas = ("<ul>" + "".join(f"<li>{html.escape(a)}</li>" for a in avisos) + "</ul>" if avisos else
             "<p>Sem avisos: o texto passou todas as verificações automáticas de qualidade.</p>")
    ficha_html = ('<div class="ficha"><div><h3>Ficha Técnica</h3><dl>'
                  + "".join(f"<div><dt>{html.escape(r)}</dt><dd>{html.escape(str(x))}</dd></div>" for r, x in ficha)
                  + f'</dl></div><div><h3>Notas sobre os Dados</h3><div class="notas">{notas}'
                  '<p>Cada indicador tem definição, unidade e limitações no <a href="README.md">relatório completo</a>.'
                  "</p></div></div></div>")
    figs = figuras_livro(freq, classes, comprimentos, evol, ents, pers, g)
    p = registo["processamento"]
    tecnico = [("Versão", p["versao"]), ("Código", p["versao_codigo"])]
    tecnico += [("Commit", p["commit"])] if p.get("commit") else []
    tecnico += [("Processado em", p["data"])]
    rodape = dict(descricao=DESCRICAO, autoria=AUTORIA,
                  aviso="Ligações entre personagens indicam co-ocorrência, não relações narrativas comprovadas.",
                  ligacoes=[("Relatório Completo do Livro", "README.md"), ("Todos os Livros Analisados", "../../painel.html"),
                            ("Dados em Excel", f"{destino.parent.name}.xlsx"), ("Repositório no GitHub", REPOSITORIO)],
                  tecnico=tecnico)
    rosto = [(r, x) for r, x in [("Ano", str(registo.get("ano") or "")), ("Língua", maiusculas(registo["lingua_nome"])),
                                  ("Palavras", v("palavras", 0)), ("Fonte", m.get("fonte") or "")] if x]
    pagina(registo["titulo"], registo.get("autor") or "", numeros, figs, ficha_html, rodape, offline, destino,
           antetitulo="Análise do Livro", dados_rosto=rosto, seccoes=SECCOES, ligacao_corpus="../../painel.html")


def painel_corpus(t: pd.DataFrame, destino: Path, offline: bool = False):
    if t.empty:
        return
    t = t.copy()
    t["rotulo"] = t.titulo.fillna(t.id).str.slice(0, 45)
    fig = go.Figure()
    for lg, sub in t.groupby("lingua"):
        fig.add_scatter(x=sub.frase_mediana, y=sub.mtld, mode="markers+text", text=sub.rotulo, textposition="top center",
                        name=tema.LINGUAS.get(lg, (0, 0, lg))[2],
                        marker=dict(size=13 + 40 * np.sqrt(sub.palavras / t.palavras.max()), symbol=SIMBOLOS_LINGUA.get(lg),
                                    color=CORES_LINGUA.get(lg, SUAVE), opacity=0.9, line=dict(color=PAPEL, width=1.5)),
                        customdata=sub[["palavras", "profundidade_media"]],
                        hovertemplate="<b>%{text}</b><br>Frase mediana: %{x:.0f} palavras<br>MTLD: %{y:.1f}"
                                      "<br>Palavras: %{customdata[0]:,}<br>Profundidade: %{customdata[1]:.2f}<extra></extra>")
    fx = max((t.frase_mediana.max() - t.frase_mediana.min()) * 0.25, 1)
    fy = max((t.mtld.max() - t.mtld.min()) * 0.2, 5) if t.mtld.notna().any() else 5
    fig.update_xaxes(title="extensão mediana das frases (palavras)", range=[t.frase_mediana.min() - fx, t.frase_mediana.max() + fx])
    fig.update_yaxes(title="diversidade lexical (MTLD)", range=[(t.mtld.min() or 0) - fy, (t.mtld.max() or 0) + fy])
    figs = [("comparacao", _layout(fig, "Extensão das frases e diversidade lexical<br><sup>Tamanho = número de "
                                         "palavras; forma = língua</sup>", altura=600,
                                    nota="Os níveis de MTLD não são comparáveis entre línguas.",
                                    legend=dict(orientation="h", y=-0.16, x=0, yanchor="top")))]
    e = html.escape
    linhas = "".join(
        f'<tr><td><a href="livros/{r.id}/painel.html">{e(str(r.titulo))}</a></td><td>{e(str(r.autor or "—"))}</td>'
        f'<td>{r.lingua}</td><td class="n">{_num(r.palavras, 0)}</td><td class="n">{_num(r.mtld)}</td>'
        f'<td class="n">{_num(r.frase_mediana, 0)}</td><td class="n">{_num(r.profundidade_media, 2)}</td>'
        f'<td class="n">{_num(r.legibilidade, 0)}</td></tr>'
        for r in t.sort_values(["lingua", "titulo"]).itertuples())
    tabela = ('<div class="tabela"><table><tr><th>Livro</th><th>Autor</th><th>Língua</th><th class="n">Palavras</th>'
              '<th class="n">MTLD</th><th class="n">Frase Mediana</th><th class="n">Profundidade</th>'
              f'<th class="n">Legibilidade</th></tr>{linhas}</table></div>')
    numeros = [(str(len(t)), "", "livros analisados"), (_num(int(t.palavras.sum()), 0), "", "palavras no total"),
               (str(t.lingua.nunique()), "", "línguas")]
    seccoes = {"comparacao": ("Comparação", "Cada ponto é um livro. Compare apenas livros da mesma língua: a "
                                            "legibilidade e o MTLD dependem da língua.")}
    rodape = dict(descricao=DESCRICAO, autoria=AUTORIA,
                  aviso="A legibilidade usa fórmulas diferentes em cada língua.",
                  ligacoes=[("Relatório do Corpus", "README.md"), ("Dados em Excel", "indicadores.xlsx"),
                            ("Repositório no GitHub", REPOSITORIO)],
                  tecnico=[("Livros", str(len(t))), ("Línguas", ", ".join(sorted(t.lingua.unique())))])
    pagina("Livros Analisados", "", numeros, figs, tabela, rodape, offline, destino, antetitulo="Corpus",
           dados_rosto=[("Livros", str(len(t))), ("Palavras", _num(int(t.palavras.sum()), 0))], seccoes=seccoes)
