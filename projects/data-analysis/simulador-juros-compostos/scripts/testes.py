"""
Testes do modelo. Cada teste verifica uma propriedade que o modelo TEM de cumprir,
independentemente dos números concretos.

Uso:  python scripts/testes.py      (sai com código 1 se algum teste falhar)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from simulador import CENARIOS, Parametros, simular  # noqa: E402

# Um plano sem qualquer aleatoriedade: deve dar sempre o mesmo número em todos os cenários.
SEM_RISCO = Parametros(
    vol_acoes=0, vol_cripto=0, vol_inflacao=0, p_crise=0, p_regulacao=0,
    p_choque_inflacao=0, p_pausa=0, custos=0, crescimento_aporte=0, n_cenarios=50,
)


def formula_classica(capital, aporte_mensal, taxa_anual, anos) -> float:
    """Valor futuro com aportes no início de cada mês: P·q^n + a·q·(q^n − 1)/(q − 1)."""
    q, n = (1 + taxa_anual) ** (1 / 12), anos * 12
    return capital * q ** n + aporte_mensal * q * (q ** n - 1) / (q - 1)


def teste_reduz_a_formula_classica():
    p = SEM_RISCO.com(peso_cripto=0, retorno_acoes=0.06, ano_alvo=2056)
    r = simular(p)
    esperado = formula_classica(p.capital_inicial, p.aporte, 0.06, 30)
    assert np.allclose(r.nominal[-1], esperado, rtol=1e-9), (r.nominal[-1, 0], esperado)
    assert np.isclose(r.deterministico[-1], esperado, rtol=1e-9)


def teste_retorno_zero_devolve_o_investido():
    p = SEM_RISCO.com(retorno_acoes=0, retorno_cripto=0)
    r = simular(p)
    assert np.allclose(r.nominal[-1], r.investido[-1])


def teste_frequencias_somam_o_mesmo_por_ano():
    for freq, aporte in (("semanal", 120.0), ("mensal", 120.0 * 52 / 12), ("anual", 120.0 * 52)):
        r = simular(SEM_RISCO.com(frequencia=freq, aporte=aporte, retorno_acoes=0, retorno_cripto=0))
        investido_anual = (r.investido[-1, 0] - SEM_RISCO.capital_inicial) / SEM_RISCO.anos
        assert np.isclose(investido_anual, 120.0 * 52), (freq, investido_anual)


def teste_inflacao_zero_real_igual_nominal():
    r = simular(Parametros(inflacao=0, vol_inflacao=0, p_choque_inflacao=0, n_cenarios=200))
    assert np.allclose(r.real, r.nominal)


def teste_choques_cripto_nao_afetam_carteira_so_acoes():
    base = Parametros(peso_cripto=0, n_cenarios=300)
    a = simular(base.com(p_regulacao=0.0))
    b = simular(base.com(p_regulacao=0.9, queda_regulacao=0.9))
    assert np.allclose(a.nominal, b.nominal)


def teste_crises_baixam_a_mediana():
    sem = simular(Parametros(p_crise=0))
    com = simular(Parametros(p_crise=0.15))
    assert np.median(com.nominal[-1]) < np.median(sem.nominal[-1])


def teste_pausas_reduzem_o_investido():
    sem = simular(Parametros(p_pausa=0)).investido[-1].mean()
    com = simular(Parametros(p_pausa=0.3)).investido[-1].mean()
    assert com < sem


def teste_reprodutivel_com_a_mesma_semente():
    assert np.array_equal(simular(Parametros()).nominal, simular(Parametros()).nominal)


def teste_ordem_dos_cenarios():
    med = {n: np.median(simular(p).real[-1]) for n, p in CENARIOS.items()}
    assert med["Otimista"] > med["Base"] > med["Pessimista"], med
    assert med["Base"] > med["Estagflação"], med


def main() -> int:
    testes = [(n, f) for n, f in globals().items() if n.startswith("teste_") and callable(f)]
    falhas = 0
    for nome, f in testes:
        try:
            f()
            print(f"  ok     {nome}")
        except AssertionError as e:
            falhas += 1
            print(f"  FALHOU {nome}: {e}")
    print(f"\n{len(testes) - falhas}/{len(testes)} testes passaram.")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
