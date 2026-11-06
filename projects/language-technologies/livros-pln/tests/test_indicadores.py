"""Indicadores calculados sobre textos curtos escritos para os testes (ver conftest.py)."""
import json
from pathlib import Path

import pandas as pd
import pytest
from conftest import GUTENBERG, PT

from livros_pln import catalogo, indicadores, processar
from livros_pln.configuracao import PARAMETROS


def test_legibilidade_formulas_publicadas():
    # Flesch (1948): 206,835 − 1,015·ASL − 84,6·ASW
    assert indicadores.legibilidade(10, 1.5, "en") == pytest.approx(206.835 - 10.15 - 126.9)
    # Kandel e Moles (1958): 207 − 1,015·ASL − 73,6·ASW
    assert indicadores.legibilidade(10, 1.5, "fr") == pytest.approx(207 - 10.15 - 110.4)
    # Martins et al. (1996): Flesch + 42
    assert indicadores.legibilidade(10, 1.5, "pt") == pytest.approx(206.835 - 10.15 - 126.9 + 42)
    # Flesch–Kincaid (Kincaid et al., 1975): 0,39·ASL + 11,8·ASW − 15,59
    assert indicadores.flesch_kincaid(10, 1.5) == pytest.approx(3.9 + 17.7 - 15.59)


def test_escala_legibilidade():
    assert indicadores.escala_legibilidade(95) == "muito fácil"
    assert indicadores.escala_legibilidade(65) == "padrão"
    assert indicadores.escala_legibilidade(10) == "muito difícil"
    assert indicadores.escala_legibilidade(None) is None


@pytest.mark.parametrize("paragrafo, esperado", [
    ("— Bom dia, disse ele.", True), ("-- Bom dia, disse ele.", True), ("«Bom dia», disse ele.", True),
    ('"Good morning," he said.', True), ("“Good morning,” he said.", True),
    ("Ele entrou na sala sem dizer nada.", False), ("-2 graus lá fora.", False),
])
def test_dialogo(paragrafo, esperado):
    assert indicadores.e_dialogo(paragrafo) is esperado


@pytest.mark.parametrize("lingua", ["pt", "fr", "en"])
def test_anotacao_e_indicadores(textos, lingua):
    paragrafos = textos[lingua].split("\n\n")
    tokens, frases, ents = indicadores.anotar(paragrafos, lingua)
    assert isinstance(tokens, pd.DataFrame) and len(tokens) > 100
    assert {"frase", "palavras", "profundidade", "soma_distancias", "dependencias", "subordinadas"} <= set(frases)
    ind, estados = indicadores.calcular(paragrafos, tokens, frases, ents, lingua)
    assert ind["paragrafos"] == 4
    assert 60 <= ind["palavras"] <= 120
    assert ind["frases"] >= 4
    assert ind["dialogo_pct"] == 50
    assert ind["frase_p25"] <= ind["frase_mediana"] <= ind["frase_p75"] <= ind["frase_maxima"]
    assert ind["profundidade_media"] >= 1 and ind["distancia_dependencia"] >= 1
    # texto curto: os índices que exigem textos longos ficam «não aplicável», não zero
    assert estados["mattr"]["estado"] == "nao_aplicavel"
    if ind["palavras"] < 100:
        assert estados["mtld"]["estado"] == "nao_aplicavel"
    assert (estados.get("flesch_kincaid", {}).get("estado") == "nao_aplicavel") is (lingua != "en")
    total = sum(ind[f"pos_{c.lower()}_por_1000"] or 0 for c in catalogo.CLASSES)
    assert 0 < total <= 1000.01
    # todas as chaves calculadas estão definidas no catálogo
    extra = set(ind) - set(catalogo.INDICADORES) - {"legibilidade_escala"}   # rótulo textual do índice
    assert not extra, extra


def test_classes_gramaticais_absolutas_e_relativas(textos):
    paragrafos = textos["pt"].split("\n\n")
    tokens, _, _ = indicadores.anotar(paragrafos, "pt")
    tab = indicadores.classes_gramaticais(tokens)
    assert {"classe", "nome", "ocorrencias", "por_1000_palavras"} <= set(tab)
    n = int(tokens.alfa.sum())
    linha = tab.iloc[0]
    assert linha.por_1000_palavras == pytest.approx(1000 * linha.ocorrencias / n)


def test_stopwords_extra_retiram_grafias_antigas():
    tokens, _, _ = indicadores.anotar(["Elle disse que ella vinha com elle à casa."], "pt")
    assert "elle" not in set(indicadores.frequencias(tokens).lema)


def test_catalogo_completo():
    for chave, ind in catalogo.INDICADORES.items():
        assert ind.nome and ind.definicao and ind.unidade and ind.interpretacao and ind.limitacoes, chave
        for r in ind.referencias:
            assert r in catalogo.REFERENCIAS, (chave, r)


def test_pipeline_completo_e_cache(tmp_path: Path):
    livros = tmp_path / "livros"
    livros.mkdir()
    (livros / "teste.txt").write_text(GUTENBERG.format(corpo=PT), encoding="utf-8")
    saida = tmp_path / "resultados"

    assert processar.main(["--pasta", str(livros), "--saida", str(saida)]) == 0
    registo = json.loads((saida / "livros" / "teste" / "indicadores.json").read_text(encoding="utf-8"))
    assert registo["lingua"] == "pt" and registo["titulo"] == "Um Livro de Teste"
    assert registo["processamento"]["versao_codigo"] == processar.versao_codigo()
    assert registo["parametros"]["janela_mattr"] == PARAMETROS.janela_mattr
    assert "python" in registo["ambiente"] and "spacy" in registo["ambiente"]["bibliotecas"]
    # nenhum valor ausente foi substituído por zero: os não aplicáveis ficam None, com estado e motivo
    assert registo["indicadores"]["mattr"] is None and registo["estados"]["mattr"]["motivo"]
    assert any(a["codigo"] == "texto_curto" for a in registo["qualidade"])
    for f in ["README.md", "frequencias.csv", "classes-gramaticais.csv", "frases.csv", "evolucao.csv",
              "graficos/frequencias.png", "graficos/frequencias.svg", "graficos/extensao-frases.png"]:
        assert (saida / "livros" / "teste" / f).exists(), f
    relatorio = (saida / "livros" / "teste" / "README.md").read_text(encoding="utf-8")
    assert "não aplicável" in relatorio and "Limitações" in relatorio
    tabela = pd.read_csv(saida / "indicadores.csv")
    assert list(tabela.id) == ["teste"]
    assert (saida / "README.md").exists() and (saida / "graficos" / "perfil-comparativo.png").exists()
    # com um só livro não há matriz de correlações nem Delta
    assert not (saida / "graficos" / "correlacoes.png").exists()

    # sem alterações, não reprocessa
    assert not processar.precisa(livros / "teste.txt", saida, processar.versao_codigo())
    # livro removido da pasta → resultados removidos
    (livros / "teste.txt").rename(livros / "outro.txt")
    processar.main(["--pasta", str(livros), "--saida", str(saida)])
    assert not (saida / "livros" / "teste").exists() and (saida / "livros" / "outro").exists()
