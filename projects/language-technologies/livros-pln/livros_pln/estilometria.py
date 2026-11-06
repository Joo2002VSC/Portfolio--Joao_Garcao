"""Estilometria: Delta de Burrows (2002) entre livros da mesma língua.

Método:
  1. por língua, as N palavras mais frequentes (MFW) no conjunto dos textos;
  2. frequência relativa de cada palavra em cada texto;
  3. z-score de cada palavra (média e desvio-padrão entre os textos);
  4. Delta(A, B) = média, sobre as N palavras, de |z_A − z_B|.

Condições de uso (Burrows, 2002; Evert et al., 2017):
  * só textos da mesma língua; com menos de `delta_minimo_textos` textos, os z-scores não
    têm significado e o Delta não é calculado;
  * textos de extensão e género comparáveis; a fiabilidade diminui com textos curtos;
  * o Delta mede distância estilística relativa dentro de um corpus: valores de corpora
    diferentes não são comparáveis e uma distância pequena não prova autoria.
"""
from __future__ import annotations

import pandas as pd

from .configuracao import PARAMETROS


def delta(frequencias: dict[str, pd.Series], linguas: dict[str, str], p=PARAMETROS) -> dict[str, dict]:
    """`frequencias`: id do livro → Série (forma → ocorrências). Devolve, por língua, estado, matriz e palavras."""
    resultado = {}
    for lg in sorted(set(linguas.values())):
        ids = sorted(i for i, l in linguas.items() if l == lg and i in frequencias)
        if len(ids) < p.delta_minimo_textos:
            resultado[lg] = {"estado": "nao_aplicavel", "matriz": None, "palavras": [],
                             "motivo": f"{len(ids)} livro(s) nesta língua; são precisos pelo menos "
                                       f"{p.delta_minimo_textos} para calcular z-scores"}
            continue
        relativas = pd.DataFrame({i: frequencias[i] / frequencias[i].sum() for i in ids}).fillna(0.0)
        mfw = relativas.mean(axis=1).sort_values(ascending=False).head(p.delta_palavras_frequentes).index
        tabela = relativas.loc[mfw]
        desvio = tabela.std(axis=1, ddof=1).replace(0, float("nan"))
        z = tabela.sub(tabela.mean(axis=1), axis=0).div(desvio, axis=0).dropna()
        matriz = pd.DataFrame({a: {b: float((z[a] - z[b]).abs().mean()) for b in ids} for a in ids})
        resultado[lg] = {"estado": "valido", "matriz": matriz.loc[ids, ids], "palavras": list(z.index),
                         "motivo": f"{len(z)} palavras mais frequentes, {len(ids)} livros"}
    return resultado
