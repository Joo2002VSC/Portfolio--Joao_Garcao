"""Gráficos 3D para os painéis HTML (Plotly).

O Plotly não tem barras 3D: cada barra é um prisma desenhado com `Mesh3d`. A perspetiva
distorce a leitura dos valores, por isso cada gráfico 3D do painel tem uma vista 2D
alternativa com os mesmos dados, e os valores exatos aparecem ao passar o rato.
"""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

# triângulos das 6 faces de um prisma com vértices 0–3 (base) e 4–7 (topo)
_I = [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1]
_J = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 2, 6]
_K = [2, 3, 6, 7, 5, 4, 6, 7, 7, 4, 6, 5]
# arestas do prisma, para o contorno
_ARESTAS = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
LUZ = dict(ambient=0.62, diffuse=0.75, specular=0.12, roughness=0.7, fresnel=0.1)


def _prisma(x: float, y: float, h: float, largura: float, profundidade: float):
    x0, x1, y0, y1 = x - largura / 2, x + largura / 2, y - profundidade / 2, y + profundidade / 2
    return ([x0, x1, x1, x0, x0, x1, x1, x0], [y0, y0, y1, y1, y0, y0, y1, y1], [0, 0, 0, 0, h, h, h, h])


def eixo(titulo: str = "", valores=None, rotulos=None, fundo: str = "#EDE4D3", grelha: str = "#D8CBB4",
         cor: str = "#6E5E4E", **extra) -> dict:
    e = dict(title=dict(text=titulo, font=dict(size=12, color=cor)), backgroundcolor=fundo, showbackground=True,
             gridcolor=grelha, zerolinecolor=grelha, tickfont=dict(size=11, color=cor), showspikes=False, **extra)
    if valores is not None:
        e.update(tickvals=list(valores), ticktext=list(rotulos))
    return e


def barras_3d(x: list, y: list, z: list, cores: list[str], *, hover: list[str], nomes: list[str] | None = None,
              titulo_z: str = "", titulo_x: str = "", titulo_y: str = "", ordem_x: list | None = None,
              ordem_y: list | None = None, rotulos: list[str] | None = None, largura: float = 0.62,
              profundidade: float = 0.62, contorno: str = "rgba(30,25,21,0.35)") -> go.Figure:
    """Barras 3D: categorias `x` ao longo da largura, `y` em profundidade, altura `z`.

    `cores` e `nomes` (legenda) são por barra; as barras com a mesma cor formam um único Mesh3d.
    `rotulos` (opcional) escreve um texto por cima de cada barra."""
    ordem_x = ordem_x or list(dict.fromkeys(x))
    ordem_y = ordem_y or list(dict.fromkeys(y))
    px = {v: i for i, v in enumerate(ordem_x)}
    py = {v: i for i, v in enumerate(ordem_y)}
    nomes = nomes or [None] * len(z)
    grupos: dict[tuple, list[int]] = {}
    for k, (c, n) in enumerate(zip(cores, nomes)):
        grupos.setdefault((c, n), []).append(k)
    traces, lx, ly, lz = [], [], [], []
    for (cor, nome), idx in grupos.items():
        vx, vy, vz, vi, vj, vk, texto = [], [], [], [], [], [], []
        for k in idx:
            h = float(z[k]) if z[k] == z[k] else 0.0
            if h <= 0:
                continue
            bx, by, bz = _prisma(px[x[k]], py[y[k]], h, largura, profundidade)
            base = len(vx)
            vx += bx
            vy += by
            vz += bz
            vi += [base + i for i in _I]
            vj += [base + j for j in _J]
            vk += [base + q for q in _K]
            texto += [hover[k]] * 8
            for a, b in _ARESTAS:
                lx += [bx[a], bx[b], None]
                ly += [by[a], by[b], None]
                lz += [bz[a], bz[b], None]
        if not vx:
            continue
        traces.append(go.Mesh3d(x=vx, y=vy, z=vz, i=vi, j=vj, k=vk, color=cor, flatshading=True, lighting=LUZ,
                                lightposition=dict(x=-1000, y=-2000, z=3000), opacity=1, name=nome or "",
                                showlegend=bool(nome), text=texto, hovertemplate="%{text}<extra></extra>"))
    if lx:
        traces.append(go.Scatter3d(x=lx, y=ly, z=lz, mode="lines", line=dict(color=contorno, width=1.4),
                                   hoverinfo="skip", showlegend=False))
    if rotulos:
        traces.append(go.Scatter3d(x=[px[v] for v in x], y=[py[v] for v in y],
                                   z=[(float(v) if v == v else 0) * 1.03 for v in z], mode="text", text=rotulos,
                                   textposition="top center", textfont=dict(size=11, color="#1E1915"),
                                   hoverinfo="skip", showlegend=False))
    fig = go.Figure(traces)
    nx_, ny_ = len(ordem_x), len(ordem_y)
    fig.update_layout(scene=dict(
        xaxis=eixo(titulo_x, range(nx_), ordem_x, range=[-0.7, nx_ - 0.3]),
        yaxis=eixo(titulo_y, range(ny_), ordem_y, range=[-0.7, ny_ - 0.3]),
        zaxis=eixo(titulo_z, rangemode="tozero"),
        aspectmode="manual", aspectratio=dict(x=1.9, y=min(1.3, 0.35 + 0.16 * ny_), z=0.85),
        camera=dict(eye=dict(x=0.5, y=-1.72, z=0.82), center=dict(x=0, y=0, z=-0.1)),
        dragmode="orbit"))
    return fig


def superficie(x: list, y: list, z: np.ndarray, *, cores: list, titulo_x: str, titulo_y: str, titulo_z: str,
               rotulos_y: list[str] | None = None, hover: str) -> go.Figure:
    """Superfície 3D (relevo) de uma matriz z[y][x]."""
    fig = go.Figure(go.Surface(x=x, y=y, z=z, colorscale=cores, showscale=False, lighting=LUZ,
                               contours=dict(z=dict(show=True, usecolormap=True, width=1, project=dict(z=False))),
                               hovertemplate=hover))
    fig.update_layout(scene=dict(
        xaxis=eixo(titulo_x), yaxis=eixo(titulo_y, y if rotulos_y else None, rotulos_y),
        zaxis=eixo(titulo_z, rangemode="tozero"), aspectmode="manual", aspectratio=dict(x=1.8, y=1.1, z=0.7),
        camera=dict(eye=dict(x=1.1, y=-1.45, z=0.85)), dragmode="orbit"))
    return fig


def fitas(x: list, series: list[tuple[str, list, list, str, str]], *, titulo_x: str, titulo_z: str) -> go.Figure:
    """Fitas 3D: uma série por fita, cada uma na sua profundidade.

    `series` = [(nome, valores na escala comum, valores originais, cor, formato do valor original)]."""
    traces = []
    for k, (nome, zs, originais, cor, fmt) in enumerate(series):
        zs = np.asarray(zs, float)
        traces.append(go.Surface(x=[x, x], y=[[k - 0.28] * len(x), [k + 0.28] * len(x)], z=[zs, zs],
                                 surfacecolor=[[0] * len(x), [0] * len(x)], colorscale=[[0, cor], [1, cor]],
                                 showscale=False, opacity=0.93, lighting=LUZ, hoverinfo="skip"))
        traces.append(go.Scatter3d(
            x=x, y=[k] * len(x), z=zs, mode="lines+markers", name=nome, line=dict(color="#1E1915", width=2),
            marker=dict(size=3.5, color=cor, line=dict(color="#F4EEE3", width=1)),
            text=[("—" if v != v else format(v, fmt).replace(".", ",")) for v in originais],
            hovertemplate=f"<b>{nome}</b><br>segmento %{{x}}: %{{text}}<extra></extra>", showlegend=False))
    fig = go.Figure(traces)
    fig.update_layout(scene=dict(
        xaxis=eixo(titulo_x, dtick=1), yaxis=eixo("", range(len(series)), [s[0] for s in series]),
        zaxis=eixo(titulo_z), aspectmode="manual", aspectratio=dict(x=1.9, y=0.4 + 0.22 * len(series), z=0.75),
        camera=dict(eye=dict(x=1.0, y=-1.6, z=0.8)), dragmode="orbit"))
    return fig


def dispersao(x, y, z, *, texto: list[str], tamanho, cores, simbolos=None, titulos: tuple[str, str, str],
              hover: str, customdata=None, nomes=None) -> go.Figure:
    """Dispersão 3D com rótulos e uma linha vertical até ao «chão» por ponto (ajuda a ler a posição)."""
    traces = []
    zmin = float(np.nanmin(z)) if len(z) else 0.0
    for xi, yi, zi in zip(x, y, z):
        traces.append(go.Scatter3d(x=[xi, xi], y=[yi, yi], z=[zmin, zi], mode="lines", hoverinfo="skip",
                                   line=dict(color="rgba(110,94,78,0.45)", width=2), showlegend=False))
    traces.append(go.Scatter3d(x=x, y=y, z=z, mode="markers+text", text=texto, textposition="top center",
                               textfont=dict(size=11, color="#1E1915"),
                               marker=dict(size=tamanho, color=cores, symbol=simbolos or "circle", opacity=0.92,
                                           line=dict(color="#F4EEE3", width=1)),
                               customdata=customdata, hovertemplate=hover, showlegend=False))
    fig = go.Figure(traces)
    fig.update_layout(scene=dict(xaxis=eixo(titulos[0]), yaxis=eixo(titulos[1]), zaxis=eixo(titulos[2]),
                                 aspectmode="manual", aspectratio=dict(x=1.5, y=1.2, z=0.85),
                                 camera=dict(eye=dict(x=1.45, y=-1.55, z=0.85)), dragmode="orbit"))
    return fig
