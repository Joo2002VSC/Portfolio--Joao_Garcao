"""Gera docs/indicadores.md a partir do catálogo (python -m livros_pln.documentacao).

A documentação não é escrita à mão: assim, as definições, fórmulas e referências dos
relatórios, do Excel e da documentação são sempre as mesmas.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import catalogo
from .configuracao import Parametros

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "docs" / "indicadores.md"
SILABAS = RAIZ / "tests" / "silabas_anotadas.json"
NOMES_LINGUAS = {"pt": "português", "fr": "francês", "en": "inglês"}


def _celula(texto: str) -> str:
    return (texto or "—").replace("|", "\\|").replace("\n", " ")


def _silabas() -> list[str]:
    if not SILABAS.exists():
        return []
    from .indicadores import silabas
    dados = json.loads(SILABAS.read_text(encoding="utf-8"))
    linhas = ["## Exatidão da estimativa de sílabas", "",
              "As fórmulas de legibilidade dependem do número de sílabas, estimado por regras ortográficas (grupos de "
              "vogais, ditongos e hiatos em português, «e» mudo em francês e inglês). A exatidão foi medida em listas "
              "anotadas à mão (`tests/silabas_anotadas.json`). As listas de **afinação** foram usadas para desenvolver "
              "as regras, pelo que sobrestimam a exatidão; as de **validação** foram escritas depois e não serviram "
              "para as ajustar. O viés é a diferença relativa entre o total de sílabas estimado e o anotado.", "",
              "| Língua | Lista | Palavras certas | Viés no total | Erros |", "|---|---|---|---|---|"]
    for lista, rotulo in [("afinacao", "afinação"), ("validacao", "validação")]:
        for lg, d in dados[lista].items():
            erros = [(w, n, silabas(w, lg)) for w, n in d.items() if silabas(w, lg) != n]
            total, estimado = sum(d.values()), sum(silabas(w, lg) for w in d)
            vies = f"{100 * (estimado - total) / total:+.1f} %".replace(".", ",")
            err = ", ".join(f"{w} ({e} em vez de {n})" for w, n, e in erros) or "—"
            linhas.append(f"| {NOMES_LINGUAS[lg]} | {rotulo} | {len(d) - len(erros)}/{len(d)} | {vies} | {err} |")
    linhas += ["", "As listas são pequenas (20 a 35 palavras): estes valores indicam a ordem de grandeza do erro, "
               "não uma avaliação definitiva. Os erros em palavras isoladas compensam-se parcialmente no total de um "
               "livro, mas o viés sistemático afeta diretamente o índice de legibilidade (cada 0,01 sílabas por "
               "palavra altera o índice de Flesch em cerca de 0,85 pontos).", ""]
    return linhas


def gerar() -> str:
    p = Parametros()
    l = ["# Indicadores", "",
         "<!-- Gerado por `python -m livros_pln.documentacao` a partir de livros_pln/catalogo.py. Não editar à mão. -->",
         "",
         "Cada indicador tem definição, fórmula, unidade, interpretação, limitações e referências. A coluna "
         "«Entre línguas» indica se os valores de livros em línguas diferentes são diretamente comparáveis; quando "
         "não são, compare apenas livros da mesma língua.", "",
         "Notação: *N* = palavras; *V* = formas distintas; *V(i)* = formas que ocorrem *i* vezes; *PF* = palavras por "
         "frase; *SP* = sílabas por palavra.", "",
         "## Estados dos valores", "",
         "Um valor ausente nunca é substituído por zero. Cada indicador tem um destes estados:", "",
         "| Estado | Significado |", "|---|---|",
         "| válido | Calculado e dentro das condições de aplicação. |",
         "| não aplicável | O indicador não se aplica a este texto (por exemplo, MATTR num texto com menos palavras do "
         "que a janela, ou Flesch–Kincaid fora do inglês). O motivo é registado. |",
         "| desconhecido | A informação necessária não está disponível (por exemplo, sem personagens identificadas). |",
         "| falha | O cálculo produziu um valor inválido. |", "",
         "## Parâmetros por omissão", "",
         "Alteráveis em `config/parametros.toml`; os valores usados ficam registados em cada `indicadores.json` e no "
         "Excel.", "", "| Parâmetro | Valor |", "|---|---|"]
    l += [f"| `{k}` | {str(v).replace('.', ',')} |" for k, v in vars(p).items()]
    l.append("")
    for grupo, chaves in catalogo.por_grupo().items():
        if not chaves:
            continue
        l += [f"## {grupo}", "", "| Indicador | Definição | Fórmula | Unidade | Interpretação | Limitações | "
              "Entre línguas | Referências |", "|---|---|---|---|---|---|---|---|"]
        for k in chaves:
            i = catalogo.INDICADORES[k]
            refs = "; ".join(catalogo.REFERENCIAS[r].split(" (")[0] + " (" + catalogo.REFERENCIAS[r].split(" (")[1]
                             .split(")")[0] + ")" for r in i.referencias) or "—"
            l.append(f"| **{_celula(i.nome)}** <br>`{k}` | {_celula(i.definicao)} | {_celula(i.formula)} | "
                     f"{_celula(i.unidade)} | {_celula(i.interpretacao)} | {_celula(i.limitacoes)} | "
                     f"{'sim' if i.entre_linguas else 'não'} | {refs} |")
        l.append("")
    l += _silabas()
    l += ["## Referências", ""] + [f"- {r}" for r in sorted(catalogo.REFERENCIAS.values())] + [""]
    return "\n".join(l)


def main() -> int:
    DESTINO.parent.mkdir(exist_ok=True)
    DESTINO.write_text(gerar(), encoding="utf-8")
    print(f"✓ {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
