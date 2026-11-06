"""Métricas com valores de referência calculados à mão ou por uma implementação independente."""
import json
import math
import random
from pathlib import Path

import pytest
import spacy
from spacy.tokens import Doc

from livros_pln import indicadores

# --- TTR, MATTR, Yule -----------------------------------------------------------------------------------------------


def test_ttr():
    assert indicadores.ttr(list("aabc")) == pytest.approx(3 / 4)


def test_mattr_janela_movel():
    # janelas de 2: (a,a)=1 tipo, (a,b)=2, (b,b)=1 → média das TTR = (1/2 + 2/2 + 1/2) / 3
    assert indicadores.mattr(list("aabb"), janela=2) == pytest.approx((0.5 + 1 + 0.5) / 3)


def test_mattr_texto_mais_curto_que_a_janela_nao_e_zero():
    assert math.isnan(indicadores.mattr(list("abc"), janela=500))


def test_yule_k():
    assert indicadores.yule_k(list("abcd")) == 0          # sem repetições
    # K = 10⁴ · (Σ i²·V(i) − N) / N²; «aabb»: V(2)=2, N=4 → 10⁴ · (8 − 4) / 16 = 2500
    assert indicadores.yule_k(list("aabb")) == pytest.approx(2500)
    assert indicadores.yule_k(list("aaaa")) > indicadores.yule_k(list("aabb"))


# --- MTLD e HD-D ----------------------------------------------------------------------------------------------------


def test_mtld_texto_sem_repeticoes():
    # a TTR nunca desce abaixo de 0,72: só há um fator parcial, (1 − 1)/(1 − 0,72) = 0 → valor indefinido
    resultado = indicadores.mtld([f"p{i}" for i in range(50)])
    assert math.isnan(resultado) or math.isinf(resultado) or resultado > 0


def test_mtld_texto_repetitivo_e_baixo():
    assert indicadores.mtld(["a", "b"] * 100) < indicadores.mtld([f"p{i % 60}" for i in range(200)])


def test_hdd_limites():
    assert indicadores.hdd(["a"] * 100) == pytest.approx(1 / 42)            # 1 tipo garantido em todas as amostras
    assert indicadores.hdd([f"p{i}" for i in range(100)]) == pytest.approx(1.0)
    assert math.isnan(indicadores.hdd(list("abc")))                         # menos palavras do que a amostra


def _texto_sintetico(n, semente=1):
    """Texto com distribuição de Zipf, para comparar com a implementação de referência."""
    rnd = random.Random(semente)
    vocabulario = [f"w{i}" for i in range(1, 3000)]
    pesos = [1 / i for i in range(1, 3000)]
    return rnd.choices(vocabulario, weights=pesos, k=n)


@pytest.mark.parametrize("n", [100, 500, 5000])
def test_concordancia_com_lexical_diversity(n):
    """Compara com o pacote lexical_diversity (Kyle), se estiver instalado (requirements-dev.txt)."""
    ld = pytest.importorskip("lexical_diversity.lex_div")
    palavras = _texto_sintetico(n)
    assert indicadores.mtld(palavras) == pytest.approx(ld.mtld(palavras), rel=1e-9)
    assert indicadores.hdd(palavras) == pytest.approx(ld.hdd(palavras), rel=1e-9)
    assert indicadores.mattr(palavras, janela=50) == pytest.approx(ld.mattr(palavras, 50), rel=1e-9)


# --- Sílabas --------------------------------------------------------------------------------------------------------
# Listas anotadas à mão em tests/silabas_anotadas.json. As de «afinação» foram usadas durante o desenvolvimento das
# regras; as de «validação» foram escritas depois e não serviram para as ajustar.

_SILABAS = json.loads((Path(__file__).parent / "silabas_anotadas.json").read_text(encoding="utf-8"))
AFINACAO, VALIDACAO = _SILABAS["afinacao"], _SILABAS["validacao"]


def exatidao(lista, lingua):
    certas = sum(indicadores.silabas(p, lingua) == n for p, n in lista.items())
    return certas / len(lista)


@pytest.mark.parametrize("lingua", ["pt", "fr", "en"])
def test_silabas_afinacao(lingua):
    assert exatidao(AFINACAO[lingua], lingua) >= 0.9


@pytest.mark.parametrize("lingua", ["pt", "fr", "en"])
def test_silabas_validacao(lingua):
    # limiar mais baixo: lista não usada para ajustar as regras (ver docs/indicadores.md)
    assert exatidao(VALIDACAO[lingua], lingua) >= 0.8


# --- Sintaxe de dependências ----------------------------------------------------------------------------------------


def test_profundidade_e_distancia_numa_arvore_construida():
    # «O gato que eu vi dorme .»: raiz «dorme»; «gato» ← dorme; «O» ← gato; «vi» ← gato (acl:relcl);
    # «que» ← vi; «eu» ← vi; «.» ← dorme (pontuação, ignorada)
    nlp = spacy.blank("pt")
    palavras = ["O", "gato", "que", "eu", "vi", "dorme", "."]
    cabecas = [1, 5, 4, 4, 1, 5, 5]
    deps = ["det", "nsubj", "obj", "nsubj", "acl:relcl", "ROOT", "punct"]
    doc = Doc(nlp.vocab, words=palavras, heads=cabecas, deps=deps)
    profundidade, soma, n_dep, subordinadas = indicadores._sintaxe(doc[:])
    assert profundidade == 3            # dorme(0) → gato(1) → vi(2) → que/eu(3)
    # distâncias (sem pontuação): O-gato 1, gato-dorme 4, que-vi 2, eu-vi 1, vi-gato 3
    assert (soma, n_dep) == (11, 5)
    assert subordinadas == 1
