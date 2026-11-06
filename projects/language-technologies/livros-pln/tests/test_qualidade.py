"""Estados dos indicadores, avisos de qualidade, Delta de Burrows e parâmetros."""
import math
from pathlib import Path

import pandas as pd
import pytest

from livros_pln import configuracao, estilometria, leitura, qualidade
from livros_pln.configuracao import PARAMETROS


def test_dividir_nao_devolve_zero():
    assert math.isnan(qualidade.dividir(5, 0))
    assert qualidade.dividir(1, 4) == 0.25


def test_sanear_marca_falhas_e_mantem_zeros_verdadeiros():
    ind = {"a": float("nan"), "b": 0.0, "c": 3.0}
    estados = {"c": {"estado": qualidade.NAO_APLICAVEL, "motivo": "x"}}
    limpos, estados = qualidade.sanear(ind, estados)
    assert limpos == {"a": None, "b": 0.0, "c": None}
    assert estados["a"]["estado"] == qualidade.FALHA


def test_aplicabilidade_texto_curto():
    e = qualidade.aplicabilidade(80, "pt", PARAMETROS)
    assert {"mattr", "mtld", "flesch_kincaid"} <= set(e)
    assert "hdd" not in e
    assert qualidade.aplicabilidade(10_000, "en", PARAMETROS) == {}


def _codigos(avisos):
    return {a["codigo"] for a in avisos}


def test_verificar_texto():
    assert _codigos(qualidade.verificar_texto([""], {}, "pt", None, 1000)) == {"texto_vazio"}
    curto = ["Era uma vez um texto pequeno."]
    assert "texto_curto" in _codigos(qualidade.verificar_texto(curto, {"pt": 0.9, "fr": 0.1}, "pt", None, 1000))
    estragado = ["CoraÃ§Ã£o e emoÃ§Ã£o numa canÃ§Ã£o."] * 3
    assert "codificacao" in _codigos(qualidade.verificar_texto(estragado, {"pt": 0.9}, "pt", None, 5))
    repetido = ["Este parágrafo aparece várias vezes por causa de um erro de extração do ficheiro original."] * 5
    assert "duplicacao" in _codigos(qualidade.verificar_texto(repetido, {"pt": 0.9}, "pt", None, 5))
    assert "lingua_incerta" in _codigos(qualidade.verificar_texto(curto, {"pt": 0.5, "es": 0.49}, "pt", None, 5))
    assert "lingua_divergente" in _codigos(qualidade.verificar_texto(curto, {"pt": 0.9}, "pt", "English", 5))


def test_verificar_anotacao():
    assert _codigos(qualidade.verificar_anotacao(0, pd.Series([], dtype=int), 0)) == {"sem_frases"}
    longas = pd.Series([200] * 10 + [10] * 90)
    assert "segmentacao" in _codigos(qualidade.verificar_anotacao(100, longas, int(longas.sum())))


def test_travessao_do_gutenberg(tmp_path: Path):
    f = tmp_path / "t.txt"
    f.write_text("--Bom dia, disse ele--e saiu.\n\nUm traço---triplo fica.", encoding="utf-8")
    p = leitura.ler_txt(f).paragrafos
    assert p[0] == "—Bom dia, disse ele—e saiu."
    assert "---" in p[1]


# --- Delta de Burrows ----------------------------------------------------------------------------------------------


def test_delta_precisa_de_tres_livros_da_mesma_lingua():
    f = {"a": pd.Series({"o": 10, "a": 5}), "b": pd.Series({"o": 8, "a": 7}), "c": pd.Series({"the": 9})}
    r = estilometria.delta(f, {"a": "pt", "b": "pt", "c": "en"})
    assert r["pt"]["estado"] == "nao_aplicavel" and r["pt"]["matriz"] is None
    assert r["en"]["estado"] == "nao_aplicavel"


def test_delta_sintetico():
    base = {"o": 100, "a": 80, "de": 60, "que": 50, "e": 40}
    f = {
        "x1": pd.Series(base),
        "x2": pd.Series({k: v + 2 for k, v in base.items()}),          # quase igual a x1
        "y": pd.Series({"o": 40, "a": 100, "de": 20, "que": 90, "e": 70}),  # perfil diferente
    }
    r = estilometria.delta(f, {k: "pt" for k in f})["pt"]
    m = r["matriz"]
    assert r["estado"] == "valido"
    assert m.loc["x1", "x1"] == 0 and m.loc["x1", "x2"] == pytest.approx(m.loc["x2", "x1"])
    assert m.loc["x1", "x2"] < m.loc["x1", "y"]


# --- Parâmetros -----------------------------------------------------------------------------------------------------


def test_parametros(tmp_path: Path):
    f = tmp_path / "p.toml"
    f.write_text("janela_mattr = 100\nsegmentos = 5\n", encoding="utf-8")
    p = configuracao.carregar(f)
    assert p.janela_mattr == 100 and p.segmentos == 5 and p.limiar_mtld == 0.72
    f.write_text("parametro_inexistente = 1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        configuracao.carregar(f)
    assert configuracao.carregar(tmp_path / "nao-existe.toml") == configuracao.Parametros()


def test_documentacao_sincronizada_com_o_catalogo():
    from livros_pln import documentacao
    assert documentacao.DESTINO.read_text(encoding="utf-8") == documentacao.gerar(), \
        "docs/indicadores.md desatualizado: correr python -m livros_pln.documentacao"
