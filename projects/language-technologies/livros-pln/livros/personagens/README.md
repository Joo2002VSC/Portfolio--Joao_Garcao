# Dicionários de personagens (opcional)

Sem dicionário, as personagens de cada livro são detetadas automaticamente pelo NER do spaCy, com fusão de variantes do mesmo nome. O NER falha nomes raros e confunde por vezes pessoas e lugares; para um livro concreto, um dicionário dá uma rede muito mais fiável.

O ficheiro tem o mesmo nome que o livro, com extensão `.json` (`livros/eca-de-queiros-os-maias.txt` → `livros/personagens/eca-de-queiros-os-maias.json`):

```json
{
  "personagens": [
    {"nome": "Carlos da Maia", "aliases": ["Carlos da Maia", "Carlos Eduardo", "Carlos"]},
    {"nome": "Maria Eduarda", "aliases": ["Maria Eduarda", {"forma": "Maria", "paragrafos": [1000, 6000]}]}
  ],
  "ignorar": ["Ave Maria"]
}
```

- A procura ignora acentos; uma forma com maiúscula inicial só é encontrada com maiúscula.
- Quando duas formas começam no mesmo ponto do texto, ganha a mais longa.
- `paragrafos` limita uma forma a um intervalo de parágrafos, para desambiguar nomes repetidos.
- `ignorar` lista formas que contêm um nome mas não se referem a nenhuma personagem.
