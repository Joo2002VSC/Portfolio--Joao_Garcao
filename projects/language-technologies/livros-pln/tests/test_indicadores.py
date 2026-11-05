import json
import math
from pathlib import Path

import pandas as pd
import pytest
from conftest import GUTENBERG, PT

from livros_pln import indicadores, processar


def test_mattr_e_ttr_coincidem_em_textos_curtos():
    palavras = "a b c a b d".split()
    assert indicadores.mattr(palavras, janela=500) == pytest.approx(4 / 6)


def test_mattr_janela_movel():
    # janelas de 2: (a,a)=1 tipo, (a,b)=2, (b,b)=1 → média 4/3/2
    assert indicadores.mattr(list("aabb"), janela=2) == pytest.approx((1 + 2 + 1) / 3 / 2)


def test_yule_k():
    assert indicadores.yule_k(list("abcd")) == 0          # sem repetições
    assert indicadores.yule_k(list("aaaa")) > indicadores.yule_k(list("aabb"))


def test_silabas():
    assert indicadores.silabas("casa", "pt") == 2
    assert indicadores.silabas("biblioteca", "pt") == 4  # aproximação por grupos de vogais
    assert indicadores.silabas("table", "en") == 2
    assert indicadores.silabas("maison", "fr") == 2


def test_legibilidade_e_escala():
    facil = indicadores.legibilidade(8, 1.4, "en")
    dificil = indicadores.legibilidade(30, 1.9, "en")
    assert facil > dificil
    assert indicadores.escala_legibilidade(95) == "muito fácil"
    assert indicadores.escala_legibilidade(10) == "muito difícil"


@pytest.mark.parametrize("lingua", ["pt", "fr", "en"])
def test_anotacao_e_indicadores(textos, lingua):
    paragrafos = textos[lingua].split("\n\n")
    tokens, ents = indicadores.anotar(paragrafos, lingua)
    assert isinstance(tokens, pd.DataFrame) and len(tokens) > 100
    ind = indicadores.calcular(paragrafos, tokens, ents, lingua)
    assert ind["paragrafos"] == 4
    assert 60 <= ind["palavras"] <= 120
    assert ind["frases"] >= 4
    assert 0 < ind["mattr_500"] <= 1
    assert ind["dialogo_pct"] == 50
    assert sum(ind[f"pos_{c.lower()}_pct"] for c in indicadores.CLASSES) <= 100.01
    assert not any(isinstance(v, float) and math.isnan(v) for v in ind.values())


def test_stopwords_extra_retiram_grafias_antigas():
    tokens, _ = indicadores.anotar(["Elle disse que ella vinha com elle à casa."], "pt")
    assert "elle" not in set(indicadores.frequencias(tokens).lema)


def test_pipeline_completo_e_cache(tmp_path: Path):
    livros = tmp_path / "livros"
    livros.mkdir()
    (livros / "teste.txt").write_text(GUTENBERG.format(corpo=PT), encoding="utf-8")
    saida = tmp_path / "resultados"

    assert processar.main(["--pasta", str(livros), "--saida", str(saida)]) == 0
    registo = json.loads((saida / "livros" / "teste" / "indicadores.json").read_text(encoding="utf-8"))
    assert registo["lingua"] == "pt" and registo["titulo"] == "Um Livro de Teste"
    assert registo["processamento"]["versao_codigo"] == processar.versao_codigo()
    for f in ["README.md", "frequencias.csv", "entidades.csv", "evolucao.csv", "graficos/frequencias.png"]:
        assert (saida / "livros" / "teste" / f).exists(), f
    tabela = pd.read_csv(saida / "indicadores.csv")
    assert list(tabela.id) == ["teste"]
    assert (saida / "README.md").exists() and (saida / "graficos" / "comparacao.png").exists()

    # sem alterações, não reprocessa
    assert not processar.precisa(livros / "teste.txt", saida, processar.versao_codigo())
    # livro removido da pasta → resultados removidos
    (livros / "teste.txt").rename(livros / "outro.txt")
    processar.main(["--pasta", str(livros), "--saida", str(saida)])
    assert not (saida / "livros" / "teste").exists() and (saida / "livros" / "outro").exists()
