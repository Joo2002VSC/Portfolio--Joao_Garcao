"""Funcionalidades da versão 2: links, rede de personagens, painéis e Excel."""
import json
from pathlib import Path

import pandas as pd
import pytest
from conftest import GUTENBERG

from livros_pln import fontes, personagens, processar


# --- links -------------------------------------------------------------------

@pytest.mark.parametrize("url,gid", [
    ("https://www.gutenberg.org/ebooks/40409", "40409"),
    ("https://www.gutenberg.org/cache/epub/40409/pg40409.txt", "40409"),
    ("https://gutenberg.org/ebooks/40409.epub.noimages", "40409"),
    ("https://www.gutenberg.org/files/1342/1342-0.txt", "1342"),
    ("https://exemplo.org/livro.txt", None),
])
def test_id_gutenberg(url, gid):
    assert fontes.id_gutenberg(url) == gid


def test_candidatos():
    assert fontes.candidatos("https://www.gutenberg.org/ebooks/11")[0] == (
        "https://www.gutenberg.org/cache/epub/11/pg11.txt", "gutenberg-11.txt")
    assert fontes.candidatos("https://exemplo.org/a%20b/Um%20Livro.epub") == [
        ("https://exemplo.org/a%20b/Um%20Livro.epub", "Um Livro.epub")]
    with pytest.raises(fontes.ErroFonte):
        fontes.candidatos("https://exemplo.org/pagina.html")


class Resposta:
    def __init__(self, estado, conteudo=b""):
        self.status_code, self._c = estado, conteudo

    def iter_content(self, n):
        yield self._c


class Sessao:
    """Simula o servidor: o .txt devolve HTML (como acontece com alguns espelhos), o .epub funciona."""
    def __init__(self):
        self.pedidos = []

    def get(self, url, **_):
        self.pedidos.append(url)
        if url.endswith(".txt") or url.endswith("txt.utf-8"):
            return Resposta(200, b"<!DOCTYPE html><html>erro</html>")
        if url.endswith(".epub"):
            return Resposta(200, b"PK\x03\x04conteudo")
        return Resposta(404)


def test_descarregar_recorre_ao_epub_quando_o_txt_falha(tmp_path: Path):
    s = Sessao()
    f = fontes.descarregar("https://www.gutenberg.org/ebooks/40409", tmp_path, sessao=s)
    assert f.name == "gutenberg-40409.epub" and f.read_bytes().startswith(b"PK")
    assert s.pedidos[0].endswith("pg40409.txt")


def test_obter_ficheiro_local(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_text("texto", encoding="utf-8")
    assert fontes.obter(str(f), tmp_path) == f
    with pytest.raises(fontes.ErroFonte):
        fontes.obter(str(tmp_path / "nao-existe.txt"), tmp_path)


# --- personagens -------------------------------------------------------------

@pytest.mark.parametrize("nome,lingua,esperado", [
    ("D. Maria da Cunha", "pt", "Maria da Cunha"),
    ("o Ega", "pt", "Ega"),
    ("Mr. Darcy's", "en", "Darcy"),
    ("Madame Bovary", "fr", "Bovary"),
    ("Melanie de sa", "pt", "Melanie"),
    ("Carlos da", "pt", "Carlos"),
])
def test_normalizar(nome, lingua, esperado):
    assert personagens.normalizar(nome, lingua) == esperado


def _entidades(linhas):
    return pd.DataFrame(linhas, columns=["paragrafo", "entidade", "rotulo"])


def test_automatico_funde_nomes_e_descarta_lugares():
    linhas = []
    for p in range(10):
        linhas += [(p, "Carlos da Maia", "PER"), (p, "Carlos", "PER"), (p, "Ega", "PER")]
    linhas += [(p, "Cintra", "PER") for p in range(6)] + [(p, "Cintra", "LOC") for p in range(9)]
    por_par, menc = personagens.automatico(_entidades(linhas), "pt", min_mencoes=5)
    assert menc == {"Carlos da Maia": 20, "Ega": 10}
    g = personagens.rede(por_par, menc, min_mencoes=5)
    assert g["Carlos da Maia"]["Ega"]["peso"] == 10


def test_nome_curto_ambiguo_nao_e_fundido():
    linhas = [(p, n, "PER") for p in range(6) for n in ("Maria", "Maria Eduarda", "Maria Monforte")]
    _, menc = personagens.automatico(_entidades(linhas), "pt", min_mencoes=5)
    assert set(menc) == {"Maria", "Maria Eduarda", "Maria Monforte"}


def test_dicionario(tmp_path: Path):
    d = tmp_path / "livro.json"
    d.write_text(json.dumps({
        "personagens": [{"nome": "Carlos da Maia", "aliases": ["Carlos"]},
                        {"nome": "Maria Monforte", "aliases": [{"forma": "Maria", "paragrafos": [0, 0]}]},
                        {"nome": "Maria Eduarda", "aliases": ["Maria Eduarda", {"forma": "Maria", "paragrafos": [1, 9]}]}],
        "ignorar": ["Ave Maria"]}), encoding="utf-8")
    pars = ["Carlos viu a Maria.", "Maria e Carlos.", "Ave Maria, disse Carlos."]
    por_par, menc = personagens.por_dicionario(pars, d)
    assert por_par[0] == {"Carlos da Maia", "Maria Monforte"}
    assert por_par[1] == {"Carlos da Maia", "Maria Eduarda"}
    assert por_par[2] == {"Carlos da Maia"}
    assert menc == {"Carlos da Maia": 3, "Maria Monforte": 1, "Maria Eduarda": 1}


# --- pipeline: painel, Excel e comando analisar ------------------------------

CORPO = "\n\n".join(
    f"O Rui encontrou a Teresa em Lisboa, e a Teresa falou ao Rui do livro {i}. Depois chegou o Tomás, e o Rui "
    f"e o Tomás discutiram com a Teresa até tarde." for i in range(12))


def test_analisar_produz_painel_excel_e_rede(tmp_path: Path, capsys):
    livros = tmp_path / "livros"
    livros.mkdir()
    f = livros / "teste.txt"
    f.write_text(GUTENBERG.format(corpo=CORPO), encoding="utf-8")
    (livros / "personagens").mkdir()
    (livros / "personagens" / "teste.json").write_text(json.dumps({"personagens": [
        {"nome": n, "aliases": [n]} for n in ("Rui", "Teresa", "Tomás")]}), encoding="utf-8")
    saida = tmp_path / "resultados"
    assert processar.main(["analisar", str(f), "--saida", str(saida)]) == 0
    pasta = saida / "livros" / "teste"
    html = (pasta / "painel.html").read_text(encoding="utf-8")
    assert "Rede de personagens em 3D" in html and "scatter3d" in html
    folhas = pd.ExcelFile(pasta / "teste.xlsx").sheet_names
    assert {"Metadados", "Indicadores", "Personagens", "Ligações", "Frequências"} <= set(folhas)
    pers = pd.read_csv(pasta / "personagens.csv")
    assert set(pers.personagem) == {"Rui", "Teresa", "Tomás"}
    registo = json.loads((pasta / "indicadores.json").read_text(encoding="utf-8"))
    assert registo["metodo_personagens"].startswith("dicionário")
    assert registo["indicadores"]["personagens_na_rede"] == 3
    assert (saida / "painel.html").exists() and (saida / "indicadores.xlsx").exists()
    assert "Personagens" in capsys.readouterr().out
    # alterar o dicionário obriga a reprocessar
    assert not processar.precisa(f, saida, processar.versao_codigo())
    (livros / "personagens" / "teste.json").write_text(json.dumps({"personagens": [
        {"nome": "Rui", "aliases": ["Rui"]}]}), encoding="utf-8")
    assert processar.precisa(f, saida, processar.versao_codigo())


def test_analisar_link_invalido(capsys):
    assert processar.main(["analisar", "https://exemplo.org/pagina.html"]) == 1
    assert "tem de apontar" in capsys.readouterr().err
