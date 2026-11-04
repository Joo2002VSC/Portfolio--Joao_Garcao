"""
Estudos de robustez do modelo, escritos em convergencia.md:

  1. Convergência de Monte Carlo — quanto variam os resultados com 2 000, 10 000 e 50 000 cenários
     quando só muda a semente aleatória;
  2. Log-normal vs Student-t — o que muda nas caudas quando os choques mensais têm caudas pesadas;
  3. Correlação efetiva — correlação entre ações e cripto com e sem o efeito das crises.

Uso:  python scripts/convergencia.py        (demora ~1 minuto)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from simulador import CENARIOS, resumir, simular  # noqa: E402

BASE = CENARIOS["Base"]


def fmt(v, casas=0):
    return f"{v:,.{casas}f}".replace(",", " ").replace(".", ",")


def convergencia() -> str:
    linhas = [
        "| Cenários | Sementes | Mediana real (média) | Desvio entre sementes | IC 95% da mediana numa só corrida | P10 real: desvio | P(objetivo): desvio |",
        "|--:|--:|--:|--:|--:|--:|--:|",
    ]
    for n, k in ((2000, 20), (10000, 12), (50000, 6)):
        med, p10, pob, larg = [], [], [], []
        for s in range(k):
            r = simular(BASE.com(n_cenarios=n, semente=1000 + s))
            x = r.real[-1]
            med.append(np.median(x)); p10.append(np.percentile(x, 10))
            pob.append((x >= BASE.objetivo_real).mean())
            lo, hi = np.percentile(x, [50 - 98 / np.sqrt(n), 50 + 98 / np.sqrt(n)])
            larg.append((hi - lo) / 2)
        m = np.mean(med)
        linhas.append(
            f"| {fmt(n)} | {k} | {fmt(m)} € | ±{fmt(np.std(med))} € ({fmt(np.std(med) / m * 100, 2)} %) "
            f"| ±{fmt(np.mean(larg))} € | ±{fmt(np.std(p10))} € | ±{fmt(np.std(pob) * 100, 2)} p.p. |"
        )
    return "\n".join(linhas)


def distribuicoes() -> str:
    linhas = [
        "| Modelo | Mediana real | P10 real | P5 real | Média dos 5 % piores | P(objetivo) | Queda máxima mediana | Perda anual a 95 % (VaR) | Média das perdas além do VaR (CVaR) |",
        "|---|--:|--:|--:|--:|--:|--:|--:|--:|",
    ]
    for nome, kw in (("Log-normal", {}), ("Student-t, ν = 8", dict(distribuicao="t", graus_liberdade=8)),
                     ("Student-t, ν = 5", dict(distribuicao="t", graus_liberdade=5)),
                     ("Student-t, ν = 3", dict(distribuicao="t", graus_liberdade=3))):
        s = resumir(simular(BASE.com(n_cenarios=50000, **kw)))
        linhas.append(
            f"| {nome} | {fmt(s['mediana_real'])} € | {fmt(s['p10_real'])} € | {fmt(s['p5_real'])} € | {fmt(s['cvar5_real'])} € "
            f"| {fmt(s['prob_objetivo'] * 100, 1)} % | {fmt(s['drawdown_mediano'] * 100, 1)} % | {fmt(-s['var95_anual'] * 100, 1)} % "
            f"| {fmt(-s['cvar95_anual'] * 100, 1)} % |"
        )
    return "\n".join(linhas)


def correlacao_efetiva() -> str:
    """Mesma semente com carteira só de ações e só de cripto → mesmos choques, caminhos separados."""
    linhas = ["| Situação | Correlação anual dos log-retornos (ações × cripto) |", "|---|--:|"]
    for nome, kw in (("Sem crises (só a correlação do modelo, ρ = 0,35)", dict(p_crise=0, p_regulacao=0)),
                     ("Com crises e regulação (cenário Base)", {})):
        p = BASE.com(aporte=0, n_cenarios=20000, ano_alvo=2036, **kw)
        a = simular(p.com(peso_cripto=0)).nominal
        c = simular(p.com(peso_cripto=1)).nominal
        la, lc = np.log(a[1:] / a[:-1]).ravel(), np.log(c[1:] / c[:-1]).ravel()
        linhas.append(f"| {nome} | {fmt(np.corrcoef(la, lc)[0, 1], 3)} |")
    return "\n".join(linhas)


def main() -> None:
    texto = f"""# Robustez do modelo

Gerado por `scripts/convergencia.py` com o cenário Base (2 000 € iniciais, 200 €/mês, 80/20, 2026–2046).

## 1. Convergência de Monte Carlo

Cada linha repete a simulação com sementes diferentes. O "desvio entre sementes" é o erro de Monte Carlo
observado; o "IC 95 % numa só corrida" é o intervalo que a página mostra, calculado pelas estatísticas de ordem.

{convergencia()}

O erro diminui com √N: multiplicar os cenários por 25 (de 2 000 para 50 000) divide o erro por ~5.
**Mais cenários reduzem o erro de amostragem, não o erro dos pressupostos.** Uma rentabilidade
esperada errada em 1 p.p. desloca a mediana muito mais do que o erro de Monte Carlo com 2 000 cenários.

## 2. Log-normal vs Student-t (50 000 cenários)

Na Student-t os choques mensais têm a mesma variância, mas caudas mais pesadas, e um fator comum às
duas classes de ativos (t multivariada), o que torna as quedas extremas mais prováveis de acontecer juntas.

{distribuicoes()}

Leitura: com estes parâmetros, trocar a log-normal pela Student-t muda pouco os resultados. Há duas razões.
Os choques são mensais e a soma de 12 meses aproxima-se da normal (teorema do limite central). E as crises
de mercado, que são saltos discretos, já dominam as caudas do modelo. Só com ν = 3 a diferença se nota:
a mediana desce cerca de 3 % e a média das piores perdas anuais (CVaR) agrava-se ligeiramente. A queda
máxima mediana até diminui, porque a t concentra mais meses perto do centro e deixa as perdas para
poucos meses extremos. Por isso o modelo por defeito continua a ser a log-normal, e a t fica disponível
como teste de sensibilidade.

## 3. Correlação efetiva com crises

{correlacao_efetiva()}

As crises atingem as duas classes de ativos no mesmo mês, por isso a correlação observada sobe
acima do parâmetro ρ. Na prática, isto já representa uma "correlação de crise" mais alta do que a
de períodos normais, sem ser preciso um segundo parâmetro.
"""
    (RAIZ / "convergencia.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
