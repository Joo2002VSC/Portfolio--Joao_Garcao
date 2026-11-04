"""Muda a versão dos ficheiros (?v=N) no index.html e recalcula o hash da política de segurança (CSP).

O mapa de importação é o único script em linha e a CSP só o autoriza pelo seu hash SHA-256:
se o conteúdo mudar (por exemplo, a versão), o hash tem de ser recalculado, senão o painel não arranca.
Uso: python scripts/versao.py 19   (ou sem argumento, para só recalcular o hash)
"""
import base64, hashlib, re, sys
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "index.html"
html = INDEX.read_text(encoding="utf-8")
if len(sys.argv) > 1:
    html = re.sub(r"\?v=\d+", f"?v={int(sys.argv[1])}", html)
mapa = re.search(r'<script type="importmap">(.*?)</script>', html, re.S).group(1)
h = base64.b64encode(hashlib.sha256(mapa.encode("utf-8")).digest()).decode()
html, n = re.subn(r"'sha256-[A-Za-z0-9+/=]+'", f"'sha256-{h}'", html)
assert n == 1, "A CSP do index.html não tem exatamente um hash."
INDEX.write_text(html, encoding="utf-8")
print(f"Hash do mapa de importação: sha256-{h}")
