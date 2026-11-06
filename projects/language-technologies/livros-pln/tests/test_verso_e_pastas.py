"""Textos em verso e pastas de trabalho locais."""
import json
import random
from pathlib import Path

from livros_pln import configuracao, fontes, leitura, processar

VERSOS = ["As armas e os barões assinalados", "Que da ocidental praia lusitana", "Por mares nunca de antes navegados",
          "Passaram ainda além da Taprobana", "Em perigos e guerras esforçados", "Mais do que prometia a força humana",
          "E entre gente remota edificaram", "Novo reino que tanto sublimaram", "Cantando espalharei por toda parte",
          "Se a tanto me ajudar o engenho e arte", "Cessem do sábio grego e do troiano", "As navegações grandes que fizeram"]


def _poema(estrofes: int = 40, semente: int = 1) -> str:
    rnd = random.Random(semente)
    blocos = []
    for _ in range(estrofes):
        linhas = [rnd.choice(VERSOS) + rnd.choice([",", ";", ",", "."]) for _ in range(8)]
        linhas[-1] = linhas[-1][:-1] + "."
        blocos.append("\n".join(linhas))
    return "\n\n".join(blocos)


def test_forma_verso_e_prosa():
    m = leitura.forma_do_texto(_poema(10).split("\n\n"))
    assert m["forma"] == "verso" and m["versos_por_estrofe"] == 8 and m["estrofes"] == 10 and m["versos"] == 80
    prosa = ["Era uma vez um texto em prosa com linhas compridas, quebradas como no Project Gutenberg, que\n"
             "continua na linha seguinte com o mesmo comprimento aproximado de setenta caracteres e\n"
             "ainda mais uma linha para garantir que o bloco tem pelo menos quatro linhas de prosa\n"
             "corrida, terminando aqui com um ponto final."] * 10
    assert leitura.forma_do_texto(prosa) == {"forma": "prosa"}


def test_pipeline_em_verso_marca_legibilidade_nao_aplicavel(tmp_path: Path):
    livros = tmp_path / "livros"
    livros.mkdir()
    (livros / "poema.txt").write_text(_poema(40), encoding="utf-8")
    saida = tmp_path / "resultados"
    assert processar.main(["--pasta", str(livros), "--saida", str(saida)]) == 0
    r = json.loads((saida / "livros" / "poema" / "indicadores.json").read_text(encoding="utf-8"))
    assert r["forma"] == "verso"
    assert r["indicadores"]["versos_por_estrofe"] == 8 and r["indicadores"]["estrofes"] == 40
    assert r["estados"]["legibilidade"]["estado"] == "nao_aplicavel" and r["indicadores"]["legibilidade"] is None
    assert r["estados"]["dialogo_pct"]["estado"] == "nao_aplicavel"
    assert any(a["codigo"] == "verso" for a in r["qualidade"])
    painel = (saida / "livros" / "poema" / "painel.html").read_text(encoding="utf-8")
    assert "Legibilidade não aplicável" in painel and "voltar-topo" in painel


def test_pastas_locais(tmp_path: Path):
    assert configuracao.pastas(tmp_path / "nao-existe.toml") == (Path("livros"), Path("resultados"))
    f = tmp_path / "pastas.toml"
    f.write_text('livros = "~/Livros"\nresultados = "/tmp/res"\n', encoding="utf-8")
    livros, resultados = configuracao.pastas(f)
    assert livros == Path.home() / "Livros" and resultados == Path("/tmp/res")


def test_pastas_locais_nao_mudam_a_impressao_digital(tmp_path: Path, monkeypatch):
    antes = processar.versao_codigo()
    destino = configuracao.PASTAS
    existia = destino.exists()
    if not existia:
        destino.write_text('livros = "/tmp/x"\n', encoding="utf-8")
    try:
        assert processar.versao_codigo() == antes
    finally:
        if not existia:
            destino.unlink()


def test_nome_do_ficheiro_descarregado():
    assert fontes.slug_nome("Camões — Os Lusíadas") == "camoes-os-lusiadas"
    assert fontes.slug_nome("camoes-os-lusiadas.txt") == "camoes-os-lusiadas"
