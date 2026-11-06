"""Textos de teste escritos para este projeto (não são excertos de obras)."""
import pytest

PT = """— Bom dia, disse o Rui ao entrar na sala, onde a Teresa lia o jornal junto à janela.

Ela levantou os olhos, sorriu e pousou a folha sobre a mesa. Lá fora, a chuva caía devagar sobre as ruas de Guimarães, e o vento trazia o cheiro do rio.

— Chegaste cedo! Pensei que só vinhas à tarde, com o teu irmão.

O Rui explicou que o comboio tinha partido de Braga antes da hora, e que preferira caminhar desde a estação. Falaram depois da viagem, do trabalho na biblioteca e dos livros que ela andava a ler."""

FR = """— Bonjour, dit Pierre en entrant dans la pièce où Claire lisait le journal près de la fenêtre.

Elle leva les yeux, sourit et posa la feuille sur la table. Dehors, la pluie tombait lentement sur les rues de Lyon, et le vent apportait l'odeur du fleuve.

— Tu es arrivé tôt ! Je pensais que tu ne viendrais que cet après-midi, avec ton frère.

Pierre expliqua que le train était parti de Paris avant l'heure, et qu'il avait préféré marcher depuis la gare. Ils parlèrent ensuite du voyage, du travail à la bibliothèque et des livres qu'elle lisait."""

EN = """"Good morning," said Peter as he walked into the room where Claire was reading the paper by the window.

She looked up, smiled and put the page down on the table. Outside, the rain was falling slowly on the streets of London, and the wind carried the smell of the river.

"You're early! I thought you would only come in the afternoon, with your brother."

Peter explained that the train had left Oxford ahead of time, and that he had chosen to walk from the station. They then talked about the journey, the work at the library and the books she was reading."""


@pytest.fixture
def textos():
    return {"pt": PT, "fr": FR, "en": EN}


GUTENBERG = """The Project Gutenberg eBook of Um Livro de Teste

Title: Um Livro de Teste

Author: Autora Exemplo

Release date: January 1, 2020 [eBook #99999]

Language: Portuguese

*** START OF THE PROJECT GUTENBERG EBOOK UM LIVRO DE TESTE ***

{corpo}

*** END OF THE PROJECT GUTENBERG EBOOK UM LIVRO DE TESTE ***

Licença e outras informações que não fazem parte do livro.
"""
