"""Divisão de um livro em capítulos, cantos ou partes, a partir dos títulos do próprio texto.

Um título é um parágrafo curto (até 70 caracteres e 10 palavras) que começa por «Capítulo»,
«Chapitre», «Chapter», «Canto», «Chant», «Livro», «Livre», «Book» ou «Parte»/«Partie»/«Part», ou
que é só um número (romano ou árabe). Os blocos com menos de `minimo_palavras` palavras (por
exemplo, um índice ou um título de parte seguido logo de um título de capítulo) juntam-se ao
bloco seguinte. Se o texto não tiver pelo menos três divisões assim, divide-se em blocos com o
mesmo número de palavras.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_TITULO = re.compile(
    r"^(?:(?:chapitre|chapter|cap[ií]tulo|chant|canto|livre|book|livro|parte?|partie|part)\b.{0,60}"
    r"|.{0,30}\b(?:partie|parte|part)"
    r"|[IVXLCDM]{1,7}\.?"
    r"|\d{1,3}\.?)$", re.I)


@dataclass
class Divisao:
    segmento: list[int]   # segmento (1…k) de cada parágrafo
    rotulos: list[str]    # rótulo de cada segmento
    metodo: str           # «capítulos» ou «blocos»

    @property
    def n(self) -> int:
        return len(self.rotulos)


def e_titulo(paragrafo: str) -> bool:
    p = paragrafo.strip()
    return 0 < len(p) <= 70 and len(p.split()) <= 10 and bool(_TITULO.match(p))


def _blocos(palavras: list[int], k: int) -> Divisao:
    total = sum(palavras)
    k = max(1, min(k, total // 50 or 1))
    seg, acumulado = [], 0
    for n in palavras:
        seg.append(min(k, acumulado * k // total + 1) if total else 1)
        acumulado += n
    usados = sorted(set(seg))
    mapa = {s: i + 1 for i, s in enumerate(usados)}
    return Divisao([mapa[s] for s in seg], [f"Bloco {i}" for i in range(1, len(usados) + 1)], "blocos")


def dividir(paragrafos: list[str], minimo_palavras: int = 300, blocos: int = 20, maximo: int = 200) -> Divisao:
    palavras = [len(p.split()) for p in paragrafos]
    titulos = [i for i, p in enumerate(paragrafos) if e_titulo(p)]
    if len(titulos) >= 3:
        # inícios dos segmentos: cada título; o texto antes do primeiro título junta-se ao primeiro segmento
        inicios = titulos
        segmentos: list[tuple[int, int, list[str]]] = []
        for j, ini in enumerate(inicios):
            fim = inicios[j + 1] if j + 1 < len(inicios) else len(paragrafos)
            segmentos.append((ini, fim, [paragrafos[ini].strip()]))
        if inicios[0] > 0:
            a, b, r = segmentos[0]
            segmentos[0] = (0, b, r)
        # junta os blocos demasiado curtos ao seguinte (índices, títulos de parte)
        juntos: list[tuple[int, int, list[str]]] = []
        pendente: tuple[int, list[str]] | None = None
        for a, b, r in segmentos:
            if pendente:
                a, r = pendente[0], pendente[1] + r
                pendente = None
            if sum(palavras[a:b]) < minimo_palavras:
                pendente = (a, r)
                continue
            juntos.append((a, b, r))
        if pendente and juntos:
            a, b, r = juntos[-1]
            juntos[-1] = (a, len(paragrafos), r)
        if 3 <= len(juntos) <= maximo:
            seg = [0] * len(paragrafos)
            for k, (a, b, _) in enumerate(juntos, 1):
                for i in range(a, b):
                    seg[i] = k
            rotulos = [" · ".join(dict.fromkeys(r))[:60] for _, _, r in juntos]
            return Divisao(seg, rotulos, "capítulos")
    return _blocos(palavras, blocos)
