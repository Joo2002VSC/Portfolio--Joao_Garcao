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

TINTA, SUAVE, FUNDO, GRELHA = tema.TINTA, tema.SUAVE, tema.FUNDO, tema.GRELHA
AZUL, VERMELHO, VERDE, OURO = tema.PETROLEO, tema.DESTAQUE, tema.VERDE_CINZA, tema.AMEIXA
COMUNIDADES = tema.SERIES
CORES_LINGUA = {lg: v[0] for lg, v in tema.LINGUAS.items()}
SIMBOLOS_LINGUA = {"pt": "circle", "fr": "square", "en": "triangle-up"}
FONTE = tema.PLOTLY_FONTE


def _layout(fig: go.Figure, titulo: str, altura: int = 420, **extra) -> go.Figure:
    fig.update_layout(title=dict(text=titulo, x=0, xanchor="left", font=dict(size=16, color=TINTA)),
                      font=dict(family=FONTE, color=TINTA, size=12), paper_bgcolor=FUNDO, plot_bgcolor=FUNDO,
                      margin=dict(l=10, r=10, t=56, b=10), height=altura, hoverlabel=dict(font_family=FONTE),
                      separators=", ", **extra)  # vírgula decimal e espaço como separador de milhares
    fig.update_xaxes(gridcolor=GRELHA, zeroline=False)
    fig.update_yaxes(gridcolor=GRELHA, zeroline=False)
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
                                       line=dict(color=f"rgba(90,105,125,{opacidade})", width=largura)))
    maximo = max(d["mencoes"] for _, d in g.nodes(data=True))
    for com in sorted({d.get("comunidade", 1) for _, d in g.nodes(data=True)}):
        nos = [n for n, d in g.nodes(data=True) if d.get("comunidade", 1) == com]
        traces.append(go.Scatter3d(
            x=[pos[n][0] for n in nos], y=[pos[n][1] for n in nos], z=[pos[n][2] for n in nos],
            mode="markers+text", name=f"Comunidade {com}", text=nos, textposition="top center",
            textfont=dict(size=11, color=TINTA, family=FONTE),
            marker=dict(size=[7 + 30 * math.sqrt(g.nodes[n]["mencoes"] / maximo) for n in nos],
                        color=COMUNIDADES[(com - 1) % len(COMUNIDADES)], opacity=0.92,
                        line=dict(color="#ffffff", width=1.5)),
            customdata=[[g.nodes[n]["mencoes"], g.degree(n), g.degree(n, weight="peso")] for n in nos],
            hovertemplate="<b>%{text}</b><br>Menções: %{customdata[0]}<br>Ligações: %{customdata[1]}"
                          "<br>Parágrafos partilhados: %{customdata[2]}<extra></extra>"))
    eixo = dict(visible=False, showbackground=False)
    fig = go.Figure(traces)
    _layout(fig, titulo, altura=720,
            scene=dict(xaxis=eixo, yaxis=eixo, zaxis=eixo, bgcolor=FUNDO, aspectmode="cube",
                       camera=dict(eye=dict(x=1.15, y=1.15, z=0.7))),
            legend=dict(orientation="h", y=-0.02, x=0, font=dict(size=11)))
    # botão para rodar a câmara à volta da rede
    frames = [go.Frame(layout=dict(scene_camera=dict(eye=dict(x=1.6 * math.cos(t), y=1.6 * math.sin(t), z=0.7))))
              for t in np.linspace(0, 2 * math.pi, 73)]
    fig.frames = frames
    fig.update_layout(updatemenus=[dict(type="buttons", showactive=False, x=1, xanchor="right", y=1.08, yanchor="top",
                                        buttons=[dict(label="⟳ Rodar", method="animate",
                                                      args=[None, dict(frame=dict(duration=60, redraw=True),
                                                                       transition=dict(duration=0),
                                                                       fromcurrent=True, mode="immediate")]),
                                                 dict(label="❚❚ Parar", method="animate",
                                                      args=[[None], dict(frame=dict(duration=0, redraw=False),
                                                                         mode="immediate")])])])
    return fig


# ---------------------------------------------------------------------------
# Gráficos por livro
# ---------------------------------------------------------------------------

def figuras_livro(freq, classes, comprimentos, evol, ents, pers, g) -> list[go.Figure]:
    figs = []
    f3d = rede_3d(g)
    if f3d is not None:
        figs.append(f3d)
    if not pers.empty:
        top = pers.head(20).iloc[::-1]
        fig = go.Figure(go.Bar(x=top.pagerank, y=top.personagem, orientation="h",
                               marker_color=[COMUNIDADES[(c - 1) % len(COMUNIDADES)] for c in top.comunidade],
                               customdata=top[["mencoes", "grau", "intermediacao", "comunidade"]],
                               hovertemplate="<b>%{y}</b><br>PageRank: %{x:.3f}<br>Menções: %{customdata[0]}"
                                             "<br>Ligações: %{customdata[1]}<br>Intermediação: %{customdata[2]:.3f}"
                                             "<br>Comunidade: %{customdata[3]}<extra></extra>"))
        figs.append(_layout(fig, "Personagens mais centrais<br><sup>PageRank na rede de co-ocorrência; cor = comunidade</sup>",
                            altura=540))

    top = freq.head(30).iloc[::-1]
    fig = go.Figure()
    for classe, sub in top.groupby("pos", observed=True, sort=False):
        fig.add_bar(x=sub.por_1000_palavras, y=sub.lema, orientation="h", name=NOMES_CLASSES.get(classe, classe),
                    marker_color=tema.CLASSES_CORES.get(classe, SUAVE),
                    hovertemplate="<b>%{y}</b>: %{x:.2f} por 1000 palavras<extra></extra>")
    fig.update_yaxes(categoryorder="array", categoryarray=list(top.lema))
    fig.update_xaxes(title="ocorrências por 1000 palavras")
    figs.append(_layout(fig, "Palavras de conteúdo mais frequentes<br><sup>Lemas de substantivos, verbos, adjetivos e "
                             "advérbios</sup>", altura=660, barmode="stack", legend=dict(orientation="h", y=-0.08, x=0, yanchor="top")))

    c = classes.sort_values("por_1000_palavras")
    fig = go.Figure(go.Bar(x=c.por_1000_palavras, y=c.nome, orientation="h", marker_color=AZUL,
                           customdata=c.ocorrencias, hovertemplate="<b>%{y}</b><br>%{x:.1f} por 1000 palavras"
                                                                  "<br>%{customdata:,} ocorrências<extra></extra>"))
    fig.update_xaxes(title="ocorrências por 1000 palavras")
    figs.append(_layout(fig, "Classes gramaticais<br><sup>Etiquetas UPOS por 1000 palavras</sup>", altura=470))

    c = comprimentos[comprimentos > 0]
    limite = int(c.quantile(0.99))
    fig = go.Figure(go.Histogram(x=c.clip(upper=limite), xbins=dict(start=0.5, end=limite + 0.5, size=1),
                                 marker_color=tema.PETROLEO_CLARO, hovertemplate="%{x} palavras: %{y} frases<extra></extra>"))
    fig.add_vline(x=c.median(), line=dict(color=AZUL, width=2), annotation_text=f"mediana {c.median():.0f}",
                  annotation_position="top right")
    fig.update_xaxes(title="palavras por frase (até ao percentil 99)")
    figs.append(_layout(fig, "Extensão das frases<br><sup>Distribuição; extensão não equivale a complexidade "
                             "sintática</sup>", altura=470, bargap=0.05))

    if len(evol) >= 3:
        from plotly.subplots import make_subplots

        series = [("mtld", "Diversidade lexical (MTLD)", ".1f"), ("frase_media", "Extensão média das frases", ".1f"),
                  ("dialogo_pct", "Parágrafos de diálogo (%)", ".0f")]
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.09,
                            subplot_titles=[rot for _, rot, _ in series])
        for k, (col, rot, fmt) in enumerate(series, start=1):
            fig.add_scatter(x=evol.segmento, y=evol[col], mode="lines+markers", name=rot, showlegend=False,
                            line=dict(color=AZUL, width=2.5), row=k, col=1,
                            hovertemplate=f"{rot}<br>segmento %{{x}}: %{{y:{fmt}}}<extra></extra>")
        fig.update_xaxes(dtick=1)
        fig.update_xaxes(title="segmento do livro (início → fim)", row=3, col=1)
        for a in fig.layout.annotations:
            a.update(x=0, xanchor="left", font=dict(size=12, color=SUAVE))
        figs.append(_layout(fig, "Evolução ao longo do livro", altura=540))

    lugares = ents[ents.tipo == "lugar"].head(15).iloc[::-1] if not ents.empty else ents
    if len(lugares):
        fig = go.Figure(go.Bar(x=lugares.ocorrencias, y=lugares.entidade, orientation="h", marker_color=VERDE,
                               hovertemplate="<b>%{y}</b>: %{x}<extra></extra>"))
        figs.append(_layout(fig, "Lugares mais mencionados<br><sup>Estimativa do reconhecimento de entidades (NER)</sup>",
                            altura=500))
    return figs


# ---------------------------------------------------------------------------
# Página HTML
# ---------------------------------------------------------------------------

CSS = """
:root{--tinta:#1d2733;--suave:#6b7785;--linha:#e3e8ee;--fundo:#f6f8fa;--azul:#1F5C6B}
*{box-sizing:border-box}body{margin:0;font-family:Inter,-apple-system,Segoe UI,Helvetica,Arial,sans-serif;
color:var(--tinta);background:var(--fundo)}main{max-width:1180px;margin:0 auto;padding:28px 16px 48px}
h1{font-size:28px;margin:0 0 4px}.sub{color:var(--suave);margin:0 0 20px}.cards{display:grid;
grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:0 0 20px}.card{background:#fff;
border:1px solid var(--linha);border-radius:10px;padding:14px 16px}.card b{display:block;font-size:22px;
font-variant-numeric:tabular-nums}.card span{color:var(--suave);font-size:12px}.bloco{background:#fff;
border:1px solid var(--linha);border-radius:10px;padding:8px;margin:0 0 16px}.grelha{display:grid;
grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:16px}.grelha .bloco{margin:0}table{border-collapse:
collapse;width:100%;font-size:13px}td,th{padding:6px 10px;border-bottom:1px solid var(--linha);text-align:left}
th{color:var(--suave);font-weight:600}td.n{text-align:right;font-variant-numeric:tabular-nums}.meta{background:#fff;
border:1px solid var(--linha);border-radius:10px;padding:8px 8px;margin:0 0 16px}footer{color:var(--suave);
font-size:12px;margin-top:24px}a{color:var(--azul)}@media(max-width:560px){.grelha{grid-template-columns:1fr}}
"""


def _num(v, casas=1):
    if v is None or (isinstance(v, float) and v != v):
        return "—"
    if isinstance(v, (int, np.integer)) or float(v).is_integer() and abs(v) >= 100:
        return f"{int(v):,}".replace(",", " ")
    return f"{v:.{casas}f}".replace(".", ",")


def pagina(titulo: str, subtitulo: str, cartoes: list[tuple[str, str]], figs: list[go.Figure],
           tabela_html: str, rodape: str, offline: bool, destino: Path):
    partes = []
    for i, f in enumerate(figs):
        largo = i == 0 or f.layout.height and f.layout.height >= 600
        div = pio.to_html(f, full_html=False, include_plotlyjs=("inline" if offline else "cdn") if i == 0 else False,
                          config={"displaylogo": False, "responsive": True,
                                  "toImageButtonOptions": {"format": "png", "scale": 2}})
        partes.append((largo, f'<div class="bloco">{div}</div>'))
    corpo, grelha = [], []
    for largo, div in partes:
        if largo:
            if grelha:
                corpo.append('<div class="grelha">' + "".join(grelha) + "</div>")
                grelha = []
            corpo.append(div)
        else:
            grelha.append(div)
    if grelha:
        corpo.append('<div class="grelha">' + "".join(grelha) + "</div>")
    cards = "".join(f'<div class="card"><b>{html.escape(v)}</b><span>{html.escape(r)}</span></div>' for r, v in cartoes)
    destino.write_text(f"""<!doctype html>
<html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)} · livros-pln</title><style>{CSS}</style></head>
<body><main><h1>{html.escape(titulo)}</h1><p class="sub">{html.escape(subtitulo)}</p>
<div class="cards">{cards}</div>{tabela_html}{''.join(corpo)}
<footer>{rodape}</footer></main>
<script>window.addEventListener("load",()=>{{document.querySelectorAll(".js-plotly-plot").forEach(g=>Plotly.Plots.resize(g))}});</script>
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
    meta += [("Aviso", a["mensagem"]) for a in registo.get("qualidade", [])]
    tabela = '<div class="meta"><table>' + "".join(
        f"<tr><th>{html.escape(r)}</th><td>{html.escape(str(x))}</td></tr>" for r, x in meta) + "</table></div>"
    figs = figuras_livro(freq, classes, comprimentos, evol, ents, pers, g)
    p = registo["processamento"]
    rodape = (f"livros-pln {p['versao']} · código {p['versao_codigo']}" + (f" · commit {p['commit']}" if p.get("commit") else "")
              + f" · processado em {p['data']} · definições e limitações dos indicadores no relatório README.md")
    sub = " · ".join(x for x in [registo.get("autor"), str(registo.get("ano") or "")] if x)
    pagina(registo["titulo"], sub, cartoes, figs, tabela, rodape, offline, destino)


def painel_corpus(t: pd.DataFrame, destino: Path, offline: bool = False):
    if t.empty:
        return
    t = t.copy()
    t["rotulo"] = t.titulo.fillna(t.id).str.slice(0, 45)
    figs = []
    fig = go.Figure()
    for lg, sub in t.groupby("lingua"):
        fig.add_scatter(x=sub.frase_mediana, y=sub.mtld, mode="markers+text", text=sub.rotulo, textposition="top center",
                        name=tema.LINGUAS.get(lg, (0, 0, lg))[2],
                        marker=dict(size=13 + 40 * np.sqrt(sub.palavras / t.palavras.max()), symbol=SIMBOLOS_LINGUA.get(lg),
                                    color=CORES_LINGUA.get(lg, SUAVE), opacity=0.85, line=dict(color="#fff", width=1.5)),
                        customdata=sub[["palavras", "profundidade_media"]],
                        hovertemplate="<b>%{text}</b><br>Frase mediana: %{x:.0f} palavras<br>MTLD: %{y:.1f}"
                                      "<br>Palavras: %{customdata[0]:,}<br>Profundidade: %{customdata[1]:.2f}<extra></extra>")
    fx = max((t.frase_mediana.max() - t.frase_mediana.min()) * 0.25, 1)
    fy = max((t.mtld.max() - t.mtld.min()) * 0.2, 5) if t.mtld.notna().any() else 5
    fig.update_xaxes(title="extensão mediana das frases (palavras)", range=[t.frase_mediana.min() - fx, t.frase_mediana.max() + fx])
    fig.update_yaxes(title="diversidade lexical (MTLD)", range=[(t.mtld.min() or 0) - fy, (t.mtld.max() or 0) + fy])
    figs.append(_layout(fig, "Extensão das frases e diversidade lexical<br><sup>Tamanho = número de palavras; os níveis "
                             "de MTLD não são comparáveis entre línguas</sup>", altura=600,
                        legend=dict(orientation="h", y=-0.16, x=0, yanchor="top")))
    linhas = "".join(
        f'<tr><td><a href="livros/{r.id}/painel.html">{html.escape(str(r.titulo))}</a></td><td>{html.escape(str(r.autor or "—"))}</td>'
        f'<td>{r.lingua}</td><td class="n">{_num(r.palavras, 0)}</td><td class="n">{_num(r.mtld)}</td>'
        f'<td class="n">{_num(r.frase_mediana, 0)}</td><td class="n">{_num(r.profundidade_media, 2)}</td>'
        f'<td class="n">{_num(r.legibilidade, 0)}</td></tr>'
        for r in t.sort_values(["lingua", "titulo"]).itertuples())
    tabela = ('<div class="meta"><table><tr><th>Livro</th><th>Autor</th><th>Língua</th><th>Palavras</th><th>MTLD</th>'
              f'<th>Frase mediana</th><th>Profundidade</th><th>Legibilidade</th></tr>{linhas}</table></div>')
    cartoes = [("livros", str(len(t))), ("palavras", _num(int(t.palavras.sum()), 0)),
               ("línguas", ", ".join(sorted(t.lingua.unique())))]
    pagina("Livros analisados", "Comparação entre livros · livros-pln", cartoes, figs, tabela,
           "Clique num título para abrir o painel do livro. A legibilidade usa fórmulas diferentes em cada língua.",
           offline, destino)
