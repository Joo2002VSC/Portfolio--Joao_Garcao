"""Rede de personagens: quem aparece com quem.

Duas formas de identificar as personagens:
  * automática: entidades «pessoa» do NER, com normalização de títulos («D.», «Mr.»,
    «Madame»…) e fusão de nomes curtos com o nome completo correspondente
    («Carlos» → «Carlos da Maia», se não houver outro «Carlos …»);
  * dicionário: se existir livros/personagens/<id-do-livro>.json, as personagens e as
    suas formas de referência vêm desse ficheiro (mais fiável; o NER erra nomes raros).
Duas personagens ligam-se quando aparecem no mesmo parágrafo.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import pandas as pd

from .indicadores import ENTIDADES

TITULOS = {
    "pt": ["d.", "dom", "dona", "sr.", "sr", "snr.", "snr", "sra.", "sr.ª", "srª", "senhor", "senhora", "dr.", "dr",
           "doutor", "conde", "condessa", "marquês", "marquesa", "visconde", "viscondessa", "padre", "o", "a", "tio", "tia"],
    "fr": ["m.", "mme", "mme.", "mlle", "mlle.", "monsieur", "madame", "mademoiselle", "le", "la", "docteur", "abbé", "comte",
           "comtesse"],
    "en": ["mr.", "mr", "mrs.", "mrs", "miss", "ms.", "dr.", "dr", "sir", "lady", "lord", "the", "uncle", "aunt", "captain"],
}


def _sem_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))


PARTICULAS = {"da", "de", "do", "das", "dos", "d'", "e", "du", "des", "la", "le", "van", "von", "of", "the", "y"}


def normalizar(nome: str, lingua: str) -> str:
    nome = re.sub(r"[’']s$", "", nome.strip(" \t\n.,;:!?«»\"“”—-"))
    partes = nome.split()
    titulos = set(TITULOS.get(lingua, []))
    while len(partes) > 1 and partes[0].lower() in titulos:
        partes.pop(0)
    # corta no primeiro elemento em minúsculas que não seja partícula («Melanie de sa» → «Melanie»)
    for i, p in enumerate(partes[1:], start=1):
        if p[:1].islower() and p.lower() not in PARTICULAS:
            partes = partes[:i]
            break
    while len(partes) > 1 and partes[-1].lower() in PARTICULAS:
        partes.pop()
    return " ".join(partes)


# ---------------------------------------------------------------------------
# Identificação
# ---------------------------------------------------------------------------

def automatico(entidades: pd.DataFrame, lingua: str, min_mencoes: int = 5, maximo: int = 40,
               ignorar: set[str] = frozenset()) -> tuple[dict[int, set[str]], dict[str, int]]:
    """Devolve ({parágrafo: {personagens}}, {personagem: menções}) a partir do NER."""
    todas = entidades.assign(nome=entidades.entidade.map(lambda n: normalizar(n, lingua)))
    # nomes que o NER classifica mais vezes como lugar ou organização do que como pessoa ficam de fora
    tipo = todas.assign(pessoa=todas.rotulo.isin(ENTIDADES["pessoa"]),
                        outro=todas.rotulo.isin(ENTIDADES["lugar"] | ENTIDADES["organizacao"]))
    votos = tipo.groupby("nome")[["pessoa", "outro"]].sum()
    pessoas_validas = set(votos.index[votos.pessoa > votos.outro])
    pessoas = todas[todas.rotulo.isin(ENTIDADES["pessoa"]) & todas.nome.isin(pessoas_validas)]
    pessoas = pessoas[(pessoas.nome.str.len() > 1) & pessoas.nome.str[0].str.isupper()
                      & ~pessoas.nome.str.contains(r"^\w{1,2}['’]", regex=True)]  # «N'essa», «D'abord»
    pessoas = pessoas[~pessoas.nome.str.lower().isin(ignorar)]
    contagem = Counter(pessoas.nome)

    # fusão de um nome curto com a forma longa dominante que começa (ou, em alternativa, acaba) por ele:
    # «Carlos» → «Carlos da Maia» se esta tiver pelo menos 60 % das menções das formas «Carlos …»
    longos = [n for n in contagem if " " in n]
    mapa = {}
    for nome in contagem:
        if " " in nome:
            continue
        for grupo in ([l for l in longos if l.split()[0] == nome], [l for l in longos if l.split()[-1] == nome]):
            if grupo:
                dominante = max(grupo, key=contagem.get)
                if contagem[dominante] >= 0.6 * sum(contagem[g] for g in grupo):
                    mapa[nome] = dominante
                break
    for longo in longos:  # formas longas secundárias juntam-se à dominante do mesmo nome próprio
        curto = longo.split()[0]
        if curto in mapa and mapa[curto] != longo and longo.split()[0] == mapa[curto].split()[0]:
            mapa[longo] = mapa[curto]
    pessoas["personagem"] = pessoas.nome.map(lambda n: mapa.get(n, n))
    mencoes = Counter(pessoas.personagem)
    escolhidas = {n for n, c in mencoes.most_common(maximo) if c >= min_mencoes}
    por_paragrafo = defaultdict(set)
    for p, n in zip(pessoas.paragrafo, pessoas.personagem):
        if n in escolhidas:
            por_paragrafo[p].add(n)
    return dict(por_paragrafo), {n: mencoes[n] for n in escolhidas}


def por_dicionario(paragrafos: list[str], ficheiro: Path) -> tuple[dict[int, set[str]], dict[str, int]]:
    """Identificação com um dicionário de personagens (formato de livros/personagens/README.md)."""
    dados = json.loads(ficheiro.read_text(encoding="utf-8"))
    formas: dict[str, list[tuple[str | None, tuple[int, int] | None]]] = defaultdict(list)
    for p in dados["personagens"]:
        for a in p["aliases"]:
            forma, intervalo = (a["forma"], tuple(a["paragrafos"]) if "paragrafos" in a else None) \
                if isinstance(a, dict) else (a, None)
            formas[_sem_acentos(forma)].append((p["nome"], intervalo))
    for f in dados.get("ignorar", []):
        formas[_sem_acentos(f)].append((None, None))
    partes = []
    for f in sorted(formas, key=len, reverse=True):
        esc = re.escape(f)
        partes.append(esc if f[:1].isupper() else f"(?i:{esc})")
    padrao = re.compile(r"(?<![\w])(?:" + "|".join(partes) + r")(?![\w])")
    por_paragrafo, mencoes = defaultdict(set), Counter()
    for i, texto in enumerate(paragrafos):
        for m in padrao.finditer(_sem_acentos(texto)):
            opcoes = formas.get(m.group(0)) or next((v for k, v in formas.items() if k.lower() == m.group(0).lower()), [])
            for nome, intervalo in opcoes:
                if intervalo is None or intervalo[0] <= i <= intervalo[1]:
                    if nome:
                        por_paragrafo[i].add(nome)
                        mencoes[nome] += 1
                    break
    return dict(por_paragrafo), dict(mencoes)


# ---------------------------------------------------------------------------
# Rede
# ---------------------------------------------------------------------------

def rede(por_paragrafo: dict[int, set[str]], mencoes: dict[str, int], min_mencoes: int = 5) -> nx.Graph:
    g = nx.Graph()
    for n, c in mencoes.items():
        if c >= min_mencoes:
            g.add_node(n, mencoes=c)
    for grupo in por_paragrafo.values():
        grupo = sorted(grupo & set(g))
        for i, a in enumerate(grupo):
            for b in grupo[i + 1:]:
                g.add_edge(a, b, peso=g[a][b]["peso"] + 1 if g.has_edge(a, b) else 1)
    g.remove_nodes_from([n for n in list(g) if g.degree(n) == 0])
    for _, _, d in g.edges(data=True):
        d["distancia"] = 1 / d["peso"]
    return g


def metricas(g: nx.Graph) -> pd.DataFrame:
    if g.number_of_nodes() == 0:
        return pd.DataFrame(columns=["personagem", "mencoes", "grau", "grau_ponderado", "intermediacao",
                                     "pagerank", "comunidade"])
    comunidades = nx.community.louvain_communities(g, weight="peso", seed=42)
    comunidade = {n: i + 1 for i, c in enumerate(sorted(comunidades, key=len, reverse=True)) for n in c}
    nx.set_node_attributes(g, comunidade, "comunidade")
    inter = nx.betweenness_centrality(g, weight="distancia")
    pr = nx.pagerank(g, weight="peso")
    df = pd.DataFrame([{"personagem": n, "mencoes": g.nodes[n]["mencoes"], "grau": g.degree(n),
                        "grau_ponderado": g.degree(n, weight="peso"), "intermediacao": inter[n],
                        "pagerank": pr[n], "comunidade": comunidade[n]} for n in g])
    return df.sort_values("pagerank", ascending=False).reset_index(drop=True)


def ligacoes(g: nx.Graph) -> pd.DataFrame:
    return (pd.DataFrame([(a, b, d["peso"]) for a, b, d in g.edges(data=True)], columns=["origem", "destino", "peso"])
            .sort_values("peso", ascending=False).reset_index(drop=True))


def analisar(paragrafos: list[str], entidades: pd.DataFrame, lingua: str, dicionario: Path | None,
             ignorar: set[str] = frozenset(), min_mencoes: int = 5) -> tuple[nx.Graph, pd.DataFrame, pd.DataFrame, str]:
    if dicionario and dicionario.exists():
        por_par, menc = por_dicionario(paragrafos, dicionario)
        metodo = f"dicionário ({dicionario.name})"
    else:
        por_par, menc = automatico(entidades, lingua, min_mencoes=min_mencoes, ignorar=ignorar)
        metodo = "automático (NER)"
    g = rede(por_par, menc, min_mencoes)
    return g, metricas(g), ligacoes(g), metodo
