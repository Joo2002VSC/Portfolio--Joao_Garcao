"""Verifica as ligações relativas nos ficheiros Markdown do repositório.

Para cada ligação ou imagem relativa ([texto](caminho), ![alt](caminho),
href="caminho" ou src="caminho"), confirma que o ficheiro ou a pasta existe.
Ignora ligações externas, âncoras internas e endereços de correio.

Uso (a partir da raiz do repositório):
    python .github/scripts/verificar_ligacoes.py
Termina com código 1 se encontrar ligações partidas.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parents[2]
PADROES = [
    re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)"),
    re.compile(r"""(?:href|src)=["']([^"']+)["']"""),
]
IGNORAR = ("http://", "https://", "mailto:", "#", "data:", "tel:")


def ligacoes(texto):
    # Ignora blocos de código, onde os caminhos são exemplos e não ligações
    texto = re.sub(r"```.*?```", "", texto, flags=re.S)
    texto = re.sub(r"`[^`\n]*`", "", texto)
    for padrao in PADROES:
        for m in padrao.finditer(texto):
            yield m.group(1)


def main():
    partidas = []
    total = 0
    for md in sorted(RAIZ.rglob("*.md")):
        if any(p in md.parts for p in (".git", "node_modules")):
            continue
        for alvo in ligacoes(md.read_text(encoding="utf-8")):
            if alvo.startswith(IGNORAR):
                continue
            caminho = unquote(alvo.split("#")[0].split("?")[0])
            if not caminho:
                continue
            total += 1
            destino = (RAIZ / caminho.lstrip("/")) if caminho.startswith("/") else (md.parent / caminho)
            if not destino.exists():
                partidas.append(f"{md.relative_to(RAIZ)} → {alvo}")
    print(f"{total} ligações relativas verificadas.")
    if partidas:
        print(f"{len(partidas)} ligações partidas:")
        print("\n".join(f"  ✗ {p}" for p in partidas))
        return 1
    print("✓ Nenhuma ligação partida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
