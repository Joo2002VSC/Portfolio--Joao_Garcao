"""Reconstrói e valida o projeto inteiro com um só comando.

Passos: base de dados → consultas → testes → dicionário de dados → gráficos →
cabeçalhos do README → versão HTML e pasta site/. Pára no primeiro erro.
Se o matplotlib ou o markdown não estiverem instalados, salta esses passos e avisa.

Uso (a partir da raiz do projeto):
    python scripts/construir.py            # tudo
    python scripts/construir.py --rapido   # só base de dados, consultas e testes
"""
import importlib.util
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASSOS = [
    ("Base de dados", ["build_db.py"], None),
    ("Consultas", ["correr_analises.py"], None),
    ("Testes", ["testes.py"], None),
    ("Dicionário de dados", ["dicionario.py"], None),
    ("Gráficos", ["graficos.py"], "matplotlib"),
    ("Cabeçalhos do README", ["cabecalhos.py"], "matplotlib"),
    ("Versão HTML e site/", ["gerar_html.py", "--site"], "markdown"),
]


def main():
    rapido = "--rapido" in sys.argv
    inicio = time.time()
    for nome, args, requisito in PASSOS[:3] if rapido else PASSOS:
        if requisito and importlib.util.find_spec(requisito) is None:
            print(f"⚠ {nome}: saltado (falta o pacote '{requisito}': pip install -r requirements.txt)")
            continue
        print(f"▶ {nome}")
        resultado = subprocess.run([sys.executable, str(RAIZ / "scripts" / args[0]), *args[1:]],
                                   cwd=RAIZ, capture_output=True, text=True)
        if resultado.returncode != 0:
            print(resultado.stdout[-3000:], resultado.stderr[-3000:], sep="\n")
            print(f"✗ {nome} falhou. Ver a mensagem acima.")
            sys.exit(resultado.returncode)
        ultima = [l for l in resultado.stdout.strip().splitlines() if l.strip()]
        print(f"  ✓ {ultima[-1].strip() if ultima else 'ok'}")
    print(f"\nConcluído em {time.time() - inicio:.0f} s.")


if __name__ == "__main__":
    main()
