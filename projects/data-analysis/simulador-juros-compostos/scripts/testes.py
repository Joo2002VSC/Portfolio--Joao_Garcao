"""
Testes do modelo Python. Cada teste verifica uma propriedade que o modelo TEM de cumprir.

  A–G  casos obrigatórios (capitalização, rentabilidade zero, sem investimento, reprodutibilidade,
       inflação, aportes crescentes, custos);
  P*   propriedades matemáticas;
  S*   testes estatísticos (tolerâncias de ±4 erros-padrão: falso alarme < 1 em 10 000);
  V*   validação de entradas.

Uso:  python scripts/testes.py      (sai com código 1 se algum teste falhar)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from simulador import (  # noqa: E402
    CENARIOS, Parametros, simular, resumir, tir_anual, prob_mensal, rentabilidade_implicita, ic_mediana,
)
from simulador.modelo import _choques  # noqa: E402

SEM_RISCO = Parametros(
    vol_acoes=0, vol_cripto=0, vol_inflacao=0, p_crise=0, p_regulacao=0, p_choque_inflacao=0,
    p_pausa=0, custos=0, crescimento_aporte=0, inflacao=0, peso_cripto=0, n_cenarios=20,
)


def formula_classica(capital, aporte_mensal, taxa_anual, anos) -> float:
    """Valor futuro com aportes no início de cada mês: P·qⁿ + a·q·(qⁿ − 1)/(q − 1)."""
    q, n = (1 + taxa_anual) ** (1 / 12), anos * 12
    if q == 1:
        return capital + aporte_mensal * n
    return capital * q ** n + aporte_mensal * q * (q ** n - 1) / (q - 1)


# ---------------------------------------------------------------- casos obrigatórios

def teste_A_capitalizacao_sem_volatilidade():
    for peso, campo in ((0.0, "retorno_acoes"), (1.0, "retorno_cripto")):
        p = SEM_RISCO.com(peso_cripto=peso, **{campo: 0.06}, ano_alvo=2056)
        r = simular(p)
        esperado = formula_classica(p.capital_inicial, p.aporte, 0.06, 30)
        assert np.allclose(r.nominal[-1], esperado, rtol=1e-10), (peso, r.nominal[-1, 0], esperado)
        assert np.isclose(r.deterministico[-1], esperado, rtol=1e-10)


def teste_A2_classica_igual_a_estocastica_com_custos():
    """Determinística e probabilística coincidem sem risco, mesmo com custos e aportes crescentes."""
    p = SEM_RISCO.com(peso_cripto=0, retorno_acoes=0.05, custos=0.008, crescimento_aporte=0.03, frequencia="semanal")
    r = simular(p)
    assert np.allclose(r.nominal[:, 0], r.deterministico, rtol=1e-10)


def teste_B_rentabilidade_zero():
    p = SEM_RISCO.com(retorno_acoes=0, retorno_cripto=0)
    r = simular(p)
    esperado = p.capital_inicial + p.aporte * 12 * p.anos
    assert np.allclose(r.nominal[-1], esperado) and np.allclose(r.investido[-1], esperado)


def teste_C_sem_investimento():
    r = simular(Parametros(capital_inicial=0, aporte=0, n_cenarios=300))
    assert np.all(r.nominal == 0) and np.all(r.real == 0) and np.all(r.investido == 0)
    s = resumir(r)
    assert s["mediana_nominal"] == 0 and s["tir_nominal"][50] is None and s["rentab_acumulada_mediana"] is None
    assert s["prob_perda_nominal"] == 0  # 0 < 0 é falso: não há perda sem investimento


def teste_D_reprodutibilidade():
    a, b = simular(Parametros()), simular(Parametros())
    assert np.array_equal(a.nominal, b.nominal) and np.array_equal(a.real, b.real)
    assert not np.array_equal(a.nominal, simular(Parametros(semente=1)).nominal)
    ta = simular(Parametros(distribuicao="t"))
    assert np.array_equal(ta.nominal, simular(Parametros(distribuicao="t")).nominal)


def teste_E_inflacao():
    r = simular(Parametros(n_cenarios=500))
    assert np.allclose(r.real, r.nominal / r.precos, rtol=1e-12)
    p = SEM_RISCO.com(inflacao=0.03, aporte=0)
    r = simular(p)
    assert np.allclose(r.precos[-1], 1.03 ** p.anos, rtol=1e-12)
    assert np.allclose(r.investido_real[-1], p.capital_inicial)  # capital entra a preços de hoje


def teste_E2_investido_real_desconta_cada_aporte():
    p = SEM_RISCO.com(inflacao=0.04, capital_inicial=0, aporte=100, ano_alvo=2028)
    r = simular(p)
    fator = 1.04 ** (1 / 12)
    esperado = sum(100 / fator ** t for t in range(24))
    assert np.allclose(r.investido_real[-1], esperado, rtol=1e-12)


def teste_F_aportes_crescentes():
    p = SEM_RISCO.com(capital_inicial=0, aporte=100, crescimento_aporte=0.10, retorno_acoes=0, retorno_cripto=0)
    r = simular(p)
    assert np.isclose(r.aportes_mensais[11], 100) and np.isclose(r.aportes_mensais[12], 110)  # sobe em janeiro
    incrementos = np.diff(r.investido[:, 0])
    assert np.allclose(incrementos / (1200 * 1.1 ** np.arange(p.anos)), 1)
    pa = SEM_RISCO.com(capital_inicial=0, aporte=1000, crescimento_aporte=0.10, frequencia="anual", retorno_acoes=0, retorno_cripto=0)
    ra = simular(pa)
    assert np.isclose(ra.aportes_mensais[24], 1210) and ra.aportes_mensais[25] == 0


def teste_G_custos():
    p = SEM_RISCO.com(retorno_acoes=0, retorno_cripto=0, custos=0.01, aporte=0)
    r = simular(p)
    assert np.allclose(r.nominal[:, 0], p.capital_inicial * 0.99 ** np.arange(p.anos + 1), rtol=1e-12)
    p2 = p.com(capital_inicial=0, aporte=100)
    r2 = simular(p2)
    m = p2.anos * 12
    esperado = sum(100 * 0.99 ** ((m - t) / 12) for t in range(m))  # cada aporte paga custos desde que entra
    assert np.allclose(r2.nominal[-1], esperado, rtol=1e-12)


# ---------------------------------------------------------------- propriedades

def teste_P1_frequencias_somam_o_mesmo_por_ano():
    for freq, aporte in (("semanal", 120.0), ("mensal", 120.0 * 52 / 12), ("anual", 120.0 * 52)):
        r = simular(SEM_RISCO.com(frequencia=freq, aporte=aporte, retorno_acoes=0, retorno_cripto=0))
        anual = (r.investido[-1, 0] - SEM_RISCO.capital_inicial) / SEM_RISCO.anos
        assert np.isclose(anual, 120.0 * 52), (freq, anual)


def teste_P2_regulacao_nao_afeta_carteira_so_de_acoes():
    base = Parametros(peso_cripto=0, n_cenarios=300)
    a, b = simular(base.com(p_regulacao=0)), simular(base.com(p_regulacao=0.9, queda_regulacao=0.9))
    assert np.allclose(a.nominal, b.nominal)


def teste_P3_monotonia_com_numeros_aleatorios_comuns():
    meds = [np.median(simular(Parametros(retorno_acoes=r)).real[-1]) for r in (0.03, 0.05, 0.07, 0.09)]
    assert all(x < y for x, y in zip(meds, meds[1:])), meds
    assert np.median(simular(Parametros(p_crise=0.15)).nominal[-1]) < np.median(simular(Parametros(p_crise=0)).nominal[-1])


def teste_P4_pausa_certa_corta_metade_dos_aportes_mensais():
    p = SEM_RISCO.com(p_pausa=1.0, retorno_acoes=0, retorno_cripto=0)
    r = simular(p)
    assert np.allclose(r.investido[-1], p.capital_inicial + p.aporte * 6 * p.anos)


def teste_P5_tir_sem_risco_e_a_taxa_liquida():
    p = SEM_RISCO.com(retorno_acoes=0.06, custos=0.005, inflacao=0.02)
    s = resumir(simular(p))
    assert np.isclose(s["tir_nominal"][50], 1.06 * 0.995 - 1, atol=1e-9), s["tir_nominal"]
    assert np.isclose(s["tir_real"][50], 1.06 * 0.995 / 1.02 - 1, atol=1e-9), s["tir_real"]  # equação de Fisher


def teste_P6_tir_de_fluxo_simples():
    assert np.isclose(tir_anual(np.array([100.0] + [0] * 11), 110.0), 0.10, atol=1e-12)
    assert tir_anual(np.zeros(12), 0) is None


def teste_P7_risco_nulo_sem_volatilidade():
    p = SEM_RISCO.com(retorno_acoes=0.05, custos=0.002)
    s = resumir(simular(p))
    assert s["drawdown_p90"] < 1e-12 and np.isclose(s["var95_anual"], 1.05 * 0.998 - 1)
    assert s["prob_perda_nominal"] == 0 and s["prob_perda_real"] == 0


def teste_P8_drawdown_inclui_a_crise():
    p = SEM_RISCO.com(p_crise=1.0, peso_cripto=0, queda_crise_acoes=0.3, retorno_acoes=0.05, ano_alvo=2028)
    r = simular(p)
    assert np.all(r.drawdown_max >= 0.3 - 1e-12)


def teste_P9_ordem_dos_cenarios():
    med = {n: np.median(simular(p).real[-1]) for n, p in CENARIOS.items()}
    assert med["Otimista"] > med["Base"] > med["Pessimista"], med
    assert med["Base"] > med["Estagflação"], med


def teste_P10_perda_comparada_por_cenario():
    r = simular(Parametros(p_pausa=0.3, n_cenarios=1000))
    s = resumir(r)
    assert np.isclose(s["prob_perda_nominal"], (r.nominal[-1] < r.investido[-1]).mean())
    assert np.isclose(s["prob_perda_real"], (r.real[-1] < r.investido_real[-1]).mean())


# ---------------------------------------------------------------- estatísticos

def _dentro(observado, esperado, erro_padrao, k=4.0):
    assert abs(observado - esperado) <= k * erro_padrao, (observado, esperado, erro_padrao)


def teste_S1_probabilidade_anual_de_crise():
    p = SEM_RISCO.com(p_crise=0.10, ano_alvo=2031, n_cenarios=20000)
    r = simular(p)
    q = (1 - 0.10) ** p.anos  # P(nenhuma crise em 5 anos)
    _dentro((r.crises == 0).mean(), q, np.sqrt(q * (1 - q) / p.n_cenarios))
    assert np.isclose(1 - (1 - prob_mensal(0.10)) ** 12, 0.10)


def teste_S2_mediana_lognormal_e_t():
    for dist in ("normal", "t"):
        p = SEM_RISCO.com(vol_acoes=0.16, retorno_acoes=0.07, aporte=0, n_cenarios=20000, distribuicao=dist)
        r = simular(p)
        alvo = p.capital_inicial * 1.07 ** p.anos
        lo, hi = ic_mediana(r.nominal[-1], confianca_z=4)
        assert lo <= alvo <= hi, (dist, lo, alvo, hi)


def teste_S3_choques_padronizados_e_correlacionados():
    for dist, nu in (("normal", 5), ("t", 4), ("t", 8)):
        p = Parametros(distribuicao=dist, graus_liberdade=nu, correlacao=0.6)
        z1, z2 = _choques(np.random.default_rng(7), 400_000, p)
        tol = 0.02 if dist == "normal" else 0.04
        assert abs(z1.var() - 1) < tol and abs(z2.var() - 1) < tol, (dist, z1.var(), z2.var())
        assert abs(np.corrcoef(z1, z2)[0, 1] - 0.6) < 0.01
        curt = np.mean(z1 ** 4) / z1.var() ** 2
        assert (abs(curt - 3) < 0.05) if dist == "normal" else curt > 3.3, (dist, curt)


def teste_S4_volatilidade_anual():
    p = SEM_RISCO.com(vol_acoes=0.20, aporte=0, n_cenarios=20000, ano_alvo=2027)
    r = simular(p)
    lr = np.log(r.nominal[1] / r.nominal[0])
    _dentro(lr.std(), 0.20, 0.20 / np.sqrt(2 * p.n_cenarios))


def teste_S5_rentabilidade_efetiva_implicita():
    """A taxa 'efetiva' publicada é exp(E[log crescimento anual]) − 1: confirma-se pela média
    simulada do logaritmo do crescimento (não pela mediana, que depende do nº de crises)."""
    for peso, chave in ((0.0, "acoes"), (1.0, "cripto")):
        p = Parametros(peso_cripto=peso, aporte=0, n_cenarios=20000, ano_alvo=2066)
        r = simular(p)
        lg = np.log(r.nominal[-1] / p.capital_inicial) / p.anos
        alvo = np.log(1 + rentabilidade_implicita(p)[chave]["efetiva"])
        _dentro(lg.mean(), alvo, lg.std() / np.sqrt(p.n_cenarios))


# ---------------------------------------------------------------- Python vs JavaScript

def _resumo_js(params: dict) -> dict:
    saida = subprocess.run(["node", str(RAIZ / "scripts" / "testes_web.js"), "--resumo", json.dumps(params)],
                           capture_output=True, text=True, check=True, timeout=300)
    return json.loads(saida.stdout)


def teste_X1_motores_python_e_javascript_coincidem():
    """Os dois motores implementam o mesmo modelo: com 50 000 cenários cada, as diferenças têm de
    caber no erro de Monte Carlo (os geradores aleatórios são diferentes)."""
    if shutil.which("node") is None:
        print("         (node não encontrado: comparação saltada)")
        return
    for extra in ({}, {"distribuicao": "t", "graus_liberdade": 4},
                  {k: v for k, v in CENARIOS["Pessimista"].como_dict().items() if k not in ("n_cenarios", "semente")}):
        p = Parametros(**{**Parametros().como_dict(), **extra, "n_cenarios": 50000})
        py, js = resumir(simular(p)), _resumo_js({**extra, "n_cenarios": 50000})
        assert np.isclose(py["deterministico"], js["deterministico"], rtol=1e-12)
        se = lambda s: (s["ic95_mediana_real"][1] - s["ic95_mediana_real"][0]) / (2 * 1.96)
        _dentro(js["mediana_real"], py["mediana_real"], np.hypot(se(py), se(js)))
        for k in ("prob_objetivo", "prob_perda_nominal", "prob_perda_real", "prob_crise"):
            q = py[k]
            _dentro(js[k], q, max(np.sqrt(2 * q * (1 - q) / 50000), 1e-4))
        for k, tol in (("drawdown_mediano", 0.01), ("var95_anual", 0.005), ("investido_medio", 0.002)):
            assert abs(js[k] - py[k]) <= tol * max(1, abs(py[k])), (k, py[k], js[k])
        assert abs(js["tir_real"]["50"] - py["tir_real"][50]) < 0.002, (py["tir_real"], js["tir_real"])


# ---------------------------------------------------------------- validação

def teste_V1_entradas_invalidas_sao_rejeitadas():
    for errado in (dict(correlacao=1.2), dict(peso_cripto=1.5), dict(queda_crise_acoes=1.0),
                   dict(ano_alvo=2026), dict(aporte=-1), dict(distribuicao="t", graus_liberdade=2),
                   dict(frequencia="diaria"), dict(p_crise=-0.1)):
        try:
            Parametros(**errado)
        except ValueError:
            continue
        raise AssertionError(f"aceitou {errado}")


def main() -> int:
    testes = [(n, f) for n, f in globals().items() if n.startswith("teste_") and callable(f)]
    falhas = 0
    for nome, f in testes:
        try:
            f()
            print(f"  ok     {nome}")
        except Exception as e:  # noqa: BLE001 — um erro inesperado também é uma falha
            falhas += 1
            print(f"  FALHOU {nome}: {type(e).__name__}: {e}")
    print(f"\n{len(testes) - falhas}/{len(testes)} testes passaram.")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
