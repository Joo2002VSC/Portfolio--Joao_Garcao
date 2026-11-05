from pathlib import Path

from conftest import GUTENBERG, PT

from livros_pln import leitura, lingua


def test_gutenberg_metadados_e_corpo(tmp_path: Path):
    f = tmp_path / "teste.txt"
    f.write_text(GUTENBERG.format(corpo=PT), encoding="utf-8")
    livro = leitura.ler(f)
    assert livro.metadados["titulo"] == "Um Livro de Teste"
    assert livro.metadados["autor"] == "Autora Exemplo"
    assert livro.metadados["lingua_declarada"] == "Portuguese"
    assert livro.metadados["fonte"] == "Project Gutenberg"
    assert "Licença" not in livro.texto and "START OF" not in livro.texto
    assert len(livro.paragrafos) == 4


def test_txt_sem_cabecalho_com_linha_de_titulo(tmp_path: Path):
    f = tmp_path / "nltk.txt"
    f.write_text("[A Short Test by Jane Doe 1900]\n\nFirst paragraph.\n\nSecond one.", encoding="utf-8")
    livro = leitura.ler(f)
    assert livro.metadados == {"codificacao": "utf-8-sig", "titulo": "A Short Test", "autor": "Jane Doe", "ano": "1900"}
    assert livro.paragrafos == ["First paragraph.", "Second one."]


def test_txt_em_latin1(tmp_path: Path):
    f = tmp_path / "antigo.txt"
    f.write_bytes("Coração e ação.".encode("latin-1"))
    assert leitura.ler(f).paragrafos == ["Coração e ação."]


def test_epub(tmp_path: Path):
    from ebooklib import epub

    livro = epub.EpubBook()
    livro.set_identifier("teste-123")
    livro.set_title("Livro EPUB")
    livro.set_language("fr")
    livro.add_author("Auteur Test")
    livro.add_metadata("DC", "date", "1901")
    cap = epub.EpubHtml(title="I", file_name="c1.xhtml", lang="fr")
    cap.content = "<html><body><h1>Chapitre I</h1><p>Premier paragraphe.</p><p>Deuxième <em>paragraphe</em>.</p></body></html>"
    livro.add_item(cap)
    livro.spine = [cap]
    livro.add_item(epub.EpubNcx())
    livro.add_item(epub.EpubNav())
    f = tmp_path / "livro.epub"
    epub.write_epub(str(f), livro)

    lido = leitura.ler(f)
    assert lido.formato == "epub"
    assert lido.metadados["titulo"] == "Livro EPUB"
    assert lido.metadados["autor"] == "Auteur Test"
    assert lido.metadados["data"] == "1901"
    assert lido.paragrafos == ["Chapitre I", "Premier paragraphe.", "Deuxième paragraphe."]


def test_metadados_manuais(tmp_path: Path):
    (tmp_path / "metadados.csv").write_text("ficheiro,ano,lingua\nlivro.txt,1888,pt\n", encoding="utf-8")
    assert leitura.metadados_manuais(tmp_path) == {"livro.txt": {"ano": "1888", "lingua": "pt"}}


def test_slug():
    assert leitura.slug("Eça de Queirós - Os Maias") == "eca-de-queiros-os-maias"


def test_detecao_de_lingua(textos):
    for esperado, texto in textos.items():
        assert lingua.detetar(texto)[0] == esperado


def test_detecao_com_grafia_antiga():
    texto = "Elle disse que ella não vinha, e que o theatro estava cheio. Ahi ficou elle, quasi só, com os amigos."
    assert lingua.detetar(texto)[0] == "pt"
