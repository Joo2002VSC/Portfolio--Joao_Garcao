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
    assert livro.metadados == {"codificacao": "utf-8-sig", "titulo": "A Short Test", "autor": "Jane Doe", "ano": "1900",
                               "forma": "prosa"}
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


def test_so_metadados_principais():
    bruto = {"titulo": "Os Maias", "autor": "Eça de Queirós", "fonte": "Project Gutenberg", "identificador": "gutenberg:40409",
             "data_publicacao_digital": "2012", "lingua_declarada": "Portuguese", "codificacao": "utf-8", "creditos": "x"}
    m = leitura.principais(bruto, "Português")
    assert set(m) == {"titulo", "autor", "ano", "idioma", "fonte"}
    assert m["fonte"] == "Project Gutenberg, n.º\u00a040409" and m["idioma"] == "Português"
    assert m["ano"] is None                     # a data de publicação digital não é o ano do livro
    assert leitura.principais({**bruto, "publicacao_original": "Porto, 1888"}, "Português")["ano"] == "1888"
    assert leitura.principais({**bruto, "ano": "1888", "fonte_manual": "Edição Livros do Brasil"}, "Português")[
        "fonte"] == "Edição Livros do Brasil"
    epub = leitura.principais({"titulo": "T", "data": "1901-05-01", "editora": "Gallimard", "fonte": "EPUB"}, "Francês")
    assert epub["ano"] == "1901" and epub["fonte"] == "Gallimard"


def test_metadados_manuais_fonte(tmp_path: Path):
    (tmp_path / "metadados.csv").write_text("ficheiro,fonte\nlivro.txt,Biblioteca Nacional\n", encoding="utf-8")
    assert leitura.metadados_manuais(tmp_path) == {"livro.txt": {"fonte_manual": "Biblioteca Nacional"}}


def test_epub_sem_notas_finais_da_edicao_digital(tmp_path):
    """As notas finais de edições digitais (créditos, licença) não entram na análise."""
    from ebooklib import epub
    from livros_pln import leitura
    livro = epub.EpubBook()
    livro.set_title("Teste")
    livro.set_language("fr")
    corpo = "".join(f"<p>Phrase numéro {i} du roman.</p>" for i in range(20))
    cap = epub.EpubHtml(title="c", file_name="c.xhtml", lang="fr",
                        content=f"<html><body>{corpo}<p>À propos de cette édition électronique</p>"
                                "<p>Texte libre de droits.</p></body></html>")
    livro.add_item(cap)
    livro.spine = [cap]
    livro.add_item(epub.EpubNcx())
    livro.add_item(epub.EpubNav())
    destino = tmp_path / "t.epub"
    epub.write_epub(str(destino), livro)
    l = leitura.ler(destino)
    assert l.paragrafos[-1] == "Phrase numéro 19 du roman."
    assert l.metadados["notas_da_edicao_removidas"] == 2


def test_ccel_sem_ficha_nem_indices(tmp_path):
    """Textos da Christian Classics Ethereal Library: a ficha inicial e os índices finais não entram na análise."""
    from livros_pln import leitura
    corpo = "\n\n".join(f"   Paragraph number {i} of the story, with enough words to count." for i in range(30))
    texto = ("     ____________________\n\n           Title: A Story\n     ____________________\n\nA STORY\n\n"
             "   Translated by Someone\n     ____________________\n\nI\n\n" + corpo + "\n     ____________________\n\n"
             "                                    Indexes\n     ____________________\n\n"
             "            This document is from the Christian Classics Ethereal\n               Library.\n")
    f = tmp_path / "historia.txt"
    f.write_text(texto, encoding="utf-8")
    l = leitura.ler(f)
    assert l.paragrafos[0] == "I" and "Indexes" not in l.texto and "Title:" not in l.texto
    assert l.metadados["fonte"] == "Christian Classics Ethereal Library"
