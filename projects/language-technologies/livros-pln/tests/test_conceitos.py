"""Legibilidade (faixas por língua), sentimento e os novos conceitos de PLN."""
import math
import random
from collections import Counter

import numpy as np
import pandas as pd
import pytest

from livros_pln import indicadores, qualidade, sentimento


# --- Legibilidade -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("indice, lingua, escala, leitura", [
    (80, "pt", "muito fácil", "fácil"), (64, "pt", "fácil", "fácil"), (50, "pt", "fácil", "fácil"),
    (40, "pt", "razoavelmente difícil", "difícil"), (10, "pt", "muito difícil", "difícil"),
    (65, "en", "padrão", "fácil"), (55, "en", "razoavelmente difícil", "difícil"), (95, "fr", "muito fácil", "fácil"),
])
def test_faixas_de_legibilidade(indice, lingua, escala, leitura):
    assert indicadores.escala_legibilidade(indice, lingua) == escala
    assert indicadores.leitura(indice, lingua) == leitura


def test_nivel_escolar_so_em_portugues():
    assert indicadores.nivel_escolar(64, "pt") == "5.º ao 8.º ano de escolaridade"
    assert indicadores.nivel_escolar(64, "en") is None
    assert indicadores.leitura(float("nan"), "pt") is None


# --- Tipos de frase -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("texto, tipo", [
    ("Onde estás?", "interrogativa"), ("— Onde estás? —", "interrogativa"), ("«Que horror!»", "exclamativa"),
    ("Saiu cedo.", "declarativa"), ("E depois…", "declarativa"), ('"Really?!"', "interrogativa"),
])
def test_tipo_de_frase(texto, tipo):
    assert indicadores.tipo_frase(texto) == tipo


# --- Zipf e Heaps -------------------------------------------------------------------------------------------------

def test_zipf_recupera_o_expoente_de_dados_sinteticos():
    # frequências exatamente proporcionais a 1/r: o expoente ajustado deve ser ≈ 1
    contagem = Counter({f"p{r}": int(round(10000 / r)) for r in range(1, 400)})
    z = indicadores.zipf(contagem, frequencia_minima=5)
    assert z["zipf_expoente"] == pytest.approx(1.0, abs=0.02)
    assert z["zipf_r2"] > 0.99


def test_heaps_vocabulario_que_nunca_se_repete_tem_beta_1():
    h = indicadores.heaps([f"p{i}" for i in range(5000)])
    assert h["heaps_beta"] == pytest.approx(1.0, abs=1e-6)


def test_heaps_vocabulario_finito_tem_beta_menor_que_1():
    rnd = random.Random(3)
    palavras = rnd.choices([f"p{i}" for i in range(2000)], weights=[1 / (i + 1) for i in range(2000)], k=20000)
    assert 0.2 < indicadores.heaps(palavras)["heaps_beta"] < 0.95


def test_zipf_e_heaps_texto_curto_nao_aplicavel():
    assert math.isnan(indicadores.zipf(Counter("abc"))["zipf_expoente"])
    assert math.isnan(indicadores.heaps(["a", "b"])["heaps_beta"])


# --- Colocações e palavras-chave --------------------------------------------------------------------------------

def _tokens(frases: list[list[str]], stop=frozenset({"o", "a", "de", "e"})):
    linhas = [(f, w, w, w in stop) for f, frase in enumerate(frases) for w in frase]
    t = pd.DataFrame(linhas, columns=["frase", "minusc", "lema", "stop"])
    t["alfa"] = True
    t["pos"] = "NOUN"
    return t


def test_colocacao_forte_aparece_primeiro():
    rnd = random.Random(1)
    vocab = [f"w{i}" for i in range(60)]
    frases = [rnd.sample(vocab, 6) + ["santa", "olavia"] + rnd.sample(vocab, 4) for _ in range(40)]
    c = indicadores.colocacoes(_tokens(frases), frequencia_minima=5)
    assert c.iloc[0].colocacao == "santa olavia"
    assert c.iloc[0].pmi > 3


def test_colocacoes_nao_cruzam_frases():
    frases = [["fim", "x"], ["y", "inicio"]] * 10
    c = indicadores.colocacoes(_tokens(frases), frequencia_minima=1)
    assert "x y" not in set(c.colocacao)


def test_palavras_chave_ignoram_lemas_presentes_em_todos_os_segmentos():
    frases = [["comum", "comum", "lisboa", "lisboa", "lisboa"], ["comum", "comum", "sintra", "sintra", "sintra"]]
    t = _tokens(frases)
    chave = indicadores.palavras_chave(t, pd.Series({0: 1, 1: 2}), n=3)
    assert "comum" not in set(chave.lema)
    assert set(chave[chave.segmento == 1].lema) == {"lisboa"}


# --- Sentimento ---------------------------------------------------------------------------------------------------

def _frases(textos):
    return pd.DataFrame({"frase": range(len(textos)), "texto": textos,
                         "palavras": [len(t.split()) for t in textos]})


@pytest.mark.parametrize("lingua, positiva, negativa", [
    ("en", "She was very happy and the garden was beautiful today.", "The death of his father left him sad and hopeless."),
    ("pt", "Ela estava muito feliz e o jardim estava lindo hoje.", "A morte do pai deixou-o triste e sem esperança."),
    ("fr", "Elle était très heureuse et le jardin était magnifique.", "La mort de son père l'a laissé triste et désespéré."),
])
def test_sentimento_polaridade(lingua, positiva, negativa):
    pytest.importorskip(sentimento.ANALISADORES[lingua][0].split(".")[0])
    frases = _frases([positiva, negativa, "Ok."])
    tokens = pd.DataFrame({"minusc": " ".join([positiva, negativa]).lower().split(), "alfa": True})
    r = sentimento.analisar(frases, tokens, lingua)
    assert r["estado"] == "valido"
    assert frases.sentimento[0] > 0.05 and frases.sentimento[1] < -0.05
    assert math.isnan(frases.sentimento[2])          # frase curta: sem pontuação, não zero
    i = r["indicadores"]
    assert i["frases_positivas_pct"] == pytest.approx(50) and i["frases_negativas_pct"] == pytest.approx(50)
    assert 0 < i["cobertura_lexico_pct"] < 100


def test_sentimento_sem_pacote_fica_desconhecido(monkeypatch):
    def falha(lingua):
        raise ImportError("sem pacote")
    monkeypatch.setattr(sentimento, "analisador", falha)
    frases = _frases(["Uma frase qualquer com palavras suficientes."])
    r = sentimento.analisar(frases, pd.DataFrame({"minusc": ["uma"], "alfa": [True]}), "pt")
    assert r["estado"] == qualidade.DESCONHECIDO and "pip install" in r["motivo"]
    assert r["indicadores"] == {} and frases.sentimento.isna().all()


def test_sentimento_lingua_sem_lexico():
    r = sentimento.analisar(_frases(["Eine Frase mit genug Wörtern hier."]), pd.DataFrame({"minusc": [], "alfa": []}), "de")
    assert r["estado"] == qualidade.NAO_APLICAVEL


def test_grafico_de_zipf_usa_os_mesmos_dados_do_indicador():
    from livros_pln.graficos import reta_zipf
    rnd = random.Random(2)
    palavras = rnd.choices([f"p{i}" for i in range(3000)], weights=[1 / (i + 1) for i in range(3000)], k=50000)
    c = Counter(palavras)
    assert reta_zipf(indicadores.tabela_zipf(c, 5), 5)[2] == pytest.approx(indicadores.zipf(c, 5)["zipf_expoente"])


def test_pronomes_pessoais_sem_prontype():
    """O modelo francês não anota PronType nos pronomes pessoais: a pessoa gramatical basta."""
    import pytest
    spacy = pytest.importorskip("spacy")
    try:
        spacy.load("fr_core_news_md")
    except OSError:
        pytest.skip("modelo francês não instalado")
    from livros_pln import indicadores
    tokens, _, _ = indicadores.anotar(["Je ne sais pas. Je lui ai dit que nous venions."], "fr")
    pessoais = tokens[tokens.pronome_pessoal]
    assert set(pessoais.texto.str.lower()) >= {"je", "lui", "nous"}
    assert (pessoais.pessoa == "1").sum() >= 3
