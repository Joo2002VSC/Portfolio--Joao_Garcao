"""Página «Livros analisados»: dados apresentados, valores em falta e casos incompletos."""
import copy
import json
from pathlib import Path

from conftest import GUTENBERG, PT

from livros_pln import pagina_livros, processar


def _registo(tmp_path: Path) -> dict:
    livros = tmp_path / "livros"
    livros.mkdir()
    (livros / "teste.txt").write_text(GUTENBERG.format(corpo=PT), encoding="utf-8")
    processar.main(["--pasta", str(livros), "--saida", str(tmp_path / "res")])
    return json.loads((tmp_path / "res" / "livros" / "teste" / "indicadores.json").read_text(encoding="utf-8"))


def test_pagina_com_livros_completos_e_incompletos(tmp_path: Path):
    r = _registo(tmp_path)
    incompleto = copy.deepcopy(r)
    incompleto.update(id="sem-dados", titulo="Livro sem metadados", autor=None, ano=None, lingua="en")
    incompleto["estados"]["sentimento_medio"] = {"estado": "desconhecido", "motivo": "o pacote vaderSentiment não está instalado"}
    incompleto["indicadores"]["sentimento_medio"] = None
    destino = tmp_path / "painel.html"
    pagina_livros.escrever([r, incompleto], destino)
    h = destino.read_text(encoding="utf-8")
    # cartões, filtros e secções
    assert h.count('class="livro"') == 2
    for ident in ("f-texto", "f-lingua", "f-autor", "f-seculo", "f-forma", "f-ordem", "f-limpar", "f-contagem",
                  "tabela-comparacao", "grafico-explorador", "dados-livros"):
        assert f'id="{ident}"' in h, ident
    # valores em falta: identificados, com o motivo, e nunca substituídos por zero
    assert "Autor desconhecido" in h and "sem data" in h
    assert 'title="o pacote vaderSentiment não está instalado"' in h
    # os dados embutidos são os do indicadores.json, sem recálculo
    dados = json.loads(h.split('id="dados-livros">')[1].split("</script>")[0].replace("<\\/", "</"))
    livro = next(l for l in dados["livros"] if l["id"] == r["id"])
    for k in ("palavras", "mtld", "frase_mediana", "sentimento_medio"):
        assert livro["valores"][k] == r["indicadores"].get(k)
    assert next(l for l in dados["livros"] if l["id"] == "sem-dados")["seculo"] is None
    # todos os indicadores do catálogo (os da análise individual) entram na comparação, uma única vez
    from livros_pln import catalogo
    chaves = [k for g in dados["grupos"] for k in g["chaves"]]
    assert sorted(chaves) == sorted(catalogo.INDICADORES) and len(chaves) == len(set(chaves))
    assert all("entre_linguas" in v for v in dados["indicadores"].values())
    assert all(g["nota"] for g in dados["grupos"])
    assert set(dados["eixos"]) == set(catalogo.INDICADORES)


def test_seculo():
    assert pagina_livros._seculo("1572") == "Século XVI"
    assert pagina_livros._seculo("1888") == "Século XIX"
    assert pagina_livros._seculo("1900") == "Século XIX"
    assert pagina_livros._seculo(None) is None and pagina_livros._seculo("s.d.") is None


def test_sem_livros_nao_escreve(tmp_path: Path):
    destino = tmp_path / "painel.html"
    pagina_livros.escrever([], destino)
    assert not destino.exists()
