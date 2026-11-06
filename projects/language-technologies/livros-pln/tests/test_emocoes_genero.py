"""Capítulos, emoções (léxico NRC), tonalidade e género literário inferido."""
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from livros_pln import capitulos, emocoes, genero
from livros_pln.configuracao import Parametros

P = Parametros()


# --- capítulos -------------------------------------------------------------------------------------------------------

def _texto(n_caps=4, titulo="Capítulo {}", palavras=400):
    pars = []
    for k in range(1, n_caps + 1):
        pars.append(titulo.format(k))
        pars += [" ".join(["palavra"] * (palavras // 4))] * 4
    return pars


def test_capitulos_pelos_titulos():
    d = capitulos.dividir(_texto(5))
    assert d.metodo == "capítulos" and d.n == 5 and d.rotulos[0] == "Capítulo 1"


def test_capitulos_junta_blocos_curtos_e_partes():
    pars = ["PREMIÈRE PARTIE", "I"] + ["mot " * 100] * 4 + ["II"] + ["mot " * 100] * 4 + ["DEUXIÈME PARTIE", "I"] + \
           ["mot " * 100] * 4
    d = capitulos.dividir(pars)
    assert d.metodo == "capítulos" and d.n == 3
    assert d.rotulos[0] == "PREMIÈRE PARTIE · I" and d.rotulos[2] == "DEUXIÈME PARTIE · I"


def test_sem_titulos_usa_blocos_iguais():
    d = capitulos.dividir(["texto corrido " * 60] * 40, blocos=10)
    assert d.metodo == "blocos" and d.n == 10 and d.segmento[0] == 1 and d.segmento[-1] == 10


# --- léxico ----------------------------------------------------------------------------------------------------------

def _zip(tmp_path: Path) -> Path:
    z = tmp_path / emocoes.ZIP
    cab = "English Word\tanger\tanticipation\tdisgust\tfear\tjoy\tnegative\tpositive\tsadness\tsurprise\ttrust\t{} Word\n"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("NRC-Emotion-Lexicon/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt",
                   "happy\tjoy\t1\nhappy\tpositive\t1\nhappy\tsadness\t0\nsad\tsadness\t1\nsad\tnegative\t1\n")
        f.writestr("NRC-Emotion-Lexicon/OneFilePerLanguage/Portuguese-NRC-EmoLex.txt",
                   cab.format("Portuguese") + "happy\t0\t0\t0\t0\t1\t0\t1\t0\t0\t0\tfeliz\n"
                   "glad\t0\t1\t0\t0\t1\t0\t1\t0\t0\t0\tfeliz\n"
                   "sad\t0\t0\t0\t0\t0\t1\t0\t1\t0\t0\ttriste\n"
                   "grief\t0\t0\t0\t0\t0\t1\t0\t1\t0\t0\tdor de alma\n"
                   "table\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\tmesa\n")
        f.writestr("__MACOSX/NRC-Emotion-Lexicon/._lixo", "x")
    return z


def test_ler_lexico_ingles_e_traduzido(tmp_path):
    z = _zip(tmp_path)
    en, info = emocoes.ler_lexico(z, "en")
    assert en["happy"] == {"alegria", "positivo"} and "anotação humana" in info["origem"]
    pt, info = emocoes.ler_lexico(z, "pt")
    assert pt["feliz"] == {"alegria", "antecipacao", "positivo"}       # traduções repetidas: união
    assert "mesa" not in pt                                            # sem associações
    assert info["multipalavra_ignoradas"] == 1 and "experimental" in info["origem"]


def _tokens(frases: list[list[str]]):
    linhas = []
    for f, palavras in enumerate(frases):
        for w in palavras:
            linhas.append({"frase": f, "texto": w, "lema": w.lower(), "alfa": w.isalpha()})
    return pd.DataFrame(linhas)


def test_contagem_com_negacao():
    lex = {"feliz": frozenset({"alegria", "positivo"}), "triste": frozenset({"tristeza", "negativo"})}
    t = _tokens([["Ele", "está", "feliz"], ["Ele", "não", "está", "feliz"], ["triste", "e", "feliz"]])
    c = emocoes.contar(t, lex, "pt", janela=3)
    assert c.loc[0, "alegria"] == 1 and c.loc[1, "alegria"] == 0 and c.loc[1, "negadas"] == 1
    assert c.loc[2, "positivo"] == 1 and c.loc[2, "negativo"] == 1


def test_discurso_direto():
    pars = ["— Bom dia, disse ele.", "Il m’a dit : « Je viens demain. » Puis il est parti.",
            "'I don't know,' said Alice."]
    frases = pd.DataFrame({"frase": [0, 1, 2, 3], "paragrafo": [0, 1, 1, 2],
                           "texto": ["— Bom dia, disse ele.", "Il m’a dit : « Je viens demain. »", "Puis il est parti.",
                                     "'I don't know,' said Alice."]})
    assert emocoes.discurso_direto(frases, pars).tolist() == [True, True, False, True]


# --- tonalidade ------------------------------------------------------------------------------------------------------

def _tom(valores, segmentos=10, cobertura=10.0):
    s = pd.Series(valores, dtype=float)
    seg = pd.Series(np.arange(len(s)) * segmentos // len(s) + 1)
    return emocoes.tonalidade(s, seg, cobertura, P)


def test_tonalidade_positiva_negativa_neutra_mista():
    rng = np.random.default_rng(1)
    assert _tom(rng.normal(0.25, 0.1, 600))["tom"] == "positivo"
    assert _tom(rng.normal(-0.25, 0.1, 600))["tom"] == "negativo"
    assert _tom(rng.normal(0.0, 0.05, 600))["tom"] == "neutro"
    misto = np.r_[np.full(150, 0.8), np.full(150, -0.8), np.zeros(300)]
    rng.shuffle(misto)
    t = _tom(misto)
    assert t["tom"] == "misto" and t["fortes_positivas_pct"] >= 10 and t["fortes_negativas_pct"] >= 10


def test_tonalidade_indeterminada_sem_dados_suficientes():
    assert _tom(np.full(50, 0.5))["tom"] == "indeterminado"                       # poucas frases
    t = _tom(np.full(600, 0.5), cobertura=1.0)
    assert t["tom"] == "indeterminado" and "cobre só" in t["razoes"][0]          # cobertura baixa
    assert t["media"] is None                                                     # nada inventado


def test_tonalidade_reprodutivel():
    rng = np.random.default_rng(2)
    v = rng.normal(0.03, 0.2, 800)
    assert _tom(v)["ic"] == _tom(v)["ic"]


def test_analisar_sem_lexico_fica_desconhecido(monkeypatch):
    monkeypatch.setattr(emocoes, "obter", lambda *a, **k: None)
    r = emocoes.analisar(pd.DataFrame(), pd.DataFrame(), [], [], [], "pt")
    assert r["estado"] == "desconhecido" and r["indicadores"] == {}


# --- género ----------------------------------------------------------------------------------------------------------

def _ind(palavras, pers=12, dd=30.0):
    return {"palavras": palavras, "personagens_na_rede": pers, "discurso_direto_frases_pct": dd}


def test_genero_por_forma_e_extensao():
    pars = ["Um parágrafo de prosa com várias palavras para o teste."] * 20
    seg = [1] * 20
    narr = {"1": 2.0, "3": 40.0}
    assert genero.inferir(_ind(60000), "prosa", pars, seg, narr)["principal"] == "Romance"
    assert genero.inferir(_ind(30000), "prosa", pars, seg, narr)["principal"] == "Novela"
    assert genero.inferir(_ind(5000), "prosa", pars, seg, narr)["principal"] == "Conto"
    assert genero.inferir(_ind(50000), "verso", pars, seg, narr)["principal"] == "Epopeia"
    lirica = genero.inferir(_ind(3000, pers=1), "verso", pars, seg, {"1": 45.0, "3": 10.0})
    assert lirica["principal"] == "Poesia lírica"


def test_genero_teatro_e_comparacao_bibliografica():
    pars = ["HAMLET. Ser ou não ser.", "OFÉLIA. Meu senhor.", "HAMLET: Vai.", "Texto de cena."]
    t = genero.inferir(_ind(20000), "prosa", pars, [1, 1, 1, 1], {"1": 5.0, "3": 5.0})
    assert t["forma_principal"] == "Teatro" and t["principal"] is None      # teatro: sem género narrativo
    prosa = ["Um parágrafo de prosa com várias palavras para o teste."] * 20
    bib = {"genero": "Epopeia (tradução em prosa)", "chave": "epopeia", "fonte": "teste", "estado": "proposto"}
    g = genero.inferir(_ind(60000), "prosa", prosa, [1] * 20, {"1": 2.0, "3": 40.0}, bib)
    assert g["principal"] == "Romance" and g["bibliografico"]["concorda"] is False and g["bibliografico"]["nota"]
    # o género bibliográfico nunca muda a inferência
    sem = genero.inferir(_ind(60000), "prosa", prosa, [1] * 20, {"1": 2.0, "3": 40.0})
    assert [c["pontuacao"] for c in sem["generos"]] == [c["pontuacao"] for c in g["generos"]]


def test_pontuacao_zero_quando_falha_criterio_essencial():
    g = genero.inferir(_ind(60000), "prosa", ["Texto."] * 5, [1] * 5, {"1": 1.0, "3": 30.0})
    epopeia = next(c for c in g["generos"] if c["chave"] == "epopeia")
    assert epopeia["pontuacao"] == 0.0
