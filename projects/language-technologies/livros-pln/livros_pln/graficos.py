"""Gráficos estáticos (matplotlib) com a identidade visual de `tema.py`: por livro e de comparação.

Cada gráfico é exportado em PNG (200 ppp) e SVG.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from . import tema
from .catalogo import CLASSES, NOMES_CLASSES
from .tema import num

# ---------------------------------------------------------------------------
# Por livro
# ---------------------------------------------------------------------------


def classes_gramaticais(classes: pd.DataFrame, titulo: str, modelo: str, pasta: Path) -> str:
    c = classes.sort_values("por_1000_palavras")
    fig, ax = tema.figura(largura=8.5, altura=5.2)
    barras = ax.barh(c.nome, c.por_1000_palavras, color=tema.PETROLEO, height=0.62)
    tema.rotular_barras(ax, barras, c.por_1000_palavras.tolist(), 0)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(tema.formatador())
    ax.set_xlabel("ocorrências por 1000 palavras")
    tema.cabecalho(fig, "Classes gramaticais", f"{titulo} · ocorrências por 1000 palavras",
                   f"Etiquetas UPOS atribuídas pelo modelo {modelo}; a exatidão varia entre modelos e é menor em "
                   "grafias antigas.")
    return tema.guardar(fig, pasta, "classes-gramaticais")


def frequencias(freq: pd.DataFrame, titulo: str, pasta: Path, n: int = 25) -> str:
    top = freq.head(n).iloc[::-1]
    rotulos = [f"{l}  ({tema.CLASSES_ABREV.get(p, p)})" for l, p in zip(top.lema, top.pos)]
    fig, ax = tema.figura(largura=8.5, altura=7.2)
    barras = ax.barh(rotulos, top.por_1000_palavras, color=[tema.CLASSES_CORES.get(p, tema.CINZA) for p in top.pos],
                     height=0.68)
    tema.rotular_barras(ax, barras, top.por_1000_palavras.tolist(), 2)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(tema.formatador(1))
    ax.set_xlabel("ocorrências por 1000 palavras")
    from matplotlib.patches import Patch

    presentes = [p for p in tema.CLASSES_CORES if p in set(top.pos)]
    ax.legend(handles=[Patch(color=tema.CLASSES_CORES[p], label=f"{NOMES_CLASSES[p]} ({tema.CLASSES_ABREV[p]})")
                       for p in presentes], loc="lower right")
    tema.cabecalho(fig, "Palavras de conteúdo mais frequentes", f"{titulo} · lemas de substantivos, verbos, adjetivos e "
                   "advérbios, sem palavras gramaticais", "Lematização do spaCy; a classe vem entre parênteses.")
    return tema.guardar(fig, pasta, "frequencias")


def frases(comprimentos: pd.Series, titulo: str, limiar_longa: int, pasta: Path) -> str:
    c = comprimentos[comprimentos > 0]
    p99 = int(np.ceil(c.quantile(0.99)))
    q1, med, q3, media = c.quantile(0.25), c.median(), c.quantile(0.75), c.mean()
    fig, (ax, bx) = tema.figura(2, 1, largura=9, altura=5.6, sharex=True, gridspec_kw={"height_ratios": [4, 1]})
    ax.hist(c.clip(upper=p99), bins=np.arange(0.5, p99 + 1.5, 1), color=tema.PETROLEO_CLARO, edgecolor=tema.FUNDO,
            linewidth=0.4)
    for x, rot, estilo, cor in [(med, f"mediana {num(med, 0)}", "-", tema.PETROLEO),
                                (media, f"média {num(media, 1)}", "--", tema.DESTAQUE)]:
        ax.axvline(x, color=cor, lw=1.6, ls=estilo, label=rot)
    ax.axvspan(limiar_longa, p99 + 1, color=tema.GRELHA, alpha=0.45, lw=0,
               label=f"frases longas (> {limiar_longa}): {num(100 * (c > limiar_longa).mean(), 1)} %")
    ax.legend(loc="upper right")
    ax.set_ylabel("frases")
    ax.yaxis.set_major_formatter(tema.formatador())
    bx.boxplot(c.clip(upper=p99), orientation="horizontal", widths=0.55, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor=tema.PETROLEO_CLARO, color=tema.PETROLEO), medianprops=dict(color=tema.PETROLEO, lw=2),
               whiskerprops=dict(color=tema.SUAVE), capprops=dict(color=tema.SUAVE))
    bx.set_yticks([])
    bx.grid(axis="y", visible=False)
    bx.set_xlabel("palavras por frase")
    tema.cabecalho(fig, "Extensão das frases", f"{titulo} · distribuição de {num(len(c), 0)} frases; percentis 25–75: "
                   f"{num(q1, 0)}–{num(q3, 0)} palavras",
                   f"Eixo cortado no percentil 99 ({p99} palavras); as frases mais longas contam na última barra. "
                   "Extensão ≠ complexidade sintática.")
    return tema.guardar(fig, pasta, "extensao-frases")


def evolucao(evol: pd.DataFrame, titulo: str, pasta: Path) -> str | None:
    if evol.empty or len(evol) < 3:
        return None
    paineis = [("mtld", "Diversidade lexical (MTLD)", 0), ("frase_media", "Extensão média das frases", 1),
               ("densidade_lexical_pct", "Densidade lexical (%)", 1), ("dialogo_pct", "Parágrafos de diálogo (%)", 0),
               ("substantivos_por_1000", "Substantivos por 1000 palavras", 0),
               ("pessoas_por_1000", "Menções de pessoas por 1000 palavras", 1)]
    fig, axes = tema.figura(2, 3, largura=11.5, altura=6.2, sharex=True)
    for ax, (col, rot, casas) in zip(axes.flat, paineis):
        y = evol[col]
        ax.plot(evol.segmento, y, color=tema.PETROLEO, lw=2, marker="o", ms=4.5)
        if y.notna().any():
            ax.axhline(y.median(), color=tema.CINZA, lw=1, ls=":")
        ax.set_title(rot, fontsize=10)
        ax.yaxis.set_major_formatter(tema.formatador(casas))
        ax.set_xticks(evol.segmento)
    for ax in axes[1]:
        ax.set_xlabel("segmento do livro (início → fim)")
    tema.cabecalho(fig, "Evolução ao longo do livro", f"{titulo} · {len(evol)} segmentos com o mesmo número de palavras; "
                   "linha pontilhada = mediana dos segmentos",
                   "Valores por segmento são mais instáveis do que os do livro inteiro; o MTLD exige pelo menos 100 "
                   "palavras por segmento.")
    return tema.guardar(fig, pasta, "evolucao")


def entidades(ents: pd.DataFrame, titulo: str, pasta: Path) -> str | None:
    tipos = [t for t in ("pessoa", "lugar") if t in set(ents.tipo)]
    if not tipos:
        return None
    fig, axes = tema.figura(1, len(tipos), largura=6 * len(tipos), altura=5.4, squeeze=False)
    for ax, tipo in zip(axes[0], tipos):
        sub = ents[ents.tipo == tipo].head(15).iloc[::-1]
        barras = ax.barh(sub.entidade, sub.ocorrencias, color=tema.PETROLEO if tipo == "pessoa" else tema.VERDE_CINZA,
                         height=0.66)
        tema.rotular_barras(ax, barras, sub.ocorrencias.tolist(), 0)
        ax.grid(axis="y", visible=False)
        ax.set_title({"pessoa": "Pessoas", "lugar": "Lugares"}[tipo])
        ax.set_xlabel("menções")
    tema.cabecalho(fig, "Entidades mais mencionadas", f"{titulo} · reconhecimento automático de entidades nomeadas (NER)",
                   "Estimativas sujeitas a erro: variantes do mesmo nome contam em separado e há confusões entre "
                   "pessoas e lugares.")
    return tema.guardar(fig, pasta, "entidades")


def rede(g, titulo: str, metodo: str, pasta: Path) -> str | None:
    """Rede de personagens; cor e forma = comunidade; tamanho = menções; espessura = parágrafos partilhados."""
    import networkx as nx

    if g.number_of_nodes() < 2:
        return None
    h = nx.Graph()
    h.add_weighted_edges_from([(a, b, 1 / math.log1p(d["peso"]) + 0.6) for a, b, d in g.edges(data=True)], weight="w")
    try:
        pos = nx.kamada_kawai_layout(g, dist=dict(nx.all_pairs_dijkstra_path_length(h, weight="w")))
    except Exception:
        pos = nx.spring_layout(g, weight="peso", seed=7)
    maximo = max(d["peso"] for _, _, d in g.edges(data=True))
    m = max(d["mencoes"] for _, d in g.nodes(data=True))
    # para legibilidade, desenham-se só as ligações com pelo menos `minimo` parágrafos partilhados
    # (o mínimo que mantém no máximo ~3 ligações por personagem); a disposição usa todas as ligações
    pesos = sorted((d["peso"] for _, _, d in g.edges(data=True)), reverse=True)
    minimo = pesos[min(len(pesos) - 1, 3 * g.number_of_nodes())] if len(pesos) > 3 * g.number_of_nodes() else 1
    arestas = [(a, b, d) for a, b, d in g.edges(data=True) if d["peso"] >= minimo]
    fig, ax = tema.figura(largura=11, altura=8.6)
    ax.grid(False)
    ax.axis("off")
    nx.draw_networkx_edges(g, pos, ax=ax, edgelist=[(a, b) for a, b, _ in arestas],
                           width=[0.4 + 5 * d["peso"] / maximo for _, _, d in arestas], edge_color=tema.CINZA, alpha=0.55)
    comunidades = sorted({d.get("comunidade", 1) for _, d in g.nodes(data=True)})
    for k, com in enumerate(comunidades):
        nos = [n for n, d in g.nodes(data=True) if d.get("comunidade", 1) == com]
        nx.draw_networkx_nodes(g, pos, nodelist=nos, ax=ax, node_shape=tema.MARCADORES[k % len(tema.MARCADORES)],
                               node_size=[70 + 1300 * (g.nodes[n]["mencoes"] / m) ** 0.7 for n in nos],
                               node_color=tema.SERIES[k % len(tema.SERIES)], edgecolors="white", linewidths=1.2,
                               label=f"comunidade {com}")
    raio = {n: 0.012 + 0.03 * (g.nodes[n]["mencoes"] / m) ** 0.35 for n in g}
    for n, (x, y) in pos.items():
        ax.text(x, y - raio[n] - 0.012, n, ha="center", va="top", fontsize=7.8, color=tema.TINTA,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))
    ax.legend(loc="lower left", markerscale=0.45, scatterpoints=1)
    filtro = f"ligações com ≥ {minimo} parágrafos partilhados" if minimo > 1 else "todas as ligações"
    tema.cabecalho(fig, "Rede de personagens", f"{titulo} · ligação = mesmo parágrafo ({filtro}); tamanho = menções; "
                   "cor e forma = comunidade (Louvain)",
                   f"Identificação: {metodo}. Co-ocorrência textual não equivale a relação narrativa; sem resolução de "
                   "correferência (pronomes não contam).")
    return tema.guardar(fig, pasta, "rede")


def sentimento(evol: pd.DataFrame, extremos: pd.DataFrame, titulo: str, metodo: str | None, limiar: float,
               pasta: Path) -> str | None:
    """Arco de sentimento: média por segmento (linha) e proporção de frases positivas e negativas (barras)."""
    if evol.empty or len(evol) < 3 or "sentimento" not in evol or evol.sentimento.isna().all():
        return None
    fig, (ax1, ax2) = tema.figura(2, 1, largura=10, altura=6.6, sharex=True, height_ratios=[1.1, 1])
    x = evol.segmento
    ax1.axhspan(-limiar, limiar, color=tema.GRELHA, alpha=0.7, lw=0)
    ax1.axhline(0, color=tema.CINZA, lw=1)
    ax1.plot(x, evol.sentimento, color=tema.PETROLEO, lw=2.2, marker="o", ms=5)
    ax1.set_title("Sentimento médio por segmento (compound, −1 a +1)", fontsize=10)
    ax1.yaxis.set_major_formatter(tema.formatador(2))
    ax1.text(x.iloc[-1] + 0.15, 0, "zona neutra", va="center", ha="left", fontsize=8, color=tema.SUAVE)
    s = evol.sentimento.dropna()
    ax1.set_ylim(min(-0.12, s.min() * 1.25), max(0.12, s.max() * 1.25))   # a zona neutra fica sempre visível
    largura = 0.38
    ax2.bar(x - largura / 2, evol.frases_positivas_pct, largura, color=tema.PETROLEO, label="frases positivas")
    ax2.bar(x + largura / 2, evol.frases_negativas_pct, largura, color=tema.DESTAQUE, label="frases negativas",
            hatch="//", edgecolor="white", lw=0)
    ax2.set_title("Frases positivas e negativas por segmento (%)", fontsize=10)
    ax2.yaxis.set_major_formatter(tema.formatador(0))
    ax2.legend(loc="upper left", ncol=2)
    ax2.set_xticks(x)
    ax2.set_xlabel("segmento do livro (início → fim)")
    tema.cabecalho(fig, "Arco de sentimento", f"{titulo} · {metodo or 'método de léxico'}; zona cinzenta = neutro "
                   f"(|compound| < {tema.num(limiar, 2)})",
                   "Mede a polaridade do vocabulário, não o tom narrativo nem a ironia. Léxicos criados para redes "
                   "sociais; não validado em prosa literária.")
    return tema.guardar(fig, pasta, "sentimento")


def reta_zipf(zipf: pd.DataFrame, frequencia_minima: int = 5):
    """Reta ajustada (posições, frequências previstas, expoente), com as mesmas formas do indicador."""
    from .indicadores import _regressao_log

    sub = zipf[zipf.frequencia >= frequencia_minima]
    if len(sub) < 10:
        return None
    declive, origem, _ = _regressao_log(sub.posicao, sub.frequencia)
    r = np.array([1, sub.posicao.max()], float)
    return r, 10 ** origem * r ** declive, -declive


def zipf_heaps(zipf: pd.DataFrame, heaps: pd.DataFrame, ind: dict, titulo: str, pasta: Path,
               frequencia_minima: int = 5) -> str | None:
    """Lei de Zipf (frequência × posição) e lei de Heaps (vocabulário × extensão), em escala log-log."""
    if zipf.empty or heaps.empty:
        return None
    fig, (ax1, ax2) = tema.figura(1, 2, largura=11, altura=5)
    ax1.loglog(zipf.posicao, zipf.frequencia, color=tema.PETROLEO, lw=0, marker="o", ms=2.6, alpha=0.7)
    ajuste = reta_zipf(zipf, frequencia_minima)
    if ajuste is not None:
        r, f, s = ajuste
        ax1.loglog(r, f, color=tema.DESTAQUE, lw=1.6, ls="--", label=f"ajuste: declive {tema.num(-s, 2)}")
        ax1.legend(loc="lower left")
    ax1.set_title("Lei de Zipf", fontsize=10)
    ax1.set_xlabel("posição da forma (1 = mais frequente)")
    ax1.set_ylabel("ocorrências")
    ax2.loglog(heaps.palavras, heaps.vocabulario, color=tema.PETROLEO, lw=2)
    b, k = ind.get("heaps_beta"), ind.get("heaps_k")
    if b == b and b is not None and k:
        n = heaps.palavras.to_numpy(float)
        ax2.loglog(n, k * n ** b, color=tema.DESTAQUE, lw=1.6, ls="--", label=f"β = {tema.num(b, 3)}")
        ax2.legend(loc="lower right")
    ax2.set_title("Lei de Heaps", fontsize=10)
    ax2.set_xlabel("palavras lidas (N)")
    ax2.set_ylabel("formas distintas (V)")
    for ax in (ax1, ax2):
        ax.grid(True, which="major")
    tema.cabecalho(fig, "Leis do vocabulário", f"{titulo} · escalas logarítmicas; tracejado = lei de potência ajustada",
                   "Zipf (1949): f ≈ C·r^−s, ajustada só com formas frequentes; Heaps (1978): V ≈ K·N^β.")
    return tema.guardar(fig, pasta, "zipf-heaps")


def por_livro(titulo, modelo, classes, freq, comprimentos, evol, ents, g, metodo, limiar_longa, pasta: Path,
              extra: dict | None = None, p=None, ind: dict | None = None) -> list[str]:
    figs = [rede(g, titulo, metodo, pasta), classes_gramaticais(classes, titulo, modelo, pasta),
            frequencias(freq, titulo, pasta), frases(comprimentos, titulo, limiar_longa, pasta),
            evolucao(evol, titulo, pasta), entidades(ents, titulo, pasta)]
    if extra:
        figs.append(sentimento(evol, extra["extremos"], titulo, extra["sentimento"]["metodo"],
                               p.sentimento_limiar if p else 0.05, pasta))
        figs.append(zipf_heaps(extra["zipf"], extra["heaps"], ind or {}, titulo, pasta,
                               p.zipf_frequencia_minima if p else 5))
    return [f for f in figs if f]


# ---------------------------------------------------------------------------
# Comparação entre livros
# ---------------------------------------------------------------------------

def _rotulo(t: pd.DataFrame) -> pd.Series:
    titulo = t.titulo.fillna(t.id).str.slice(0, 34)
    return titulo + t.ano.fillna("").astype(str).str.slice(0, 4).map(lambda a: f" ({a})" if a else "")


def _ordem(t: pd.DataFrame) -> pd.DataFrame:
    t = t.copy()
    t["rotulo"] = _rotulo(t)
    return t.sort_values(["lingua", "rotulo"], ascending=[False, False]).reset_index(drop=True)


def _legenda_linguas(fig, linguas):
    from matplotlib.lines import Line2D

    fig.legend(handles=[Line2D([], [], color=tema.LINGUAS[l][0], marker=tema.LINGUAS[l][1], ls="", ms=8,
                               label=tema.LINGUAS[l][2]) for l in linguas if l in tema.LINGUAS],
               loc="outside lower right", ncol=3)


def perfil_comparativo(t: pd.DataFrame, pasta: Path) -> str:
    """Dot plot por indicador; livros agrupados por língua (cor e forma)."""
    t = _ordem(t)
    paineis = [("mtld", "Diversidade lexical (MTLD)", 0), ("densidade_lexical_pct", "Densidade lexical (%)", 0),
               ("frase_mediana", "Extensão mediana das frases", 0), ("profundidade_media", "Profundidade sintática", 1),
               ("distancia_dependencia", "Distância de dependência média", 2), ("dialogo_pct", "Diálogo (% parágrafos)", 0)]
    altura = max(4.2, 0.42 * len(t) + 3)
    fig, axes = tema.figura(2, 3, largura=12, altura=2 * altura * 0.62, sharey=True)
    y = np.arange(len(t))
    for ax, (col, rot, casas) in zip(axes.flat, paineis):
        for lg, sub in t.groupby("lingua"):
            cor, marca, _ = tema.LINGUAS.get(lg, (tema.CINZA, "o", lg))
            ax.scatter(sub[col], sub.index, color=cor, marker=marca, s=55, zorder=3)
        ax.hlines(y, 0, t[col].fillna(0), color=tema.GRELHA, lw=1, zorder=1)
        ax.set_yticks(y, t.rotulo)
        ax.set_title(rot, fontsize=10)
        ax.xaxis.set_major_formatter(tema.formatador(casas))
        validos = t[col].dropna()
        if len(validos) and validos.max() > 0:
            ax.set_xlim(0, validos.max() * 1.15)
        ax.grid(axis="y", visible=False)
    _legenda_linguas(fig, sorted(t.lingua.unique()))
    tema.cabecalho(fig, "Perfil linguístico dos livros", "Livros agrupados por língua · comparar sobretudo dentro da mesma "
                   "língua", "MTLD, densidade lexical, profundidade e distância de dependência dependem da língua e do "
                   "modelo spaCy: diferenças entre línguas não medem diferenças de estilo.")
    return tema.guardar(fig, pasta, "perfil-comparativo")


def classes_comparadas(classes: dict[str, pd.DataFrame], t: pd.DataFrame, pasta: Path) -> str:
    t = _ordem(t)
    principais = ["NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "PROPN"]
    fig, ax = tema.figura(largura=10, altura=5.8)
    y = np.arange(len(principais))
    desvio = np.linspace(-0.28, 0.28, len(t)) if len(t) > 1 else [0]
    for k, (r, d) in enumerate(zip(t.itertuples(), desvio)):
        c = classes[r.id].set_index("classe").reindex(principais)
        ax.scatter(c.por_1000_palavras, y + d, color=tema.SERIES[k % len(tema.SERIES)],
                   marker=tema.MARCADORES[k % len(tema.MARCADORES)], s=48, label=r.rotulo, zorder=3)
    ax.set_yticks(y, [NOMES_CLASSES[c] for c in principais])
    ax.invert_yaxis()
    ax.set_xlabel("ocorrências por 1000 palavras")
    ax.xaxis.set_major_formatter(tema.formatador())
    ax.legend(loc="lower right")
    tema.cabecalho(fig, "Classes gramaticais por livro", "Ocorrências por 1000 palavras (UPOS)",
                   "A distribuição depende da gramática de cada língua (por exemplo, sujeito nulo em português) e da "
                   "exatidão do modelo.")
    return tema.guardar(fig, pasta, "classes-comparadas")


def frases_comparadas(frases: dict[str, pd.Series], t: pd.DataFrame, pasta: Path) -> str:
    t = _ordem(t)
    dados = [frases[i][frases[i] > 0].values for i in t.id]
    fig, ax = tema.figura(largura=10, altura=max(3.5, 0.55 * len(t) + 2.2))
    caixas = ax.boxplot(dados, orientation="horizontal", widths=0.55, showfliers=False, patch_artist=True, showmeans=True,
                        meanprops=dict(marker="D", markerfacecolor=tema.DESTAQUE, markeredgecolor="white", ms=6),
                        medianprops=dict(color=tema.TINTA, lw=1.8), whiskerprops=dict(color=tema.SUAVE),
                        capprops=dict(color=tema.SUAVE))
    for caixa, lg in zip(caixas["boxes"], t.lingua):
        caixa.set(facecolor=tema.LINGUAS.get(lg, (tema.CINZA,))[0], alpha=0.35, edgecolor=tema.SUAVE)
    ax.set_yticks(range(1, len(t) + 1), t.rotulo)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("palavras por frase")
    tema.cabecalho(fig, "Extensão das frases por livro", "Caixa = percentis 25–75; traço = mediana; losango = média; "
                   "bigodes até 1,5 × intervalo interquartil",
                   "Valores extremos omitidos. A segmentação de frases depende do modelo de cada língua.")
    return tema.guardar(fig, pasta, "frases-comparadas")


def evolucao_comparada(evolucoes: dict[str, pd.DataFrame], t: pd.DataFrame, pasta: Path) -> str | None:
    t = _ordem(t)
    if not any(len(evolucoes.get(i, [])) >= 3 for i in t.id):
        return None
    fig, axes = tema.figura(1, 2, largura=11.5, altura=4.8)
    for k, r in enumerate(t.itertuples()):
        e = evolucoes.get(r.id)
        if e is None or len(e) < 3:
            continue
        x = (e.segmento - 0.5) / len(e) * 100
        for ax, col in zip(axes, ["mtld", "frase_media"]):
            ax.plot(x, e[col], color=tema.SERIES[k % len(tema.SERIES)], marker=tema.MARCADORES[k % len(tema.MARCADORES)],
                    ms=5, lw=1.8, label=r.rotulo)
    for ax, rot in zip(axes, ["Diversidade lexical (MTLD)", "Extensão média das frases"]):
        ax.set_title(rot, fontsize=10)
        ax.set_xlabel("posição no livro (% do texto)")
        ax.set_xlim(0, 100)
    axes[1].legend(loc="best")
    tema.cabecalho(fig, "Evolução ao longo dos livros", "Posição normalizada (0 % = início, 100 % = fim)",
                   "Comparar a forma das curvas; os níveis de MTLD não são comparáveis entre línguas.")
    return tema.guardar(fig, pasta, "evolucao-comparada")


def correlacoes(t: pd.DataFrame, pasta: Path, minimo: int = 5) -> str | None:
    """Matriz de correlação de Spearman entre indicadores; só com pelo menos `minimo` livros."""
    if len(t) < minimo:
        return None
    cols = {"mtld": "MTLD", "hdd": "HD-D", "densidade_lexical_pct": "Densidade lexical", "frase_media": "Frase média",
            "profundidade_media": "Profundidade", "distancia_dependencia": "Dist. dependência",
            "subordinadas_por_frase": "Subordinadas/frase", "dialogo_pct": "Diálogo", "pronomes_pessoais_por_1000": "Pron. pessoais"}
    m = t[list(cols)].rename(columns=cols).corr(method="spearman")
    from matplotlib.colors import LinearSegmentedColormap

    mapa = LinearSegmentedColormap.from_list("divergente", [tema.DESTAQUE, "#F4F1EC", tema.PETROLEO])
    fig, ax = tema.figura(largura=8.6, altura=7.4)
    im = ax.imshow(m.values, cmap=mapa, vmin=-1, vmax=1)
    ax.set_xticks(range(len(m)), m.columns, rotation=40, ha="right")
    ax.set_yticks(range(len(m)), m.index)
    ax.grid(False)
    for i in range(len(m)):
        for j in range(len(m)):
            v = m.values[i, j]
            if v == v:
                ax.text(j, i, num(v, 2), ha="center", va="center", fontsize=7.5, color=tema.TINTA if abs(v) < 0.6 else "white")
    fig.colorbar(im, ax=ax, shrink=0.75, label="ρ de Spearman")
    tema.cabecalho(fig, "Correlação entre indicadores", f"{len(t)} livros · correlação de postos de Spearman",
                   "Com poucos livros as correlações são muito instáveis; mistura de línguas pode criar correlações "
                   "espúrias.")
    return tema.guardar(fig, pasta, "correlacoes")


def delta(resultado: dict, titulos: dict[str, str], pasta: Path) -> list[str]:
    figs = []
    for lg, r in resultado.items():
        if r["estado"] != "valido":
            continue
        m = r["matriz"]
        rot = [titulos.get(i, i)[:30] for i in m.index]
        from matplotlib.colors import LinearSegmentedColormap

        mapa = LinearSegmentedColormap.from_list("sequencial", ["#F4F1EC", tema.PETROLEO_CLARO, tema.AZUL_ESCURO])
        fig, ax = tema.figura(largura=7.5 + 0.2 * len(m), altura=6 + 0.2 * len(m))
        im = ax.imshow(m.values, cmap=mapa)
        ax.set_xticks(range(len(m)), rot, rotation=40, ha="right")
        ax.set_yticks(range(len(m)), rot)
        ax.grid(False)
        for i in range(len(m)):
            for j in range(len(m)):
                ax.text(j, i, num(m.values[i, j], 2), ha="center", va="center", fontsize=8,
                        color="white" if m.values[i, j] > m.values.max() * 0.6 else tema.TINTA)
        fig.colorbar(im, ax=ax, shrink=0.75, label="Delta de Burrows")
        tema.cabecalho(fig, f"Distância estilística ({tema.LINGUAS.get(lg, (0, 0, lg))[2]})",
                       f"Delta de Burrows com as {len(r['palavras'])} palavras mais frequentes · menor = mais semelhante",
                       "Distância relativa dentro deste corpus; não constitui prova de autoria.")
        figs.append(tema.guardar(fig, pasta, f"delta-{lg}"))
    return figs


def corpus(t, classes, frases_por_livro, evolucoes, resultado_delta, pasta: Path) -> list[str]:
    if t.empty:
        return []
    figs = [perfil_comparativo(t, pasta), classes_comparadas(classes, t, pasta), frases_comparadas(frases_por_livro, t, pasta),
            evolucao_comparada(evolucoes, t, pasta), correlacoes(t, pasta)]
    figs += delta(resultado_delta, dict(zip(t.id, t.titulo)), pasta)
    return [f for f in figs if f]
