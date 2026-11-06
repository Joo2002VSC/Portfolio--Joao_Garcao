"""Indicadores de PLN calculados com spaCy e pandas.

O texto é anotado pelo spaCy e convertido em duas tabelas pandas: uma com um token por
linha e outra com uma frase por linha (extensão, profundidade da árvore de dependências,
distância de dependência, orações subordinadas). Todos os indicadores são calculados a
partir dessas tabelas. As definições, fórmulas e referências estão em `catalogo.py`.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from . import qualidade
from .catalogo import CLASSES, NOMES_CLASSES  # noqa: F401  (reexportado para os outros módulos)
from .configuracao import PARAMETROS
from .lingua import MODELOS

ENTIDADES = {"pessoa": {"PER", "PERSON"}, "lugar": {"LOC", "GPE"}, "organizacao": {"ORG"}}
CONTEUDO = ["NOUN", "VERB", "ADJ", "ADV"]
SINAIS = {"virgula": r",", "ponto": r"(?<!\.)\.(?!\.)", "ponto_e_virgula": r";", "dois_pontos": r":",
          "exclamacao": r"!", "interrogacao": r"\?", "reticencias": r"…|\.\.\.", "travessao": r"—",
          "aspas": r"[«»\"“”]", "parenteses": r"\("}
# relações que introduzem orações subordinadas: Universal Dependencies (pt, fr) e ClearNLP (en)
SUBORDINADAS = {"advcl", "ccomp", "csubj", "csubj:pass", "csubjpass", "acl", "acl:relcl", "relcl"}
MODAIS = {"pt": {"poder", "dever"}, "fr": {"pouvoir", "devoir"}}
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


def info_modelo(lingua: str) -> dict:
    """Nome, versão e exatidão declarada do modelo (meta do próprio pacote spaCy)."""
    m = modelo(lingua).meta
    desempenho = m.get("performance", {}) or {}
    chaves = {"pos_acc": "pos", "tag_acc": "etiquetas_finas", "morph_acc": "morfologia", "dep_las": "dependencias_las", "dep_uas": "dependencias_uas",
              "sents_f": "frases_f", "ents_f": "entidades_f", "lemma_acc": "lemas"}
    return {"nome": f"{m.get('lang')}_{m.get('name')}", "versao": m.get("version"),
            "spacy": m.get("spacy_version"),
            "exatidao": {rot: round(float(desempenho[k]), 4) for k, rot in chaves.items() if desempenho.get(k) is not None}}


# ---------------------------------------------------------------------------
# Anotação
# ---------------------------------------------------------------------------

def _sintaxe(frase) -> tuple[int, int, int, int]:
    """(profundidade máxima, soma das distâncias, número de dependências, orações subordinadas) de uma frase."""
    palavras = [t for t in frase if not t.is_punct and not t.is_space]
    if not palavras:
        return 0, 0, 0, 0
    posicao = {t.i: k for k, t in enumerate(palavras)}
    profundidade: dict[int, int] = {}

    def nivel(t, guarda=0):
        if t.i in profundidade:
            return profundidade[t.i]
        if t.head.i == t.i or guarda > 200:
            profundidade[t.i] = 0
        else:
            profundidade[t.i] = nivel(t.head, guarda + 1) + 1
        return profundidade[t.i]

    maxima = max(nivel(t) for t in palavras)
    distancias = [abs(posicao[t.i] - posicao[t.head.i]) for t in palavras
                  if t.head.i != t.i and t.head.i in posicao]
    subordinadas = sum(1 for t in palavras if t.dep_.lower() in SUBORDINADAS)
    return maxima, sum(distancias), len(distancias), subordinadas


def _traco(morph, nome: str) -> str:
    v = morph.get(nome)
    return v[0] if v else ""


_FECHO = "\"'»”’)]—–- \u00a0"


def tipo_frase(texto: str) -> str:
    """Declarativa, interrogativa ou exclamativa, pela pontuação final (ignorando aspas e travessões de fecho)."""
    fim = texto.rstrip(_FECHO)
    if fim.endswith("?") or fim.endswith("?!") or fim.endswith("!?"):
        return "interrogativa"
    if fim.endswith("!"):
        return "exclamativa"
    return "declarativa"


def anotar(paragrafos: list[str], lingua: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Devolve (tokens, frases, entidades) como DataFrames."""
    nlp = modelo(lingua)
    linhas, frases, ents = [], [], []
    f = 0
    for p, doc in enumerate(nlp.pipe(paragrafos, batch_size=64)):
        for s in doc.sents:
            n_palavras = 0
            for t in s:
                m = t.morph
                pessoal = t.pos_ == "PRON" and "Prs" in m.get("PronType")
                linhas.append((p, f, t.text, t.lemma_.lower(), t.pos_, t.tag_, t.is_alpha, t.is_stop, pessoal,
                               _traco(m, "Tense"), _traco(m, "Mood"), _traco(m, "Person"), _traco(m, "VerbForm")))
                n_palavras += t.is_alpha
            prof, soma, n_dep, sub = _sintaxe(s)
            frases.append((f, p, n_palavras, prof, soma, n_dep, sub, tipo_frase(s.text), s.text.strip()))
            f += 1
        for e in doc.ents:
            ents.append((p, e.text.strip(), e.label_))
    tokens = pd.DataFrame(linhas, columns=["paragrafo", "frase", "texto", "lema", "pos", "tag", "alfa", "stop",
                                           "pronome_pessoal", "tempo", "modo", "pessoa", "forma_verbal"])
    for c in ("tempo", "modo", "pessoa", "forma_verbal"):
        tokens[c] = tokens[c].astype("category")
    tokens["minusc"] = tokens.texto.str.lower()
    extra = stopwords_extra(lingua)
    if extra:
        tokens["stop"] = tokens.stop | tokens.minusc.isin(extra) | tokens.lema.isin(extra)
    tokens["pos"] = tokens.pos.astype("category")
    frases_df = pd.DataFrame(frases, columns=["frase", "paragrafo", "palavras", "profundidade", "soma_distancias",
                                              "dependencias", "subordinadas", "tipo", "texto"])
    entidades = pd.DataFrame(ents, columns=["paragrafo", "entidade", "rotulo"])
    if extra:
        entidades = entidades[~entidades.entidade.str.lower().isin(extra)]
    return tokens, frases_df, entidades


# ---------------------------------------------------------------------------
# Diversidade lexical
# ---------------------------------------------------------------------------

def ttr(palavras: list[str]) -> float:
    return len(set(palavras)) / len(palavras) if palavras else float("nan")


def mattr(palavras: list[str], janela: int = 500) -> float:
    """Moving-Average Type-Token Ratio (Covington e McFall, 2010). NaN se o texto for mais curto do que a janela."""
    n = len(palavras)
    if n < janela or janela <= 0:
        return float("nan")
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


def _mtld_sentido(palavras: list[str], limiar: float, minimo: int) -> float:
    fatores, tipos, inicio = 0.0, set(), 0
    for i, w in enumerate(palavras):
        tipos.add(w)
        extensao = i - inicio + 1
        if len(tipos) / extensao < limiar and extensao >= minimo:
            fatores += 1
            tipos, inicio = set(), i + 1
    resto = len(palavras) - inicio
    if resto:
        fatores += (1 - len(tipos) / resto) / (1 - limiar)   # fator parcial
    return len(palavras) / fatores if fatores else float("nan")


def mtld(palavras: list[str], limiar: float = 0.72, minimo_fator: int = 10) -> float:
    """Measure of Textual Lexical Diversity (McCarthy e Jarvis, 2010): média dos sentidos direto e inverso."""
    if not palavras:
        return float("nan")
    return (_mtld_sentido(palavras, limiar, minimo_fator) + _mtld_sentido(palavras[::-1], limiar, minimo_fator)) / 2


def hdd(palavras: list[str], amostra: int = 42) -> float:
    """HD-D (McCarthy e Jarvis, 2010): Σ_formas P(forma ocorre numa amostra de `amostra` palavras) / amostra."""
    from scipy.stats import hypergeom

    n = len(palavras)
    if n < amostra:
        return float("nan")
    espectro = Counter(Counter(palavras).values())     # frequência → número de formas com essa frequência
    total = sum(v * (1 - hypergeom.pmf(0, n, f, amostra)) for f, v in espectro.items())
    return total / amostra


def yule_k(palavras: list[str]) -> float:
    n = len(palavras)
    if not n:
        return float("nan")
    espectro = Counter(Counter(palavras).values())
    return 1e4 * (sum(m * m * v for m, v in espectro.items()) - n) / (n * n)


# ---------------------------------------------------------------------------
# Sílabas e legibilidade
# ---------------------------------------------------------------------------

VOGAIS = {"pt": "aeiouáéíóúâêôãõàü", "fr": "aeiouyéèêëàâîïôûùüœæ", "en": "aeiouy"}
FORTES_PT = set("aeoáéóâêôãõà")
NASAIS_PT = {"ão", "õe", "ãe", "ãi", "õi"}


def silabas(palavra: str, lingua: str) -> int:
    """Estimativa do número de sílabas.

    pt: grupos de vogais, separando hiatos entre vogais fortes («po-e-ta») e junto de «í»/«ú»
        acentuados («sa-ú-de»); ditongos com i/u átonos contam como uma sílaba.
    fr: grupos de vogais, sem o «e» mudo final («-e», «-es», «-ent» verbal).
    en: grupos de vogais, sem o «e» final mudo e o «-ed» sem som silábico.
    Validação: ver tests/test_silabas.py (palavras com silabação anotada à mão).
    """
    p = palavra.lower()
    if lingua == "en":
        if len(p) > 3 and p.endswith("e") and not p.endswith(("le", "ee", "ye")):
            p = p[:-1]
        if len(p) > 3 and p.endswith("ed") and not p.endswith(("ted", "ded")):
            p = p[:-2] + "d"
    if lingua == "fr" and len(p) > 3:
        p = re.sub(r"(?<=[^aeiouy])(e|es|ent)$", "", p) if not p.endswith(("ée", "ées")) else p
    grupos = re.findall(f"[{VOGAIS[lingua]}]+", p)
    if lingua == "en":
        # hiatos frequentes: «cu-ri-ous», «i-de-a», «po-em», «sci-ence», mas não «-tion», «-cious»
        extra = len(re.findall(r"(?<![tsc])i[aou]|ea$|oe(?!s?$)|ie(?=n)", p))
        return max(1, len(grupos) + extra)
    if lingua != "pt":
        return max(1, len(grupos))
    total = 0
    for m in re.finditer(f"[{VOGAIS[lingua]}]+", p):
        g, antes = m.group(0), p[m.start() - 1] if m.start() else ""
        n = 1
        for k, (a, b) in enumerate(zip(g, g[1:])):
            anterior = g[k - 1] if k else antes
            semivogal_qg = a == "u" and anterior in "qg"            # «qua», «gua»: u não é núcleo
            if a + b in NASAIS_PT:                                   # «ão», «õe», «ãe», «ãi»: ditongo
                continue
            if (a in FORTES_PT and b in FORTES_PT) \
                    or (b in "íú" and not semivogal_qg) \
                    or (a in "iuíú" and b in FORTES_PT and not semivogal_qg):   # hiatos: «po-e-ta», «ri-o»
                n += 1
        total += n
    return max(1, total)


COEFICIENTES_FLESCH = {"en": (206.835, 1.015, 84.6), "fr": (207.0, 1.015, 73.6), "pt": (248.835, 1.015, 84.6)}


def legibilidade(palavras_por_frase: float, silabas_por_palavra: float, lingua: str) -> float:
    """Índice de facilidade de leitura de Flesch, na adaptação de cada língua (ver catálogo)."""
    base, k_frase, k_silaba = COEFICIENTES_FLESCH[lingua]
    return base - k_frase * palavras_por_frase - k_silaba * silabas_por_palavra


def flesch_kincaid(palavras_por_frase: float, silabas_por_palavra: float) -> float:
    """Nível de escolaridade de Flesch-Kincaid (Kincaid et al., 1975). Só para inglês."""
    return 0.39 * palavras_por_frase + 11.8 * silabas_por_palavra - 15.59


# Faixas de interpretação. Português: Martins et al. (1996), que indicam também o nível escolar (sistema escolar
# brasileiro). Inglês e francês: escala de Flesch (1948), que Kandel e Moles (1958) mantiveram para o francês.
FAIXAS_FLESCH = [(90, "muito fácil"), (80, "fácil"), (70, "razoavelmente fácil"), (60, "padrão"),
                 (50, "razoavelmente difícil"), (30, "difícil"), (-math.inf, "muito difícil")]
FAIXAS_MARTINS = [(75, "muito fácil", "1.º ao 4.º ano de escolaridade"), (50, "fácil", "5.º ao 8.º ano de escolaridade"),
                  (25, "razoavelmente difícil", "ensino secundário e superior"),
                  (-math.inf, "muito difícil", "textos académicos")]
# Fronteira entre leitura «fácil» e «difícil»: pt 50 (Martins et al., 1996: fácil ≥ 50); en e fr 60 (Flesch, 1948:
# a partir de 60, «padrão» ou mais fácil).
FRONTEIRA_LEITURA = {"pt": 50, "fr": 60, "en": 60}


def _vazio(indice) -> bool:
    return indice is None or (isinstance(indice, float) and math.isnan(indice))


def escala_legibilidade(indice: float | None, lingua: str = "en") -> str | None:
    if _vazio(indice):
        return None
    faixas = [(lim, rot) for lim, rot, _ in FAIXAS_MARTINS] if lingua == "pt" else FAIXAS_FLESCH
    return next(rot for lim, rot in faixas if indice >= lim)


def nivel_escolar(indice: float | None, lingua: str) -> str | None:
    """Nível escolar correspondente (só português, segundo Martins et al., 1996)."""
    if _vazio(indice) or lingua != "pt":
        return None
    return next(nivel for lim, _, nivel in FAIXAS_MARTINS if indice >= lim)


def leitura(indice: float | None, lingua: str) -> str | None:
    """Classificação simplificada da leitura: «fácil» ou «difícil»."""
    if _vazio(indice):
        return None
    return "fácil" if indice >= FRONTEIRA_LEITURA.get(lingua, 60) else "difícil"


# ---------------------------------------------------------------------------
# Diálogo
# ---------------------------------------------------------------------------

_FALA = re.compile(r"[“«\"][^“”«»\"]{3,}[”»\"]|(^|\s)[‘']\S[^‘'’\n]*?[,.!?—-][’'](\s|$)")


def e_dialogo(paragrafo: str) -> bool:
    """Heurística tipográfica: começa por travessão/aspas ou contém uma fala entre aspas."""
    return paragrafo.startswith(("—", "–", "--", "- ", "«", '"', "“", "‘", "'")) or bool(_FALA.search(paragrafo))


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------

def calcular(paragrafos: list[str], tokens: pd.DataFrame, frases: pd.DataFrame, entidades: pd.DataFrame,
             lingua: str, p=PARAMETROS) -> tuple[dict, dict]:
    """Devolve (indicadores, estados). Ver `catalogo.INDICADORES` para as definições."""
    d = qualidade.dividir
    palavras_df = tokens[tokens.alfa]
    palavras = palavras_df.minusc.tolist()
    n = len(palavras)
    contagem = Counter(palavras)
    frases_validas = frases[frases.palavras > 0]
    ext = frases_validas.palavras
    n_sil = sum(silabas(w, lingua) * c for w, c in contagem.items())
    texto = "\n".join(paragrafos)
    pos_contagem = palavras_df.pos.value_counts()

    ind = {
        "palavras": n,
        "frases": int(len(frases_validas)),
        "paragrafos": len(paragrafos),
        "tempo_leitura_horas": d(n, p.palavras_por_minuto * 60),
        "vocabulario": len(contagem),
        "lemas_distintos": int(palavras_df.lema.nunique()),
        "ttr": ttr(palavras),
        "mattr": mattr(palavras, p.janela_mattr),
        "mtld": mtld(palavras, p.limiar_mtld, p.minimo_fator_mtld) if n >= p.minimo_mtld else float("nan"),
        "hdd": hdd(palavras, p.amostra_hdd),
        "yule_k": yule_k(palavras),
        "hapax_pct": 100 * d(sum(v == 1 for v in contagem.values()), len(contagem)),
        "densidade_lexical_pct": 100 * d(int(palavras_df.pos.isin(CONTEUDO).sum()), n),
        "palavra_media_letras": float(palavras_df.texto.str.len().mean()) if n else float("nan"),
        "frase_media": float(ext.mean()) if len(ext) else float("nan"),
        "frase_mediana": float(ext.median()) if len(ext) else float("nan"),
        "frase_p25": float(ext.quantile(0.25)) if len(ext) else float("nan"),
        "frase_p75": float(ext.quantile(0.75)) if len(ext) else float("nan"),
        "frase_desvio_padrao": float(ext.std()) if len(ext) > 1 else float("nan"),
        "frase_maxima": int(ext.max()) if len(ext) else None,
        "frases_longas_pct": 100 * d(int((ext > p.frase_longa).sum()), len(ext)),
        "paragrafo_medio": float(palavras_df.groupby("paragrafo").size().mean()) if n else float("nan"),
        "profundidade_media": float(frases_validas.profundidade.mean()) if len(ext) else float("nan"),
        "distancia_dependencia": d(int(frases_validas.soma_distancias.sum()), int(frases_validas.dependencias.sum())),
        "subordinadas_por_frase": d(int(frases_validas.subordinadas.sum()), len(frases_validas)),
        "silabas_por_palavra": d(n_sil, n),
        "dialogo_pct": 100 * d(sum(e_dialogo(x) for x in paragrafos), len(paragrafos)),
    }
    pf, sp = ind["frase_media"], ind["silabas_por_palavra"]
    ind["legibilidade"] = legibilidade(pf, sp, lingua)
    ind["flesch_kincaid"] = flesch_kincaid(pf, sp) if lingua == "en" else float("nan")
    for sinal, padrao in SINAIS.items():
        ind[f"{sinal}_por_1000"] = 1000 * d(len(re.findall(padrao, texto)), n)
    for classe in CLASSES:
        ind[f"pos_{classe.lower()}_por_1000"] = 1000 * d(int(pos_contagem.get(classe, 0)), n)
    ind["pronomes_pessoais_por_1000"] = 1000 * d(int(tokens.pronome_pessoal.sum()), n)
    if lingua == "en":
        modais = int((tokens.tag == "MD").sum())
    else:
        modais = int((tokens.pos.isin(["VERB", "AUX"]) & tokens.lema.isin(MODAIS[lingua])).sum())
    ind["modais_por_1000"] = 1000 * d(modais, n)
    # tipos de frase
    if len(frases_validas):
        tipos = frases_validas.tipo.value_counts()
        ind["frases_interrogativas_pct"] = 100 * d(int(tipos.get("interrogativa", 0)), len(frases_validas))
        ind["frases_exclamativas_pct"] = 100 * d(int(tipos.get("exclamativa", 0)), len(frases_validas))
    # morfologia verbal (só formas finitas com o traço anotado)
    finitos = tokens[tokens.pos.isin(["VERB", "AUX"]) & (tokens.forma_verbal == "Fin")]
    com_tempo = finitos[finitos.tempo != ""]
    com_modo = finitos[finitos.modo != ""]
    ind["verbos_presente_pct"] = 100 * d(int((com_tempo.tempo == "Pres").sum()), len(com_tempo))
    ind["verbos_passado_pct"] = 100 * d(int(com_tempo.tempo.isin(["Past", "Imp", "Pqp"]).sum()), len(com_tempo))
    ind["verbos_futuro_pct"] = 100 * d(int(com_tempo.tempo.isin(["Fut"]).sum()), len(com_tempo))
    ind["verbos_conjuntivo_pct"] = 100 * d(int((com_modo.modo == "Sub").sum()), len(com_modo))
    pronomes = tokens[tokens.pronome_pessoal]
    for pessoa in ("1", "2", "3"):
        ind[f"pronomes_{pessoa}a_pessoa_por_1000"] = 1000 * d(int((pronomes.pessoa == pessoa).sum()), n)
    # leis do vocabulário
    ind.update(zipf(contagem, p.zipf_frequencia_minima))
    ind.update(heaps(palavras))
    for tipo, rotulos in ENTIDADES.items():
        ind[f"entidades_{tipo}"] = int(entidades[entidades.rotulo.isin(rotulos)].entidade.nunique())
    todas = set().union(*ENTIDADES.values())
    ind["entidades_por_1000"] = 1000 * d(int(entidades.rotulo.isin(todas).sum()), n)

    estados = qualidade.aplicabilidade(n, lingua, p)
    if lingua == "en":
        motivo = ("o inglês forma o futuro e o conjuntivo com auxiliares ou formas iguais às do presente, sem traço "
                  "morfológico próprio no modelo")
        for k in ("verbos_futuro_pct", "verbos_conjuntivo_pct"):
            estados[k] = {"estado": qualidade.NAO_APLICAVEL, "motivo": motivo}
    if len(com_tempo) < 50:
        for k in ("verbos_presente_pct", "verbos_passado_pct", "verbos_futuro_pct", "verbos_conjuntivo_pct"):
            estados.setdefault(k, {"estado": qualidade.NAO_APLICAVEL,
                                   "motivo": "menos de 50 formas verbais finitas com tempo anotado"})
    if not len(ext):
        for k in [k for k in ind if k.startswith(("frase_", "profundidade", "distancia", "subordinadas", "legibilidade",
                                                   "flesch"))]:
            estados.setdefault(k, {"estado": qualidade.DESCONHECIDO, "motivo": "nenhuma frase segmentada"})
    ind, estados = qualidade.sanear(ind, estados)
    ind["legibilidade_escala"] = escala_legibilidade(ind["legibilidade"], lingua)
    ind["legibilidade_leitura"] = leitura(ind["legibilidade"], lingua)
    ind["legibilidade_nivel"] = nivel_escolar(ind["legibilidade"], lingua)
    return ind, estados


# ---------------------------------------------------------------------------
# Leis do vocabulário: Zipf e Heaps
# ---------------------------------------------------------------------------

def _regressao_log(x, y) -> tuple[float, float, float]:
    """Regressão linear de log10(y) em log10(x). Devolve (declive, ordenada na origem, R²)."""
    lx, ly = np.log10(np.asarray(x, float)), np.log10(np.asarray(y, float))
    declive, origem = np.polyfit(lx, ly, 1)
    previsto = declive * lx + origem
    soma_total = ((ly - ly.mean()) ** 2).sum()
    r2 = 1 - ((ly - previsto) ** 2).sum() / soma_total if soma_total else float("nan")
    return float(declive), float(origem), float(r2)


def zipf(contagem: Counter, frequencia_minima: int = 5) -> dict:
    """Lei de Zipf (1949): f(r) ∝ r^−s. Ajuste por mínimos quadrados em escala log-log, só com as formas que
    ocorrem pelo menos `frequencia_minima` vezes (o patamar dos hapax distorce o declive)."""
    freqs = sorted((f for f in contagem.values() if f >= frequencia_minima), reverse=True)
    if len(freqs) < 10:
        return {"zipf_expoente": float("nan"), "zipf_r2": float("nan")}
    declive, _, r2 = _regressao_log(range(1, len(freqs) + 1), freqs)
    return {"zipf_expoente": -declive, "zipf_r2": r2}


def curva_heaps(palavras: list[str], pontos: int = 60) -> pd.DataFrame:
    """Crescimento do vocabulário: formas distintas (V) depois de N palavras, em pontos espaçados em log."""
    n = len(palavras)
    if n < 2:
        return pd.DataFrame(columns=["palavras", "vocabulario"])
    marcas = sorted(set(np.unique(np.geomspace(10, n, pontos).astype(int)).tolist()) | {n})
    vistos, linhas, i = set(), [], 0
    for m in marcas:
        vistos.update(palavras[i:m])
        i = m
        linhas.append((m, len(vistos)))
    return pd.DataFrame(linhas, columns=["palavras", "vocabulario"])


def heaps(palavras: list[str]) -> dict:
    """Lei de Heaps (1978): V(N) = K·N^β, ajustada em escala log-log sobre a curva de crescimento do vocabulário."""
    curva = curva_heaps(palavras)
    curva = curva[curva.palavras >= 100]
    if len(curva) < 5:
        return {"heaps_beta": float("nan"), "heaps_k": float("nan"), "heaps_r2": float("nan")}
    declive, origem, r2 = _regressao_log(curva.palavras, curva.vocabulario)
    return {"heaps_beta": declive, "heaps_k": 10 ** origem, "heaps_r2": r2}


def tabela_zipf(contagem, frequencia_minima: int = 5) -> pd.DataFrame:
    """Posição e frequência das formas usadas no ajuste da lei de Zipf (as que ocorrem pelo menos `frequencia_minima`
    vezes), para que o gráfico e o indicador assentem exatamente nos mesmos dados."""
    freqs = sorted(((w, f) for w, f in contagem.items() if f >= frequencia_minima), key=lambda kv: -kv[1])
    return pd.DataFrame([(r, w, f) for r, (w, f) in enumerate(freqs, start=1)], columns=["posicao", "forma", "frequencia"])


# ---------------------------------------------------------------------------
# Colocações (Dunning, 1993; Church e Hanks, 1990) e palavras-chave por segmento (TF-IDF)
# ---------------------------------------------------------------------------

def _xlogx(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(a > 0, a * np.log(a / b), 0.0)


def colocacoes(tokens: pd.DataFrame, frequencia_minima: int = 5, n: int = 30) -> pd.DataFrame:
    """Pares de palavras contíguas (na mesma frase) que ocorrem juntas mais do que o acaso faria prever.

    Ordenadas pela razão de verosimilhança G² (Dunning, 1993); inclui também a informação mútua pontual (PMI;
    Church e Hanks, 1990). Exclui pares em que as duas palavras são palavras gramaticais (stopwords)."""
    t = tokens[tokens.alfa][["frase", "minusc", "stop"]].reset_index(drop=True)
    if len(t) < 2:
        return pd.DataFrame(columns=["colocacao", "ocorrencias", "g2", "pmi"])
    mesma = (t.frase.values[1:] == t.frase.values[:-1])
    pares = pd.DataFrame({"w1": t.minusc.values[:-1][mesma], "w2": t.minusc.values[1:][mesma],
                          "s1": t.stop.values[:-1][mesma], "s2": t.stop.values[1:][mesma]})
    total = len(pares)
    if not total:
        return pd.DataFrame(columns=["colocacao", "ocorrencias", "g2", "pmi"])
    f1, f2 = pares.w1.value_counts(), pares.w2.value_counts()
    c = pares[~(pares.s1 & pares.s2)].groupby(["w1", "w2"]).size().rename("o11").reset_index()
    c = c[c.o11 >= frequencia_minima]
    if c.empty:
        return pd.DataFrame(columns=["colocacao", "ocorrencias", "g2", "pmi"])
    o11 = c.o11.values.astype(float)
    r1, c1 = c.w1.map(f1).values.astype(float), c.w2.map(f2).values.astype(float)
    o12, o21 = r1 - o11, c1 - o11
    o22 = total - o11 - o12 - o21
    r2, c2 = total - r1, total - c1
    e11, e12, e21, e22 = r1 * c1 / total, r1 * c2 / total, r2 * c1 / total, r2 * c2 / total
    g2 = 2 * (_xlogx(o11, e11) + _xlogx(o12, e12) + _xlogx(o21, e21) + _xlogx(o22, e22))
    c = c.assign(g2=g2, pmi=np.log2(o11 / e11), atracao=o11 > e11)
    c = c[c.atracao].sort_values("g2", ascending=False).head(n)
    return pd.DataFrame({"colocacao": c.w1 + " " + c.w2, "ocorrencias": c.o11.astype(int).values,
                         "g2": c.g2.values, "pmi": c.pmi.values})


def palavras_chave(tokens: pd.DataFrame, segmentos: pd.Series, n: int = 5) -> pd.DataFrame:
    """Palavras mais características de cada segmento: TF-IDF (Spärck Jones, 1972) com os segmentos como documentos.

    tf = ocorrências do lema no segmento ÷ palavras do segmento; idf = log(segmentos ÷ segmentos onde o lema ocorre).
    Lemas presentes em todos os segmentos têm idf = 0 e nunca são escolhidos."""
    t = tokens[tokens.alfa & ~tokens.stop & tokens.pos.isin(["NOUN", "PROPN", "ADJ", "VERB"])].copy()
    t = t[t.lema.str.len() > 2]
    t["segmento"] = t.frase.map(segmentos)
    t = t.dropna(subset=["segmento"])
    if t.empty:
        return pd.DataFrame(columns=["segmento", "lema", "ocorrencias", "tfidf"])
    k = t.segmento.nunique()
    cont = t.groupby(["segmento", "lema"]).size().rename("ocorrencias").reset_index()
    tamanho = tokens[tokens.alfa].assign(segmento=lambda x: x.frase.map(segmentos)).groupby("segmento").size()
    df = cont.groupby("lema").segmento.nunique()
    cont["tfidf"] = cont.ocorrencias / cont.segmento.map(tamanho) * np.log(k / cont.lema.map(df))
    cont = cont[(cont.tfidf > 0) & (cont.ocorrencias >= 3)]
    cont["tfidf"] *= 1000   # por 1000 palavras, para números legíveis
    top = cont.sort_values(["segmento", "tfidf"], ascending=[True, False]).groupby("segmento").head(n)
    return top.assign(segmento=top.segmento.astype(int)).reset_index(drop=True)


def tempos_verbais(tokens: pd.DataFrame) -> pd.DataFrame:
    """Formas verbais finitas por tempo e modo (traços morfológicos Universal Dependencies)."""
    f = tokens[tokens.pos.isin(["VERB", "AUX"]) & (tokens.forma_verbal == "Fin") & (tokens.tempo != "")]
    if f.empty:
        return pd.DataFrame(columns=["tempo", "modo", "ocorrencias", "pct"])
    t = f.groupby(["tempo", "modo"], observed=True).size().rename("ocorrencias").reset_index()
    t = t[t.ocorrencias > 0]
    t["pct"] = 100 * t.ocorrencias / t.ocorrencias.sum()
    t["tempo"] = t.tempo.astype(str).map(NOMES_TEMPOS).fillna(t.tempo.astype(str))
    t["modo"] = t.modo.astype(str).map(NOMES_MODOS).fillna("não anotado")
    return t.sort_values("ocorrencias", ascending=False).reset_index(drop=True)


NOMES_TEMPOS = {"Pres": "presente", "Past": "passado", "Imp": "imperfeito", "Pqp": "mais-que-perfeito",
                "Fut": "futuro"}
NOMES_MODOS = {"Ind": "indicativo", "Sub": "conjuntivo", "Cnd": "condicional", "Imp": "imperativo", "": "não anotado"}


def segmentos_das_frases(tokens: pd.DataFrame, k: int) -> pd.Series:
    """Segmento (1…k) de cada frase, com segmentos com o mesmo número de palavras (igual a `evolucao`)."""
    palavras = tokens[tokens.alfa].reset_index(drop=True)
    n = len(palavras)
    if not n:
        return pd.Series(dtype=int)
    k = max(1, min(k, n // 50 or 1))
    seg = np.minimum((palavras.index * k) // n, k - 1) + 1
    return pd.Series(seg, index=palavras.frase).groupby(level=0).first()


# ---------------------------------------------------------------------------
# Tabelas auxiliares
# ---------------------------------------------------------------------------

def frequencias(tokens: pd.DataFrame, n: int = 200) -> pd.DataFrame:
    conteudo = tokens[tokens.alfa & ~tokens.stop & tokens.pos.isin(CONTEUDO) & (tokens.lema.str.len() > 2)]
    freq = conteudo.groupby(["lema", "pos"], observed=True).size().rename("ocorrencias").reset_index()
    freq = freq.sort_values(["ocorrencias", "lema"], ascending=[False, True]).head(n)
    freq["por_1000_palavras"] = 1000 * freq.ocorrencias / max(int(tokens.alfa.sum()), 1)
    return freq.reset_index(drop=True)


def classes_gramaticais(tokens: pd.DataFrame) -> pd.DataFrame:
    """Frequências absolutas e por 1000 palavras de cada classe (UPOS)."""
    palavras = tokens[tokens.alfa]
    contagem = palavras.pos.value_counts().reindex(CLASSES).fillna(0).astype(int)
    return pd.DataFrame({"classe": CLASSES, "nome": [NOMES_CLASSES[c] for c in CLASSES],
                         "ocorrencias": contagem.values,
                         "por_1000_palavras": 1000 * contagem.values / max(len(palavras), 1)})


def tabela_entidades(entidades: pd.DataFrame, n: int = 25) -> pd.DataFrame:
    tipo = {r: t for t, rs in ENTIDADES.items() for r in rs}
    sub = entidades[entidades.rotulo.isin(tipo)].assign(tipo=lambda x: x.rotulo.map(tipo))
    sub = sub[sub.entidade.str.len() > 1]
    tabela = sub.groupby(["tipo", "entidade"]).size().rename("ocorrencias").reset_index()
    return (tabela.sort_values(["tipo", "ocorrencias", "entidade"], ascending=[True, False, True])
            .groupby("tipo").head(n).reset_index(drop=True))


def evolucao(tokens: pd.DataFrame, frases: pd.DataFrame, entidades: pd.DataFrame, paragrafos: list[str],
             p=PARAMETROS) -> pd.DataFrame:
    """Indicadores por segmento do livro (segmentos com o mesmo número de palavras)."""
    palavras = tokens[tokens.alfa].reset_index(drop=True)
    n = len(palavras)
    if n == 0:
        return pd.DataFrame()
    k = max(1, min(p.segmentos, n // 50 or 1))
    palavras["segmento"] = np.minimum((palavras.index * k) // n, k - 1) + 1
    seg_frase = palavras.groupby("frase").segmento.first()
    seg_par = palavras.groupby("paragrafo").segmento.first()
    frases = frases.assign(segmento=frases.frase.map(seg_frase)).dropna(subset=["segmento"])
    pessoas = entidades[entidades.rotulo.isin(ENTIDADES["pessoa"])]
    pessoas = pessoas.assign(segmento=pessoas.paragrafo.map(seg_par))
    linhas = []
    for s, g in palavras.groupby("segmento"):
        lista = g.minusc.tolist()
        fs = frases[frases.segmento == s]
        pars = [i for i, v in seg_par.items() if v == s]
        janela = min(p.janela_mattr, len(lista))
        linhas.append({
            "segmento": int(s), "palavras": len(g),
            "mtld": mtld(lista, p.limiar_mtld, p.minimo_fator_mtld) if len(lista) >= p.minimo_mtld else np.nan,
            "mattr": mattr(lista, janela), "janela_mattr": janela,
            "frase_media": fs.palavras[fs.palavras > 0].mean(),
            "densidade_lexical_pct": 100 * g.pos.isin(CONTEUDO).mean(),
            "substantivos_por_1000": 1000 * (g.pos == "NOUN").mean(),
            "verbos_por_1000": 1000 * (g.pos == "VERB").mean(),
            "dialogo_pct": 100 * np.mean([e_dialogo(paragrafos[i]) for i in pars]) if pars else np.nan,
            "pessoas_por_1000": 1000 * (pessoas.segmento == s).sum() / len(g),
            "sentimento": fs.sentimento.mean() if "sentimento" in fs else np.nan,
            "frases_positivas_pct": 100 * (fs.sentimento >= p.sentimento_limiar).sum() / fs.sentimento.notna().sum()
            if "sentimento" in fs and fs.sentimento.notna().any() else np.nan,
            "frases_negativas_pct": 100 * (fs.sentimento <= -p.sentimento_limiar).sum() / fs.sentimento.notna().sum()
            if "sentimento" in fs and fs.sentimento.notna().any() else np.nan,
        })
    return pd.DataFrame(linhas)
