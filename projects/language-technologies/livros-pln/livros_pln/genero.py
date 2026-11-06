"""Perfil de género literário inferido pelo conteúdo: regras transparentes, em dois níveis (forma e género).

Com um corpus de poucos livros não há dados para treinar nem validar um classificador supervisionado,
por isso a inferência usa regras explícitas sobre indicadores já calculados. Cada categoria recebe
uma PONTUAÇÃO DE REGRAS (fração dos critérios cumpridos, de 0 a 1), que não é uma probabilidade
nem um grau de confiança calibrado. Uma obra pode ter mais de uma categoria.

Os limiares de extensão de romance, novela e conto seguem a convenção das regras dos prémios Nebula
(SFWA): conto < 7500 palavras; novela curta («novelette») 7500–17 500; novela 17 500–40 000;
romance ≥ 40 000. É uma convenção editorial, não uma definição literária.

O género bibliográfico (de `metadados.csv`) nunca entra no cálculo: serve só para comparar.
Temas e subgéneros (histórico, religioso, de viagem…), memórias, autobiografia e o teatro trágico ou
cómico não são inferidos nesta versão.
"""
from __future__ import annotations

import re

import pandas as pd

FORMAS = {"prosa": "Prosa narrativa", "verso": "Verso", "teatro": "Teatro", "epistolar": "Narrativa epistolar"}
GENEROS = {"romance": "Romance", "novela": "Novela", "conto": "Conto", "epopeia": "Epopeia",
           "poesia_lirica": "Poesia lírica", "ensaio": "Ensaio"}
NAO_INFERIDOS = ["Tragédia", "Comédia", "Drama", "Autobiografia", "Biografia", "Memórias", "Literatura de viagem",
                 "Literatura histórica", "Literatura filosófica", "Literatura religiosa"]
# chaves aceites na coluna genero_chave de metadados.csv (comparação com a inferência)
CHAVES_BIBLIOGRAFICAS = set(GENEROS) | {"narrativa", "poesia", "teatro"}

_FALANTE = re.compile(r"^[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ'’ .-]{1,30}[.:](\s|$)")
_SAUDACAO = re.compile(r"^(meu caro|minha cara|caro|cara|querid[oa]|ex\.?mo|senhor|senhora|mon cher|ma chère|"
                       r"cher|chère|monsieur|madame|dear|my dear|sir|madam)\b[^.!?]{0,40}[,!:]", re.I)


def teatro_pct(paragrafos: list[str]) -> float:
    """% de parágrafos que abrem com o nome de uma personagem em maiúsculas seguido de ponto ou dois pontos."""
    validos = [p for p in paragrafos if p.strip()]
    return 100 * sum(bool(_FALANTE.match(p.strip())) for p in validos) / len(validos) if validos else float("nan")


def cartas_pct(paragrafos: list[str], segmento: list[int]) -> float:
    """% de capítulos (ou blocos) cujo primeiro parágrafo de texto abre com uma fórmula de saudação."""
    primeiros: dict[int, str] = {}
    for p, s in zip(paragrafos, segmento):
        if s not in primeiros and len(p.split()) > 10:
            primeiros[s] = p.strip()
    return 100 * sum(bool(_SAUDACAO.match(t)) for t in primeiros.values()) / len(primeiros) if primeiros else float("nan")


def pronomes_na_narracao(tokens: pd.DataFrame, direto: pd.Series) -> dict[str, float]:
    """Pronomes pessoais de 1.ª e 3.ª pessoa por 1000 palavras, só nas frases de narração (fora do discurso direto)."""
    narr = tokens[~tokens.frase.map(direto).fillna(False).astype(bool)]
    palavras = int(narr.alfa.sum())
    if not palavras:
        return {"1": float("nan"), "3": float("nan")}
    pess = narr[narr.pronome_pessoal]
    return {k: 1000 * int((pess.pessoa == k).sum()) / palavras for k in ("1", "3")}


PRIMEIRA_PESSOA = 30.0  # pronomes de 1.ª pessoa por 1000 palavras na narração a partir dos quais a narração é na 1.ª pessoa


def _criterio(texto: str, ok: bool | None, essencial: bool = False) -> dict:
    return {"criterio": texto, "cumprido": None if ok is None else bool(ok), "essencial": essencial}


def _pontuar(criterios: list[dict]) -> float | None:
    """Fração dos critérios cumpridos; 0 se falhar um critério essencial (forma ou extensão)."""
    if any(c["essencial"] and c["cumprido"] is False for c in criterios):
        return 0.0
    avaliados = [c for c in criterios if c["cumprido"] is not None]
    return sum(c["cumprido"] for c in avaliados) / len(avaliados) if avaliados else None


def _f(v, casas=1) -> str:
    return "—" if v is None or v != v else f"{v:,.{casas}f}".replace(",", " ").replace(".", ",")


def inferir(ind: dict, forma_texto: str, paragrafos: list[str], segmento: list[int], narr: dict[str, float],
            bibliografico: dict | None = None) -> dict:
    """Devolve o perfil de género: formas e géneros com pontuação e critérios, principal, alternativas e
    comparação com o género bibliográfico (se existir)."""
    palavras = ind.get("palavras") or 0
    teatro = teatro_pct(paragrafos)
    cartas = cartas_pct(paragrafos, segmento)
    pers = ind.get("personagens_na_rede")
    dd = ind.get("discurso_direto_frases_pct")
    p1, p3 = narr.get("1"), narr.get("3")
    primeira = None if p1 is None or p1 != p1 else p1 >= PRIMEIRA_PESSOA
    verso = forma_texto == "verso"

    formas = {
        "prosa": [_criterio("texto em prosa (deteção pela extensão das linhas)", not verso),
                  _criterio(f"poucos parágrafos com nome de personagem antes da fala ({_f(teatro)} % < 20 %)",
                            teatro < 20 if teatro == teatro else None)],
        "verso": [_criterio("texto em verso (deteção pela extensão das linhas)", verso)],
        "teatro": [_criterio(f"parágrafos que abrem com o nome de uma personagem ({_f(teatro)} % ≥ 20 %)",
                             teatro >= 20 if teatro == teatro else None)],
        "epistolar": [_criterio(f"capítulos que abrem com uma saudação de carta ({_f(cartas)} % ≥ 50 %)",
                                cartas >= 50 if cartas == cartas else None)],
    }
    narrativa = not verso and teatro < 20
    tam = f"{_f(palavras, 0)} palavras"
    um = f"{_f(p1)} pronomes de 1.ª pessoa por 1000 palavras na narração"
    generos = {
        "romance": [_criterio("prosa narrativa", narrativa, True),
                    _criterio(f"{tam} ≥ 40 000 (convenção SFWA)", palavras >= 40000, True)],
        "novela": [_criterio("prosa narrativa", narrativa, True),
                   _criterio(f"{tam} entre 17 500 e 40 000 (convenção SFWA)", 17500 <= palavras < 40000, True)],
        "conto": [_criterio("prosa narrativa", narrativa, True),
                  _criterio(f"{tam} < 17 500 (convenção SFWA)", palavras < 17500, True)],
        "epopeia": [_criterio("verso", verso, True), _criterio(f"poema longo ({tam} ≥ 10 000)", palavras >= 10000, True),
                    _criterio(f"narração na 3.ª pessoa ({um} < {_f(PRIMEIRA_PESSOA, 0)})",
                              None if primeira is None else not primeira),
                    _criterio(f"muitas personagens ({_f(pers, 0)} ≥ 10 na rede)", None if pers is None else pers >= 10)],
        "poesia_lirica": [_criterio("verso", verso, True),
                          _criterio(f"poema curto ou coletânea ({tam} < 10 000)", palavras < 10000, True),
                          _criterio(f"primeira pessoa predominante ({um} ≥ {_f(PRIMEIRA_PESSOA, 0)})", primeira)],
        "ensaio": [_criterio("prosa", not verso, True),
                   _criterio(f"pouco discurso direto ({_f(dd)} % < 5 %)", None if dd is None else dd < 5),
                   _criterio(f"poucas personagens ({_f(pers, 0)} < 5 na rede)", None if pers is None else pers < 5)],
    }
    forma_res = sorted(({"chave": k, "nome": FORMAS[k], "pontuacao": _pontuar(c), "criterios": c}
                        for k, c in formas.items()), key=lambda x: -(x["pontuacao"] or 0))
    gen_res = sorted(({"chave": k, "nome": GENEROS[k], "pontuacao": _pontuar(c), "criterios": c}
                      for k, c in generos.items()), key=lambda x: -(x["pontuacao"] or 0))
    principal = gen_res[0] if gen_res[0]["pontuacao"] == 1 else None
    alternativas = [g["nome"] for g in gen_res if g is not principal and (g["pontuacao"] or 0) >= 0.5]
    tracos = []
    if primeira:
        tracos.append(f"Narração na 1.ª pessoa ({um}): compatível com romance na 1.ª pessoa, memórias ou "
                      "autobiografia, que o conteúdo sozinho não distingue.")
    if dd is not None and dd >= 25:
        tracos.append(f"Muito discurso direto ({_f(dd)} % das frases).")
    comparacao = None
    if bibliografico and bibliografico.get("genero"):
        chave = bibliografico.get("chave")
        inferido = principal["chave"] if principal else None
        if chave and inferido:
            concorda = chave == inferido or (chave == "narrativa" and inferido in ("romance", "novela", "conto"))
        else:
            concorda = None
        nota = None
        if concorda is False:
            nota = ("A inferência avalia o texto analisado (a forma desta edição e a sua extensão); o género "
                    "bibliográfico refere-se à obra. Uma tradução em prosa de um poema, ou uma obra mais curta do que "
                    "a convenção de extensão, produzem esta divergência sem que nenhuma das duas esteja errada.")
        comparacao = {"genero": bibliografico["genero"], "fonte": bibliografico.get("fonte"),
                      "estado": bibliografico.get("estado") or "proposto", "concorda": concorda, "nota": nota}
    return {"metodo": "regras transparentes (exploratório, sem validação estatística)",
            "formas": forma_res, "generos": gen_res,
            "forma_principal": forma_res[0]["nome"] if forma_res[0]["pontuacao"] == 1 else None,
            "principal": principal["nome"] if principal else None, "alternativas": alternativas,
            "tracos": tracos, "nao_inferidos": NAO_INFERIDOS, "bibliografico": comparacao,
            "medidas": {"teatro_pct": teatro, "cartas_pct": cartas, "pronomes_1a_narracao_por_1000": p1,
                        "pronomes_3a_narracao_por_1000": p3}}
