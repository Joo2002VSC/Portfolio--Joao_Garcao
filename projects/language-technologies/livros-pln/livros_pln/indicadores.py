"""Indicadores de PLN calculados com spaCy e pandas.

O texto é anotado pelo spaCy e convertido num DataFrame com um token por linha;
todos os indicadores são calculados a partir dessa tabela.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from .lingua import MODELOS

CLASSES = ["NOUN", "VERB", "ADJ", "ADV", "PRON", "PROPN", "DET", "ADP", "CCONJ", "SCONJ", "AUX", "NUM"]
NOMES_CLASSES = {"NOUN": "substantivo", "VERB": "verbo", "ADJ": "adjetivo", "ADV": "advérbio", "PRON": "pronome",
                 "PROPN": "nome próprio", "DET": "determinante", "ADP": "preposição", "CCONJ": "conj. coordenativa",
                 "SCONJ": "conj. subordinativa", "AUX": "auxiliar", "NUM": "numeral"}
ENTIDADES = {"pessoa": {"PER", "PERSON"}, "lugar": {"LOC", "GPE"}, "organizacao": {"ORG"}}
SINAIS = {"virgula": r",", "ponto": r"(?<!\.)\.(?!\.)", "ponto_e_virgula": r";", "dois_pontos": r":",
          "exclamacao": r"!", "interrogacao": r"\?", "reticencias": r"…|\.\.\.", "travessao": r"—",
          "aspas": r"[«»\"“”]", "parenteses": r"\("}
VOGAIS = {"pt": "aeiouáéíóúâêôãõày", "fr": "aeiouyéèêëàâîïôûùüœæ", "en": "aeiouy"}
PALAVRAS_POR_MINUTO = 230
CONFIG = Path(__file__).resolve().parent.parent / "config"
_modelos: dict = {}


def stopwords_extra(lingua: str) -> set[str]:
    """Lê config/stopwords-<língua>.txt (palavras a ignorar, por exemplo grafias antigas)."""
    f = CONFIG / f"stopwords-{lingua}.txt"
    if not f.exists():
        return set()
    return {l.strip().lower() for l in f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")}


def modelo(lingua: str):
    import spacy

    if lingua not in _modelos:
        nlp = spacy.load(MODELOS[lingua], exclude=["textcat"])
        nlp.max_length = 3_000_000
        _modelos[lingua] = nlp
    return _modelos[lingua]


# ---------------------------------------------------------------------------
# Anotação
# ---------------------------------------------------------------------------

def anotar(paragrafos: list[str], lingua: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (tokens, entidades) como DataFrames."""
    nlp = modelo(lingua)
    linhas, ents = [], []
    frase_global = 0
    for p, doc in enumerate(nlp.pipe(paragrafos, batch_size=64)):
        for s in doc.sents:
            for t in s:
                linhas.append((p, frase_global, t.text, t.lemma_.lower(), t.pos_, t.is_alpha, t.is_stop, t.is_punct))
            frase_global += 1
        for e in doc.ents:
            ents.append((p, e.text.strip(), e.label_))
    tokens = pd.DataFrame(linhas, columns=["paragrafo", "frase", "texto", "lema", "pos", "alfa", "stop", "pontuacao"])
    tokens["minusc"] = tokens.texto.str.lower()
    extra = stopwords_extra(lingua)
    if extra:
        tokens["stop"] = tokens.stop | tokens.minusc.isin(extra) | tokens.lema.isin(extra)
    tokens["pos"] = tokens.pos.astype("category")
    entidades = pd.DataFrame(ents, columns=["paragrafo", "entidade", "rotulo"])
    if extra:
        entidades = entidades[~entidades.entidade.str.lower().isin(extra)]
    return tokens, entidades


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

def mattr(palavras: list[str], janela: int = 500) -> float:
    """Moving-Average Type-Token Ratio (Covington e McFall, 2010)."""
    n = len(palavras)
    if n == 0:
        return float("nan")
    if n < janela:
        return len(set(palavras)) / n
    contagem = Counter(palavras[:janela])
    soma = len(contagem)
    for i in range(janela, n):
        saiu = palavras[i - janela]
        contagem[saiu] -= 1
        if not contagem[saiu]:
            del contagem[saiu]
        contagem[palavras[i]] += 1
        soma += len(contagem)
    return soma / (n - janela + 1) / janela


def yule_k(palavras: list[str]) -> float:
    n = len(palavras)
    if not n:
        return float("nan")
    espectro = Counter(Counter(palavras).values())
    return 1e4 * (sum(m * m * v for m, v in espectro.items()) - n) / (n * n)


def silabas(palavra: str, lingua: str) -> int:
    """Contagem aproximada de sílabas por grupos de vogais."""
    p = palavra.lower()
    if lingua == "en" and len(p) > 3 and p.endswith("e") and not p.endswith(("le", "ee")):
        p = p[:-1]
    if lingua == "fr" and len(p) > 3 and p.endswith(("e", "es", "ent")):
        p = re.sub(r"(e|es|ent)$", "", p)
    return max(1, len(re.findall(f"[{VOGAIS[lingua]}]+", p)))


def legibilidade(palavras_por_frase: float, silabas_por_palavra: float, lingua: str) -> float:
    """Índice de facilidade de leitura de Flesch, na adaptação de cada língua.

    pt: Martins et al. (1996); fr: Kandel e Moles (1958); en: Flesch (1948).
    Valores mais altos = leitura mais fácil (aproximadamente 0-100).
    """
    base, k_frase, k_silaba = {"pt": (248.835, 1.015, 84.6), "fr": (207.0, 1.015, 73.6),
                               "en": (206.835, 1.015, 84.6)}[lingua]
    return base - k_frase * palavras_por_frase - k_silaba * silabas_por_palavra


def escala_legibilidade(indice: float) -> str:
    for limite, rotulo in [(90, "muito fácil"), (70, "fácil"), (60, "razoavelmente fácil"), (50, "razoável"),
                           (30, "difícil")]:
        if indice >= limite:
            return rotulo
    return "muito difícil"


def calcular(paragrafos: list[str], tokens: pd.DataFrame, entidades: pd.DataFrame, lingua: str) -> dict:
    palavras_df = tokens[tokens.alfa]
    palavras = palavras_df.minusc.tolist()
    n_pal = len(palavras)
    frases = palavras_df.groupby("frase").size()
    contagem = Counter(palavras)
    conteudo = palavras_df.pos.isin(["NOUN", "VERB", "ADJ", "ADV"]).sum()
    n_sil = sum(silabas(w, lingua) * n for w, n in contagem.items())
    texto = "\n".join(paragrafos)
    dialogo = sum(p.startswith(("—", "–", "-", "«", '"', "“", "'", "‘")) for p in paragrafos)
    pos_pct = (palavras_df.pos.value_counts(normalize=True) * 100).reindex(CLASSES).fillna(0)

    ind = {
        "paragrafos": len(paragrafos),
        "frases": int(frases.size),
        "tokens": int(len(tokens)),
        "palavras": n_pal,
        "caracteres": len(texto),
        "tempo_leitura_horas": round(n_pal / PALAVRAS_POR_MINUTO / 60, 1),
        "vocabulario": len(contagem),
        "lemas_distintos": int(palavras_df.lema.nunique()),
        "ttr": len(contagem) / n_pal if n_pal else np.nan,
        "mattr_500": mattr(palavras),
        "hapax_pct": 100 * sum(v == 1 for v in contagem.values()) / len(contagem) if contagem else np.nan,
        "yule_k": yule_k(palavras),
        "densidade_lexical_pct": 100 * conteudo / n_pal if n_pal else np.nan,
        "palavra_media_letras": float(palavras_df.texto.str.len().mean()),
        "silabas_por_palavra": n_sil / n_pal if n_pal else np.nan,
        "frase_media_palavras": float(frases.mean()),
        "frase_mediana_palavras": float(frases.median()),
        "frase_desvio_padrao": float(frases.std()),
        "frase_maxima_palavras": int(frases.max()),
        "paragrafo_medio_palavras": float(palavras_df.groupby("paragrafo").size().mean()),
        "dialogo_pct": 100 * dialogo / len(paragrafos) if paragrafos else np.nan,
    }
    ind["legibilidade"] = legibilidade(ind["frase_media_palavras"], ind["silabas_por_palavra"], lingua)
    ind["legibilidade_escala"] = escala_legibilidade(ind["legibilidade"])
    for sinal, padrao in SINAIS.items():
        ind[f"{sinal}_por_1000"] = 1000 * len(re.findall(padrao, texto)) / n_pal if n_pal else np.nan
    for classe in CLASSES:
        ind[f"pos_{classe.lower()}_pct"] = float(pos_pct[classe])
    for tipo, rotulos in ENTIDADES.items():
        sub = entidades[entidades.rotulo.isin(rotulos)]
        ind[f"entidades_{tipo}"] = int(sub.entidade.nunique())
    return ind


def frequencias(tokens: pd.DataFrame, n: int = 200) -> pd.DataFrame:
    conteudo = tokens[tokens.alfa & ~tokens.stop & tokens.pos.isin(["NOUN", "VERB", "ADJ", "ADV"])
                      & (tokens.lema.str.len() > 2)]
    freq = conteudo.groupby(["lema", "pos"], observed=True).size().rename("ocorrencias").reset_index()
    freq = freq.sort_values("ocorrencias", ascending=False).head(n)
    freq["por_1000_palavras"] = 1000 * freq.ocorrencias / tokens.alfa.sum()
    return freq.reset_index(drop=True)


def tabela_entidades(entidades: pd.DataFrame, n: int = 25) -> pd.DataFrame:
    tipo = {r: t for t, rs in ENTIDADES.items() for r in rs}
    sub = entidades[entidades.rotulo.isin(tipo)].assign(tipo=lambda d: d.rotulo.map(tipo))
    sub = sub[sub.entidade.str.len() > 1]
    tabela = sub.groupby(["tipo", "entidade"]).size().rename("ocorrencias").reset_index()
    return (tabela.sort_values(["tipo", "ocorrencias"], ascending=[True, False])
            .groupby("tipo").head(n).reset_index(drop=True))


def evolucao(tokens: pd.DataFrame, partes: int = 10) -> pd.DataFrame:
    """Indicadores por décimo do livro (posição na narrativa)."""
    palavras = tokens[tokens.alfa].reset_index(drop=True)
    palavras["parte"] = np.minimum((palavras.index * partes) // max(len(palavras), 1), partes - 1) + 1
    linhas = []
    for parte, grupo in palavras.groupby("parte"):
        frases = grupo.groupby("frase").size()
        linhas.append({"parte": parte, "palavras": len(grupo), "mattr_500": mattr(grupo.minusc.tolist()),
                       "frase_media_palavras": frases.mean(),
                       "densidade_lexical_pct": 100 * grupo.pos.isin(["NOUN", "VERB", "ADJ", "ADV"]).mean()})
    return pd.DataFrame(linhas)


def distribuicao_frases(tokens: pd.DataFrame) -> pd.Series:
    return tokens[tokens.alfa].groupby("frase").size()
