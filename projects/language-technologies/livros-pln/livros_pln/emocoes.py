"""Emoções (modelo de Plutchik) e tonalidade emocional de um livro.

Emoções: léxico NRC Word-Emotion Association (EmoLex, Mohammad e Turney, 2013), com oito emoções
(alegria, tristeza, medo, raiva, aversão, surpresa, confiança e antecipação) e duas polaridades.
Em inglês, as associações foram anotadas por pessoas (crowdsourcing); em português e em francês,
são traduções automáticas do inglês (Google Translate, 2022), por isso os resultados nessas
línguas são EXPERIMENTAIS. O léxico não pode ser redistribuído: é descarregado do sítio oficial
para a pasta `lexicos` (ver `config/pastas.exemplo.toml`) e nunca entra no repositório.

Cada palavra do texto (pelo lema, ou pela forma se o lema não existir no léxico) conta para as
emoções a que está associada, exceto se uma palavra de negação a preceder na mesma frase, até
`emocoes_janela_negacao` palavras antes («não», «ne», «not», …). O léxico mede associações de
palavras, não emoções vividas: não deteta ironia, sarcasmo nem metáforas, e não diz o que o
autor sentiu nem o que o leitor sentirá.

Tonalidade: classificação interpretativa que combina a polaridade por frase do método de
sentimento já usado no projeto (VADER e adaptações) com a distribuição dessa polaridade pelos
capítulos (ou blocos) do livro. Ver `tonalidade()`.
"""
from __future__ import annotations

import csv
import io
import math
import shutil
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from . import configuracao, qualidade
from .configuracao import PARAMETROS

URL = "https://saifmohammad.com/WebDocs/Lexicons/NRC-Emotion-Lexicon.zip"
ZIP = "NRC-Emotion-Lexicon.zip"
EMOCOES = ["alegria", "tristeza", "medo", "raiva", "aversao", "surpresa", "confianca", "antecipacao"]
NOMES = {"alegria": "Alegria", "tristeza": "Tristeza", "medo": "Medo", "raiva": "Raiva", "aversao": "Aversão",
         "surpresa": "Surpresa", "confianca": "Confiança", "antecipacao": "Antecipação"}
_INGLES = {"joy": "alegria", "sadness": "tristeza", "fear": "medo", "anger": "raiva", "disgust": "aversao",
           "surprise": "surpresa", "trust": "confianca", "anticipation": "antecipacao",
           "positive": "positivo", "negative": "negativo"}
_LINGUA_NRC = {"pt": "Portuguese", "fr": "French"}
ORIGEM = {"en": "anotação humana (crowdsourcing), em inglês",
          "pt": "tradução automática do inglês (Google Translate, 2022) — experimental",
          "fr": "tradução automática do inglês (Google Translate, 2022) — experimental"}
NEGADORES = {
    "pt": {"não", "nao", "nunca", "jamais", "nem", "nenhum", "nenhuma", "nada", "sem"},
    "fr": {"ne", "n'", "n’", "pas", "jamais", "aucun", "aucune", "sans", "ni", "point"},
    "en": {"not", "n't", "n’t", "no", "never", "nor", "without", "nothing", "none"},
}
TONS = {
    "positivo": "Predominantemente positivo (feliz)",
    "negativo": "Predominantemente negativo (triste)",
    "neutro": "Tonalidade neutra",
    "misto": "Emocionalmente misto",
    "indeterminado": "Indeterminado",
}
_CACHE: dict = {}


# ---------------------------------------------------------------------------
# Léxico
# ---------------------------------------------------------------------------

def pasta_lexicos() -> Path:
    return configuracao.pasta_lexicos()


def obter(descarregar: bool = True, pasta: Path | None = None) -> Path | None:
    """Caminho do ZIP do EmoLex; descarrega-o do sítio oficial se faltar (e `descarregar`)."""
    pasta = pasta or pasta_lexicos()
    destino = pasta / ZIP
    if destino.exists():
        return destino
    if not descarregar:
        return None
    pasta.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(".parcial")
    try:
        pedido = urllib.request.Request(URL, headers={"User-Agent": "livros-pln (investigação, uso não comercial)"})
        with urllib.request.urlopen(pedido, timeout=120) as r, open(temporario, "wb") as f:
            shutil.copyfileobj(r, f)
        zipfile.ZipFile(temporario).testzip()
        temporario.replace(destino)
        return destino
    except Exception:  # sem rede, sítio indisponível ou ficheiro corrompido
        temporario.unlink(missing_ok=True)
        return None


def ler_lexico(zip_: Path, lingua: str) -> tuple[dict[str, frozenset[str]], dict]:
    """Devolve ({palavra: categorias}, informação). As categorias são as emoções e «positivo»/«negativo»."""
    chave = (str(zip_), lingua)
    if chave in _CACHE:
        return _CACHE[chave]
    lex: dict[str, set[str]] = {}
    multipalavra = 0
    with zipfile.ZipFile(zip_) as z:
        nomes = [n for n in z.namelist() if not n.startswith("__MACOSX")]
        if lingua == "en":
            membro = next(n for n in nomes if n.endswith("Wordlevel-v0.92.txt") or "Wordlevel" in n and n.endswith(".txt"))
            for linha in io.TextIOWrapper(z.open(membro), encoding="utf-8"):
                partes = linha.rstrip("\n").split("\t")
                if len(partes) == 3 and partes[2].strip() == "1" and partes[1] in _INGLES:
                    lex.setdefault(partes[0].lower(), set()).add(_INGLES[partes[1]])
        else:
            nome = _LINGUA_NRC[lingua]
            membro = next(n for n in nomes if n.endswith(f"OneFilePerLanguage/{nome}-NRC-EmoLex.txt"))
            leitor = csv.reader(io.TextIOWrapper(z.open(membro), encoding="utf-8"), delimiter="\t")
            cabecalho = next(leitor)
            col_palavra = next(i for i, c in enumerate(cabecalho) if c.startswith(nome))
            colunas = {i: _INGLES[c.strip().lower()] for i, c in enumerate(cabecalho) if c.strip().lower() in _INGLES}
            for linha in leitor:
                if len(linha) <= col_palavra:
                    continue
                cats = {cat for i, cat in colunas.items() if linha[i].strip() == "1"}
                palavra = linha[col_palavra].strip().lower()
                if not cats or not palavra:
                    continue
                if " " in palavra:  # traduções com mais de uma palavra não se comparam com palavras do texto
                    multipalavra += 1
                    continue
                lex.setdefault(palavra, set()).update(cats)  # traduções repetidas: união das associações
    final = {k: frozenset(v) for k, v in lex.items()}
    info = {"ficheiro": membro.split("/")[-1], "entradas": len(final), "multipalavra_ignoradas": multipalavra,
            "origem": ORIGEM[lingua],
            "versao": "NRC EmoLex v0.92" + (" (traduções de agosto de 2022)" if lingua != "en" else "")}
    _CACHE[chave] = (final, info)
    return final, info


# ---------------------------------------------------------------------------
# Contagem por frase
# ---------------------------------------------------------------------------

def contar(tokens: pd.DataFrame, lex: dict[str, frozenset[str]], lingua: str, janela: int = 3) -> pd.DataFrame:
    """Uma linha por frase: palavras, palavras do léxico, palavras negadas e ocorrências por categoria."""
    cats = EMOCOES + ["positivo", "negativo"]
    neg = NEGADORES.get(lingua, set())
    linhas = {}
    for frase, grupo in tokens.groupby("frase", sort=False):
        conta = dict.fromkeys(cats, 0)
        no_lex = negadas = palavras = 0
        ultimo_neg = -10 ** 6
        for pos, (texto, lema, alfa) in enumerate(zip(grupo.texto.str.lower(), grupo.lema, grupo.alfa)):
            if texto in neg or lema in neg:
                ultimo_neg = pos
                continue
            if not alfa:
                continue
            palavras += 1
            entrada = lex.get(lema) or lex.get(texto)
            if not entrada:
                continue
            no_lex += 1
            if pos - ultimo_neg <= janela:
                negadas += 1
                continue
            for c in entrada:
                conta[c] += 1
        linhas[frase] = {"palavras": palavras, "no_lexico": no_lex, "negadas": negadas, **conta}
    return pd.DataFrame.from_dict(linhas, orient="index").rename_axis("frase")


# ---------------------------------------------------------------------------
# Discurso direto
# ---------------------------------------------------------------------------

_ABRE = {"«": "»", "“": "”", "„": "“"}


def _dentro_de_aspas(paragrafo: str) -> list[bool]:
    """Para cada carácter do parágrafo, se está dentro de aspas: « », “ ”, " " e aspas simples (‘ ’ ou ')
    quando abrem antes de uma letra e fecham depois de uma letra ou pontuação (os apóstrofos entre letras,
    como em «don't», são ignorados)."""
    dentro, fecho, retas, simples = [], None, False, False
    n = len(paragrafo)
    for i, c in enumerate(paragrafo):
        ant = paragrafo[i - 1] if i else " "
        seg = paragrafo[i + 1] if i + 1 < n else " "
        if fecho is None and c in _ABRE:
            fecho = _ABRE[c]
            dentro.append(True)
            continue
        if fecho is not None and c == fecho:
            fecho = None
            dentro.append(True)
            continue
        if c == '"':
            retas = not retas
            dentro.append(True)
            continue
        if c in "'‘’":
            if not simples and (ant.isspace() or ant in "(—–-") and seg.isalpha():
                simples = True
                dentro.append(True)
                continue
            if simples and not seg.isalpha() and (ant.isalpha() or ant in ",.!?;:—–-"):
                simples = False
                dentro.append(True)
                continue
        dentro.append(fecho is not None or retas or simples)
    return dentro


def discurso_direto(frases: pd.DataFrame, paragrafos: list[str], limiar: float = 0.5) -> pd.Series:
    """Heurística tipográfica, por frase: discurso direto se pelo menos metade dos caracteres da frase está
    entre aspas, ou se a frase pertence a um parágrafo que abre com travessão (convenção do diálogo em
    português e francês)."""
    mascaras: dict[int, list[bool]] = {}
    posicao: dict[int, int] = {}
    resultado = []
    for par, texto in zip(frases.paragrafo, frases.texto):
        p = paragrafos[par] if 0 <= par < len(paragrafos) else ""
        if p.lstrip().startswith(("—", "–", "-")):
            resultado.append(True)
            continue
        if par not in mascaras:
            mascaras[par], posicao[par] = _dentro_de_aspas(p), 0
        t = texto.strip()
        i = p.find(t, posicao[par]) if t else -1
        if i < 0:
            resultado.append(False)
            continue
        posicao[par] = i + len(t)
        m = mascaras[par][i:i + len(t)]
        resultado.append(bool(m) and sum(m) / len(m) >= limiar)
    return pd.Series(resultado, index=frases.index)


# ---------------------------------------------------------------------------
# Tonalidade
# ---------------------------------------------------------------------------

def _bootstrap(valores: np.ndarray, n: int, semente: int = 20261106) -> tuple[float, float]:
    rng = np.random.default_rng(semente)
    medias = rng.choice(valores, size=(n, len(valores)), replace=True).mean(axis=1)
    a, b = np.percentile(medias, [2.5, 97.5])
    return float(a), float(b)


def tonalidade(sentimento: pd.Series, segmento: pd.Series, cobertura: float | None, p=PARAMETROS) -> dict:
    """Classificação interpretativa da tonalidade de um livro.

    `sentimento`: pontuação «compound» por frase (NaN nas frases não pontuadas);
    `segmento`: capítulo ou bloco de cada frase; `cobertura`: % das palavras no léxico de sentimento.

    Regras (limiares em `config/parametros.toml`):
      1. indeterminado se houver poucas frases pontuadas, poucos segmentos ou cobertura baixa;
      2. calcula-se a média da polaridade por segmento e o intervalo de confiança a 95 % da média
         desses segmentos (bootstrap por segmentos, que respeita a dependência entre frases vizinhas);
      3. positivo (negativo) se o intervalo inteiro está acima de +limiar (abaixo de −limiar);
      4. misto se não for positivo nem negativo e houver pelo menos `tom_minimo_forte_pct` % de
         frases fortemente positivas E fortemente negativas (|compound| ≥ `tom_forte`);
      5. neutro se o intervalo inteiro está entre −limiar e +limiar;
      6. indeterminado nos restantes casos (o intervalo atravessa o limiar).
    """
    s = sentimento.dropna()
    base = {"tom": "indeterminado", "rotulo": TONS["indeterminado"], "media": None, "ic": [None, None],
            "segmentos": None, "fortes_positivas_pct": None, "fortes_negativas_pct": None,
            "intensidade": None, "variabilidade": None, "razoes": []}
    if len(s) < p.tom_minimo_frases:
        base["razoes"].append(f"só {len(s)} frases pontuadas (mínimo: {p.tom_minimo_frases})")
        return base
    if cobertura is not None and cobertura < p.tom_cobertura_minima:
        base["razoes"].append(f"o léxico de sentimento cobre só {cobertura:.1f} % das palavras "
                              f"(mínimo: {p.tom_cobertura_minima:.0f} %)")
        return base
    medias = sentimento.groupby(segmento).mean().dropna()
    if len(medias) < 5:
        base["razoes"].append(f"só {len(medias)} segmentos com frases pontuadas (mínimo: 5)")
        return base
    a, b = _bootstrap(medias.to_numpy(), p.tom_bootstrap)
    lim, forte = p.tom_limiar, p.tom_forte
    fp, fn = 100 * float((s >= forte).mean()), 100 * float((s <= -forte).mean())
    base.update(media=float(medias.mean()), ic=[a, b], segmentos=int(len(medias)), fortes_positivas_pct=fp,
                fortes_negativas_pct=fn, intensidade=float(s.abs().mean()), variabilidade=float(medias.std(ddof=1)))
    ic = f"intervalo de confiança a 95 % da polaridade média dos {len(medias)} segmentos: [{_n(a)}; {_n(b)}]"
    fortes = f"{_n(fp, 1)} % de frases fortemente positivas e {_n(fn, 1)} % fortemente negativas (|polaridade| ≥ {_n(forte, 1)})"
    if a > lim:
        tom, razao = "positivo", f"{ic}, inteiramente acima de +{_n(lim)}"
    elif b < -lim:
        tom, razao = "negativo", f"{ic}, inteiramente abaixo de −{_n(lim)}"
    elif fp >= p.tom_minimo_forte_pct and fn >= p.tom_minimo_forte_pct:
        tom, razao = "misto", f"{fortes}: ambas acima de {_n(p.tom_minimo_forte_pct, 0)} %; {ic}"
    elif a >= -lim and b <= lim:
        tom, razao = "neutro", f"{ic}, inteiramente entre −{_n(lim)} e +{_n(lim)}; {fortes}"
    else:
        tom, razao = "indeterminado", f"{ic}, que atravessa o limiar de ±{_n(lim)}; {fortes}"
    base.update(tom=tom, rotulo=TONS[tom])
    base["razoes"].append(razao)
    return base


def _n(v: float, casas: int = 3) -> str:
    return f"{v:.{casas}f}".replace(".", ",").replace("-", "−")


# ---------------------------------------------------------------------------
# Análise completa
# ---------------------------------------------------------------------------

def _entropia(contagens: np.ndarray) -> float:
    total = contagens.sum()
    if total <= 0:
        return float("nan")
    q = contagens[contagens > 0] / total
    return float(-(q * np.log(q)).sum() / math.log(len(contagens)))


def _vazio(estado: str, motivo: str) -> dict:
    return {"estado": estado, "motivo": motivo, "metodo": None, "indicadores": {}, "segmentos": pd.DataFrame(),
            "canais": pd.DataFrame(), "lexico": None, "emocao_dominante": None, "mudancas": [],
            "fases": pd.DataFrame(), "presenca": {}, "por_frase": pd.DataFrame()}


def analisar(tokens: pd.DataFrame, frases: pd.DataFrame, paragrafos: list[str], segmento_par: list[int],
             rotulos: list[str], lingua: str, p=PARAMETROS, zip_: Path | None = None) -> dict:
    """Emoções por frase, por segmento (capítulo ou bloco), por canal (narração ou discurso direto) e no livro."""
    if lingua not in ("pt", "fr", "en"):
        return _vazio(qualidade.NAO_APLICAVEL, f"sem léxico de emoções para a língua «{lingua}»")
    zip_ = zip_ or obter()
    if zip_ is None:
        return _vazio(qualidade.DESCONHECIDO, "o léxico NRC EmoLex não está disponível (sem ligação ao sítio oficial); "
                                              "corra «python -m livros_pln lexicos»")
    try:
        lex, info = ler_lexico(zip_, lingua)
    except (KeyError, StopIteration, zipfile.BadZipFile) as e:
        return _vazio(qualidade.FALHA, f"não foi possível ler o léxico NRC EmoLex ({type(e).__name__})")

    por_frase = contar(tokens, lex, lingua, p.emocoes_janela_negacao)
    por_frase = por_frase.join(frases.set_index("frase")[["paragrafo"]], how="left")
    por_frase["segmento"] = por_frase.paragrafo.map(lambda i: segmento_par[i] if 0 <= i < len(segmento_par) else 0)
    direto = pd.Series(discurso_direto(frases, paragrafos).to_numpy(), index=frases.frase.to_numpy())
    por_frase["direto"] = direto.reindex(por_frase.index).fillna(False).astype(bool)
    palavras = int(por_frase.palavras.sum())
    if palavras < p.minimo_texto:
        return _vazio(qualidade.NAO_APLICAVEL, f"texto demasiado curto ({palavras} palavras)")
    tot = por_frase[EMOCOES].sum()
    emocionais = int(tot.sum())
    ind = {f"emocao_{e}_por_1000": 1000 * tot[e] / palavras for e in EMOCOES}
    presenca = {e: 100 * float((por_frase[e] > 0).mean()) for e in EMOCOES}  # % de frases com a emoção
    ind["emocoes_cobertura_pct"] = 100 * por_frase.no_lexico.sum() / palavras
    ind["emocoes_intensidade_por_1000"] = 1000 * emocionais / palavras
    ind["emocoes_entropia"] = _entropia(tot.to_numpy(dtype=float))
    ind["emocoes_negadas_pct"] = 100 * por_frase.negadas.sum() / max(1, por_frase.no_lexico.sum())
    elegiveis = por_frase[por_frase.palavras >= p.sentimento_minimo_palavras]
    ind["frases_ambivalentes_pct"] = 100 * float(((elegiveis.positivo > 0) & (elegiveis.negativo > 0)).mean()) \
        if len(elegiveis) else float("nan")
    ind["alegria_tristeza_razao"] = tot["alegria"] / tot["tristeza"] if tot["tristeza"] else float("nan")
    dominante = tot.idxmax() if emocionais else None
    # convergência entre os dois léxicos (não é validação): correlação de Spearman, por frase, entre a polaridade do
    # método de sentimento e a polaridade NRC ((positivo − negativo) ÷ (positivo + negativo)), nas frases com ambas
    if "sentimento" in frases:
        sent_f = frases.set_index("frase").sentimento.reindex(por_frase.index)
        soma = por_frase.positivo + por_frase.negativo
        ok = sent_f.notna() & (soma > 0)
        ind["concordancia_lexicos"] = float(sent_f[ok].corr(((por_frase.positivo - por_frase.negativo) / soma)[ok],
                                                            method="spearman")) if ok.sum() >= 30 else float("nan")

    # por segmento
    seg = por_frase.groupby("segmento").agg(palavras=("palavras", "sum"), **{e: (e, "sum") for e in EMOCOES})
    for e in EMOCOES:
        seg[e] = 1000 * seg[e] / seg.palavras.replace(0, np.nan)
    seg["dominante"] = seg[EMOCOES].idxmax(axis=1).where(seg[EMOCOES].sum(axis=1) > 0)
    sent = frases.set_index("frase").sentimento if "sentimento" in frases else pd.Series(dtype=float)
    seg["polaridade"] = sent.reindex(por_frase.index).groupby(por_frase.segmento).mean()
    seg = seg[seg.index > 0]
    seg.insert(0, "rotulo", [rotulos[i - 1] if 0 < i <= len(rotulos) else str(i) for i in seg.index])
    # mudanças expressivas: diferenças entre segmentos consecutivos acima de 2 desvios-padrão das diferenças
    mudancas = []
    if len(seg) >= 4 and seg.polaridade.notna().sum() >= 4:
        dif = seg.polaridade.diff().dropna()
        corte = 2 * dif.std(ddof=1)
        for i, d in dif.items():
            if corte > 0 and abs(d) >= corte:
                mudancas.append({"segmento": int(i), "rotulo": seg.loc[i, "rotulo"], "variacao": float(d)})
    # início (20 % das palavras), desenvolvimento (60 %) e conclusão (20 %)
    acum = por_frase.palavras.cumsum() / max(1, palavras)
    fase = pd.cut(acum, [-0.01, 0.2, 0.8, 1.01], labels=["início", "desenvolvimento", "conclusão"])
    fases = por_frase.groupby(fase, observed=False).agg(palavras=("palavras", "sum"), **{e: (e, "sum") for e in EMOCOES})
    for e in EMOCOES:
        fases[e] = 1000 * fases[e] / fases.palavras.replace(0, np.nan)
    fases["polaridade"] = sent.reindex(por_frase.index).groupby(fase, observed=False).mean()

    # canais: narração e discurso direto
    canais = por_frase.groupby(por_frase.direto.map({True: "discurso direto", False: "narração"})).agg(
        frases=("palavras", "size"), palavras=("palavras", "sum"), **{e: (e, "sum") for e in EMOCOES})
    for e in EMOCOES:
        canais[e] = 1000 * canais[e] / canais.palavras.replace(0, np.nan)
    canais["polaridade"] = sent.reindex(por_frase.index).groupby(por_frase.direto.map(
        {True: "discurso direto", False: "narração"})).mean()
    ind["discurso_direto_frases_pct"] = 100 * float(por_frase.direto.mean())

    metodo = f"NRC EmoLex v0.92 ({info['origem']})"
    return {"estado": "valido", "motivo": None, "metodo": metodo, "indicadores": ind, "segmentos": seg,
            "fases": fases, "canais": canais, "lexico": info, "emocao_dominante": dominante, "mudancas": mudancas,
            "presenca": presenca, "por_frase": por_frase}
