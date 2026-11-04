"""
Indicadores de resultado e de risco calculados a partir de uma simulação.

Regras de base monetária:
  • comparações nominais usam valores nominais dos dois lados (final vs investido);
  • comparações reais usam € de hoje dos dois lados (final ÷ índice vs aportes ÷ índice no mês do aporte);
  • ganhos e rentabilidades são calculados POR CENÁRIO e só depois resumidos (mediana/percentis).
"""

from __future__ import annotations

import numpy as np


def tir_anual(aportes_mensais: np.ndarray, valor_final: float) -> float | None:
    """Taxa interna de rentabilidade anualizada (ponderada pelo dinheiro).

    aportes_mensais[t] entra no início do mês t; valor_final é medido no fim do último mês.
    Resolve Σ a_t (1+r)^(T−t) = valor_final por bisseção (a função é monótona em r)."""
    a = np.asarray(aportes_mensais, dtype=float)
    T = len(a)
    if a.sum() <= 0 or valor_final <= 0:
        return None
    exp = T - np.arange(T)

    def vf(r):
        return float(np.sum(a * (1 + r) ** exp))

    lo, hi = -0.99, 1.0
    if vf(lo) > valor_final or vf(hi) < valor_final:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if vf(mid) < valor_final:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13:
            break
    return (1 + (lo + hi) / 2) ** 12 - 1


def ic_mediana(x: np.ndarray, confianca_z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de 95% (sem pressupostos de distribuição) para a mediana,
    pelas estatísticas de ordem: índices n/2 ± z·√n/2."""
    s = np.sort(x)
    n = len(s)
    k = confianca_z * np.sqrt(n) / 2
    lo = int(max(0, np.floor(n / 2 - k)))
    hi = int(min(n - 1, np.ceil(n / 2 + k)))
    return float(s[lo]), float(s[hi])


def var_cvar(x: np.ndarray, nivel: float = 0.05) -> tuple[float, float]:
    """Percentil `nivel` de x e média dos valores ≤ esse percentil (Expected Shortfall)."""
    q = float(np.percentile(x, nivel * 100))
    cauda = x[x <= q]
    return q, float(cauda.mean()) if len(cauda) else q


def resumir(r) -> dict:
    p = r.parametros
    nom, real = r.nominal[-1], r.real[-1]
    inv, inv_real = r.investido[-1], r.investido_real[-1]
    n = len(nom)
    pct = lambda x, q: float(np.percentile(x, q))
    with np.errstate(divide="ignore", invalid="ignore"):
        rent_acum = np.where(inv > 0, nom / inv - 1, np.nan)

    p_obj = float((real >= p.objetivo_real).mean())
    var95, cvar95 = var_cvar(r.retornos_anuais.ravel(), 0.05) if r.retornos_anuais.size else (np.nan, np.nan)
    p5_real, cvar5_real = var_cvar(real, 0.05)
    med_lo, med_hi = ic_mediana(nom)
    real_lo, real_hi = ic_mediana(real)

    tir = {q: tir_anual(r.aportes_mensais, pct(nom, q)) for q in (10, 50, 90)}
    tir_real = {q: tir_anual(r.aportes_mensais_reais, pct(real, q)) for q in (10, 50, 90)}

    return {
        "n": n,
        "mediana_nominal": pct(nom, 50),
        "mediana_real": pct(real, 50),
        "media_real": float(real.mean()),
        "p10_real": pct(real, 10), "p25_real": pct(real, 25), "p75_real": pct(real, 75), "p90_real": pct(real, 90),
        "p10_nominal": pct(nom, 10), "p90_nominal": pct(nom, 90),
        "investido_medio": float(inv.mean()),
        "investido_real_medio": float(inv_real.mean()),
        "ganho_nominal_mediano": pct(nom - inv, 50),
        "ganho_real_mediano": pct(real - inv_real, 50),
        "rentab_acumulada_mediana": float(np.nanmedian(rent_acum)) if np.isfinite(rent_acum).any() else None,
        "tir_nominal": tir, "tir_real": tir_real,
        "prob_objetivo": p_obj,
        "erro_prob_objetivo": float(np.sqrt(p_obj * (1 - p_obj) / n)),
        "prob_perda_nominal": float((nom < inv).mean()),
        "prob_perda_real": float((real < inv_real).mean()),
        "ic95_mediana_nominal": (med_lo, med_hi),
        "ic95_mediana_real": (real_lo, real_hi),
        "drawdown_mediano": pct(r.drawdown_max, 50),
        "drawdown_p90": pct(r.drawdown_max, 90),
        "var95_anual": var95, "cvar95_anual": cvar95,
        "p5_real": p5_real, "cvar5_real": cvar5_real,
        "prob_crise": float((r.crises > 0).mean()),
        "deterministico": float(r.deterministico[-1]),
    }
