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
GRELHA = "#E9E0D0"
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
FONTE = "Inter, -apple-system, Segoe UI, Helvetica Neue, Arial, sans-serif"
FONTE_TITULOS = "Fraunces, Georgia, Times New Roman, serif"
RECURSOS = Path(__file__).parent / "recursos"


def _layout(fig: go.Figure, titulo: str, altura: int = 420, **extra) -> go.Figure:
    fig.update_layout(title=dict(text=titulo, x=0.01, xanchor="left", font=dict(size=17, color=TINTA,
                                                                               family=FONTE_TITULOS)),
                      font=dict(family=FONTE, color=TINTA, size=12), paper_bgcolor=FUNDO, plot_bgcolor=FUNDO,
                      margin=dict(l=14, r=14, t=64, b=14), height=altura,
                      hoverlabel=dict(font_family=FONTE, bgcolor=TINTA, font_color="#F3EADB", bordercolor=TINTA),
                      separators=", ", **extra)  # vírgula decimal e espaço como separador de milhares
    fig.update_xaxes(gridcolor=GRELHA, zeroline=False, linecolor=GRELHA, tickfont=dict(color=SUAVE),
                     title_font=dict(color=SUAVE))
    fig.update_yaxes(gridcolor=GRELHA, zeroline=False, linecolor=GRELHA, tickfont=dict(color=SUAVE),
                     title_font=dict(color=SUAVE))
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
            textfont=dict(size=11, color=TINTA, family=FONTE),
            marker=dict(size=[7 + 30 * math.sqrt(g.nodes[n]["mencoes"] / maximo) for n in nos],
                        color=COMUNIDADES[(com - 1) % len(COMUNIDADES)], opacity=0.93,
                        symbol=SIMBOLOS_3D[(com - 1) % len(SIMBOLOS_3D)],
                        line=dict(color=FUNDO, width=1.5)),
            customdata=[[g.nodes[n]["mencoes"], g.degree(n), g.degree(n, weight="peso")] for n in nos],
            hovertemplate="<b>%{text}</b><br>Menções: %{customdata[0]}<br>Ligações: %{customdata[1]}"
                          "<br>Parágrafos partilhados: %{customdata[2]}<extra></extra>"))
    eixo = dict(visible=False, showbackground=False, showspikes=False)
    fig = go.Figure(traces)
    # sem animação nem rotação automática: é o leitor que roda a rede com o rato ou o dedo
    _layout(fig, titulo + "<br><sup>Arraste para rodar · roda do rato para aproximar · duplo clique repõe a vista</sup>", altura=720,
            scene=dict(xaxis=eixo, yaxis=eixo, zaxis=eixo, bgcolor=FUNDO, aspectmode="cube", dragmode="orbit",
                       camera=dict(eye=dict(x=1.15, y=1.15, z=0.7))),
            legend=dict(orientation="h", y=-0.02, x=0, font=dict(size=11)))
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
                                     marker=dict(color=AREIA, line=dict(color=FUNDO, width=0.5)),
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
                            subplot_titles=[rot for _, rot, _, _ in series])
        for k, (col, rot, fmt, cor) in enumerate(series, start=1):
            fig.add_scatter(x=evol.segmento, y=evol[col], mode="lines+markers", name=rot, showlegend=False,
                            line=dict(color=cor, width=2.5), marker=dict(size=7, color=cor, line=dict(color=FUNDO, width=1)),
                            row=k, col=1, hovertemplate=f"{rot}<br>segmento %{{x}}: %{{y:{fmt}}}<extra></extra>")
        fig.update_xaxes(dtick=1)
        fig.update_xaxes(title="segmento do livro (início → fim)", row=3, col=1)
        _layout(fig, "Evolução ao longo do livro<br><sup>O livro é dividido em segmentos com o mesmo número de "
                     "palavras</sup>", altura=600)
        fig.update_layout(margin=dict(t=100))
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
              '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&'
              'family=Inter:wght@400;500;600&display=swap" rel="stylesheet">')

CSS = """
:root{--papel:#F4EEE3;--cartao:#FBF8F2;--tinta:#1E1915;--suave:#6E5E4E;--linha:#E4D9C5;--castanho:#7A4E2D;
--ocre:#B8893E;--areia:#D9C7A3;--creme:#F3EADB;--serif:Fraunces,Georgia,"Times New Roman",serif;
--sans:Inter,-apple-system,"Segoe UI","Helvetica Neue",Arial,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:var(--sans);color:var(--tinta);background:var(--papel);line-height:1.5;
-webkit-font-smoothing:antialiased}
a{color:var(--castanho);text-decoration-color:var(--areia);text-underline-offset:3px}
a:hover{color:var(--tinta)}
.topo{background:var(--tinta);color:var(--creme);border-bottom:4px solid var(--ocre)}
.topo .dentro{max-width:1180px;margin:0 auto;padding:36px 20px 32px;display:flex;gap:22px;align-items:center}
.topo img{width:76px;height:76px;flex:none;border-radius:50%;box-shadow:0 0 0 3px rgba(243,234,219,.12)}
.topo .chapeu{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--ocre);margin:0 0 6px;font-weight:600}
.topo h1{font-family:var(--serif);font-weight:600;font-size:clamp(28px,4.4vw,44px);line-height:1.08;margin:0;
letter-spacing:-.01em}
.topo .sub{margin:8px 0 0;color:var(--areia);font-size:16px}
nav{position:sticky;top:0;z-index:5;background:rgba(244,238,227,.94);backdrop-filter:blur(6px);
border-bottom:1px solid var(--linha)}
nav .dentro{max-width:1180px;margin:0 auto;padding:10px 20px;display:flex;gap:8px;overflow-x:auto}
nav a{flex:none;text-decoration:none;color:var(--suave);font-size:13px;font-weight:500;padding:6px 12px;
border-radius:999px;border:1px solid transparent}
nav a:hover{color:var(--tinta);border-color:var(--linha);background:var(--cartao)}
main{max-width:1180px;margin:0 auto;padding:28px 20px 56px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:0 0 28px}
.card{background:var(--cartao);border:1px solid var(--linha);border-top:3px solid var(--castanho);border-radius:4px;
padding:16px 18px}
.card b{display:block;font-family:var(--serif);font-weight:600;font-size:28px;line-height:1.15;
font-variant-numeric:tabular-nums}
.card span{display:block;margin-top:6px;color:var(--suave);font-size:12px;letter-spacing:.04em;text-transform:uppercase}
section{margin:0 0 36px;scroll-margin-top:64px}
h2{font-family:var(--serif);font-weight:600;font-size:26px;margin:0 0 4px;letter-spacing:-.005em}
.lede{color:var(--suave);margin:0 0 16px;max-width:760px}
.bloco{background:var(--cartao);border:1px solid var(--linha);border-radius:4px;padding:10px;margin:0 0 16px;
box-shadow:0 1px 0 rgba(30,25,21,.03)}
.grelha{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(480px,100%),1fr));gap:16px}
.grelha .bloco{margin:0}
.meta{background:var(--cartao);border:1px solid var(--linha);border-radius:4px;padding:6px 18px;margin:0 0 28px}
table{border-collapse:collapse;width:100%;font-size:14px}
td,th{padding:9px 10px;border-bottom:1px solid var(--linha);text-align:left;vertical-align:top}
tr:last-child td,tr:last-child th{border-bottom:0}
th{color:var(--suave);font-weight:500;width:180px}
thead th,.cab th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;width:auto}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.avisos{background:#F7EEDC;border-left:4px solid var(--ocre);border-radius:4px;padding:12px 18px;margin:0 0 28px;
font-size:14px}
.avisos strong{display:block;font-family:var(--serif);font-size:16px;margin-bottom:4px}
.avisos ul{margin:0;padding-left:18px}
footer{border-top:1px solid var(--linha);color:var(--suave);font-size:12px;padding-top:16px;margin-top:8px}
.tabela-larga{overflow-x:auto}
@media(max-width:640px){.topo .dentro{padding:26px 16px;gap:14px}.topo img{width:54px;height:54px}
main{padding:20px 16px 40px}nav .dentro{padding:8px 16px}th{width:auto}.card b{font-size:23px}}
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


def pagina(titulo: str, subtitulo: str, cartoes: list[tuple[str, str]], figs: list[tuple[str, go.Figure]],
           tabela_html: str, rodape: str, offline: bool, destino: Path, chapeu: str = "livros-pln",
           seccoes: dict | None = None, avisos: list[str] | None = None):
    seccoes = seccoes or {}
    ordem = list(dict.fromkeys(chave for chave, _ in figs))
    corpo, primeira = [], True
    for chave in ordem:
        nome, lede = seccoes.get(chave, (chave.capitalize(), ""))
        largos, grelha = [], []
        for k, f in figs:
            if k != chave:
                continue
            div = f'<div class="bloco">{_div(f, primeira, offline)}</div>'
            primeira = False
            (largos if (f.layout.height or 0) >= 560 else grelha).append(div)
        miolo = "".join(largos) + (f'<div class="grelha">{"".join(grelha)}</div>' if grelha else "")
        corpo.append(f'<section id="{chave}"><h2>{html.escape(nome)}</h2>'
                     + (f'<p class="lede">{html.escape(lede)}</p>' if lede else "") + miolo + "</section>")
    navegacao = "".join(f'<a href="#{k}">{html.escape(seccoes.get(k, (k.capitalize(),))[0])}</a>' for k in ordem)
    cards = "".join(f'<div class="card"><b>{html.escape(v)}</b><span>{html.escape(r)}</span></div>' for r, v in cartoes)
    caixa = ("" if not avisos else '<div class="avisos"><strong>Qualidade dos dados</strong><ul>'
             + "".join(f"<li>{html.escape(a)}</li>" for a in avisos) + "</ul></div>")
    icone32, icone128 = _icone(32), _icone(128)
    cabeca_icone = (f'<link rel="icon" type="image/png" sizes="32x32" href="{icone32}">'
                    f'<link rel="apple-touch-icon" href="{icone128}">') if icone32 else ""
    imagem = f'<img src="{icone128}" alt="">' if icone128 else ""
    destino.write_text(f"""<!doctype html>
<html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)} · livros-pln</title><meta name="theme-color" content="#1E1915">{cabeca_icone}
{FONTES_WEB}<style>{CSS}</style></head>
<body><header class="topo"><div class="dentro">{imagem}<div><p class="chapeu">{html.escape(chapeu)}</p>
<h1>{html.escape(titulo)}</h1><p class="sub">{html.escape(subtitulo)}</p></div></div></header>
{f'<nav><div class="dentro"><a href="#resumo">Resumo</a>{navegacao}</div></nav>' if navegacao else ''}
<main><section id="resumo"><div class="cards">{cards}</div>{caixa}{tabela_html}</section>{''.join(corpo)}
<footer>{rodape}</footer></main>
<script>window.addEventListener("load",()=>{{if(window.Plotly)document.querySelectorAll(".js-plotly-plot").forEach(g=>Plotly.Plots.resize(g))}});</script>
</body></html>
""", encoding="utf-8")


def painel_livro(registo: dict, freq, classes, comprimentos, evol, ents, pers, g, destino: Path, offline: bool = False):
    i, m, e = registo["indicadores"], registo["metadados"], registo["estados"]

    def v(chave, casas=1):
        return "n.a." if chave in e else tema.num(i.get(chave), casas)

    cartoes = [("palavras", v("palavras", 0)), ("diversidade lexical (MTLD)", v("mtld")),
               ("extensão mediana das frases", f"{v('frase_mediana', 0)} palavras"),
               ("profundidade sintática", v("profundidade_media", 2)),
               ("legibilidade (Flesch adaptado)", f"{v('legibilidade', 0)} · {i.get('legibilidade_escala') or '—'}"),
               ("personagens na rede", v("personagens_na_rede", 0))]
    meta = [(r, m.get(k)) for k, r in [("autor", "Autor"), ("ano", "Ano"), ("data", "Data"), ("editora", "Editora"),
                                        ("tradutor", "Tradutor"), ("identificador", "Identificador"), ("fonte", "Fonte")]
            if m.get(k)]
    meta += [("Língua", f"{registo['lingua_nome']} (modelo {registo['modelo_spacy']})"),
             ("Personagens", registo.get("metodo_personagens", "—"))]
    tabela = '<div class="meta"><table>' + "".join(
        f"<tr><th>{html.escape(r)}</th><td>{html.escape(str(x))}</td></tr>" for r, x in meta) + "</table></div>"
    avisos = [a["mensagem"] for a in registo.get("qualidade", [])]
    figs = figuras_livro(freq, classes, comprimentos, evol, ents, pers, g)
    p = registo["processamento"]
    rodape = (f"livros-pln {p['versao']} · código {p['versao_codigo']}" + (f" · commit {p['commit']}" if p.get("commit") else "")
              + f" · processado em {p['data']} · definições e limitações dos indicadores no relatório "
              '<a href="README.md">README.md</a>')
    sub = " · ".join(x for x in [registo.get("autor"), str(registo.get("ano") or "")] if x)
    pagina(registo["titulo"], sub, cartoes, figs, tabela, rodape, offline, destino,
           chapeu="livros-pln · análise do livro", seccoes=SECCOES, avisos=avisos)


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
                                    color=CORES_LINGUA.get(lg, SUAVE), opacity=0.9, line=dict(color=FUNDO, width=1.5)),
                        customdata=sub[["palavras", "profundidade_media"]],
                        hovertemplate="<b>%{text}</b><br>Frase mediana: %{x:.0f} palavras<br>MTLD: %{y:.1f}"
                                      "<br>Palavras: %{customdata[0]:,}<br>Profundidade: %{customdata[1]:.2f}<extra></extra>")
    fx = max((t.frase_mediana.max() - t.frase_mediana.min()) * 0.25, 1)
    fy = max((t.mtld.max() - t.mtld.min()) * 0.2, 5) if t.mtld.notna().any() else 5
    fig.update_xaxes(title="extensão mediana das frases (palavras)", range=[t.frase_mediana.min() - fx, t.frase_mediana.max() + fx])
    fig.update_yaxes(title="diversidade lexical (MTLD)", range=[(t.mtld.min() or 0) - fy, (t.mtld.max() or 0) + fy])
    figs = [("comparacao", _layout(fig, "Extensão das frases e diversidade lexical<br><sup>Tamanho = número de palavras; "
                                         "os níveis de MTLD não são comparáveis entre línguas</sup>", altura=600,
                                    legend=dict(orientation="h", y=-0.16, x=0, yanchor="top")))]
    linhas = "".join(
        f'<tr><td><a href="livros/{r.id}/painel.html">{html.escape(str(r.titulo))}</a></td><td>{html.escape(str(r.autor or "—"))}</td>'
        f'<td>{r.lingua}</td><td class="n">{_num(r.palavras, 0)}</td><td class="n">{_num(r.mtld)}</td>'
        f'<td class="n">{_num(r.frase_mediana, 0)}</td><td class="n">{_num(r.profundidade_media, 2)}</td>'
        f'<td class="n">{_num(r.legibilidade, 0)}</td></tr>'
        for r in t.sort_values(["lingua", "titulo"]).itertuples())
    tabela = ('<div class="meta tabela-larga"><table><tr class="cab"><th>Livro</th><th>Autor</th><th>Língua</th>'
              '<th>Palavras</th><th>MTLD</th><th>Frase mediana</th><th>Profundidade</th><th>Legibilidade</th></tr>'
              f'{linhas}</table></div>')
    cartoes = [("livros", str(len(t))), ("palavras", _num(int(t.palavras.sum()), 0)),
               ("línguas", ", ".join(sorted(t.lingua.unique())))]
    seccoes = {"comparacao": ("Comparação", "Cada ponto é um livro. Compare apenas livros da mesma língua; a "
                                            "legibilidade e o MTLD dependem da língua.")}
    pagina("Livros analisados", "Comparação entre livros", cartoes, figs, tabela,
           "Clique num título para abrir o painel do livro. A legibilidade usa fórmulas diferentes em cada língua.",
           offline, destino, chapeu="livros-pln · corpus", seccoes=seccoes)
