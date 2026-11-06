"""Análise de sentimento por frase, com léxicos e regras do método VADER.

Cada frase recebe uma pontuação «compound» entre −1 (muito negativa) e +1 (muito positiva),
calculada a partir de um léxico de palavras com valência e de regras para intensificadores,
negação, pontuação e maiúsculas (Hutto e Gilbert, 2014). Cada língua usa uma adaptação do
VADER com o seu léxico:

- inglês: vaderSentiment (Hutto e Gilbert, 2014);
- português: LeIA, léxico traduzido e adaptado para português do Brasil (Almeida, 2018);
- francês: VADER-FR, léxico traduzido manualmente para francês.

Os três léxicos foram criados para textos curtos das redes sociais, não para prosa literária, e
não foram validados neste projeto com anotação humana: os valores descrevem a polaridade do
vocabulário, não o tom narrativo, a ironia ou as emoções das personagens. Os valores de
línguas diferentes não são comparáveis (léxicos diferentes).
"""
from __future__ import annotations

import importlib
import importlib.metadata
import logging
import warnings

import numpy as np
import pandas as pd

from . import qualidade
from .configuracao import PARAMETROS

# língua → (módulo, pacote pip, nome do método)
ANALISADORES = {
    "en": ("vaderSentiment.vaderSentiment", "vaderSentiment", "VADER (vaderSentiment)"),
    "pt": ("LeIA", "leia-br", "LeIA (VADER adaptado ao português)"),
    "fr": ("vaderSentiment_fr.vaderSentiment", "vaderSentiment-fr", "VADER-FR (VADER adaptado ao francês)"),
}
_CACHE: dict = {}


def analisador(lingua: str):
    """Devolve (analisador, descrição do método). Lança ImportError se o pacote não estiver instalado."""
    if lingua not in ANALISADORES:
        raise KeyError(lingua)
    if lingua not in _CACHE:
        modulo, pacote, nome = ANALISADORES[lingua]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            logging.getLogger("fuzzywuzzy").setLevel(logging.ERROR)
            classe = importlib.import_module(modulo).SentimentIntensityAnalyzer
            try:
                versao = importlib.metadata.version(pacote)
            except importlib.metadata.PackageNotFoundError:
                versao = "?"
            _CACHE[lingua] = (classe(), f"{nome} {versao}")
    return _CACHE[lingua]


def _vazio(motivo: str, estado: str) -> dict:
    return {"estado": estado, "motivo": motivo, "metodo": None, "indicadores": {}, "extremos": pd.DataFrame()}


def analisar(frases: pd.DataFrame, tokens: pd.DataFrame, lingua: str, p=PARAMETROS) -> dict:
    """Pontua cada frase e acrescenta a coluna `sentimento` a `frases` (NaN nas frases curtas).

    Devolve {"estado", "motivo", "metodo", "indicadores", "extremos"}."""
    frases["sentimento"] = np.nan
    try:
        sia, metodo = analisador(lingua)
    except KeyError:
        return _vazio(f"sem léxico de sentimento para a língua «{lingua}»", qualidade.NAO_APLICAVEL)
    except ImportError:
        pacote = ANALISADORES[lingua][1]
        return _vazio(f"o pacote {pacote} não está instalado (pip install -r requirements.txt)",
                      qualidade.DESCONHECIDO)

    elegiveis = frases.palavras >= p.sentimento_minimo_palavras
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        frases.loc[elegiveis, "sentimento"] = [sia.polarity_scores(t)["compound"]
                                               for t in frases.loc[elegiveis, "texto"]]
    pontuadas = frases.sentimento.dropna()
    if pontuadas.empty:
        return _vazio("nenhuma frase com extensão suficiente", qualidade.NAO_APLICAVEL)

    lexico = {k.lower() for k in sia.lexicon}
    palavras = tokens.loc[tokens.alfa, "minusc"]
    limiar = p.sentimento_limiar
    ind = {
        "sentimento_medio": float(pontuadas.mean()),
        "frases_positivas_pct": 100 * float((pontuadas >= limiar).mean()),
        "frases_negativas_pct": 100 * float((pontuadas <= -limiar).mean()),
        "frases_neutras_pct": 100 * float(((pontuadas > -limiar) & (pontuadas < limiar)).mean()),
        "cobertura_lexico_pct": 100 * float(palavras.isin(lexico).mean()) if len(palavras) else float("nan"),
    }
    return {"estado": "valido", "motivo": None, "metodo": metodo, "indicadores": ind,
            "extremos": extremos(frases)}


def extremos(frases: pd.DataFrame, n: int = 3, minimo: int = 8, maximo: int = 60, corte: int = 280) -> pd.DataFrame:
    """As `n` frases mais positivas e mais negativas, com extensão entre `minimo` e `maximo` palavras."""
    f = frases[(frases.palavras >= minimo) & (frases.palavras <= maximo)].dropna(subset=["sentimento"])
    if f.empty:
        return pd.DataFrame(columns=["polaridade", "sentimento", "frase", "texto"])
    pos = f[f.sentimento > 0].nlargest(n, "sentimento").assign(polaridade="positiva")
    neg = f[f.sentimento < 0].nsmallest(n, "sentimento").assign(polaridade="negativa")
    out = pd.concat([pos, neg])[["polaridade", "sentimento", "frase", "texto"]]
    out["texto"] = out.texto.str.replace(r"\s+", " ", regex=True).map(
        lambda t: t if len(t) <= corte else t[: corte - 1].rsplit(" ", 1)[0] + "…")
    return out.reset_index(drop=True)
