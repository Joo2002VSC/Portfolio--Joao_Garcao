"""Cenários prontos: os mesmos quatro da versão web (web/index.html)."""

from .modelo import Parametros

BASE = Parametros()

CENARIOS: dict[str, Parametros] = {
    "Base": BASE,
    "Pessimista": BASE.com(
        retorno_acoes=0.045, vol_acoes=0.18, retorno_cripto=0.05, vol_cripto=0.75, correlacao=0.5,
        inflacao=0.03, vol_inflacao=0.015, p_crise=0.10, queda_crise_acoes=0.35, queda_crise_cripto=0.65,
        p_regulacao=0.06, queda_regulacao=0.50, p_choque_inflacao=0.08, choque_inflacao=0.06, p_pausa=0.08,
    ),
    "Otimista": BASE.com(
        retorno_acoes=0.09, vol_acoes=0.15, retorno_cripto=0.25, vol_cripto=0.60, correlacao=0.3,
        inflacao=0.02, vol_inflacao=0.007, p_crise=0.04, queda_crise_acoes=0.20, queda_crise_cripto=0.40,
        p_regulacao=0.01, queda_regulacao=0.30, p_choque_inflacao=0.03, choque_inflacao=0.04, p_pausa=0.03,
    ),
    "Estagflação": BASE.com(
        retorno_acoes=0.03, vol_acoes=0.19, retorno_cripto=0.04, vol_cripto=0.70, correlacao=0.45,
        inflacao=0.05, vol_inflacao=0.02, p_crise=0.09, queda_crise_acoes=0.30, queda_crise_cripto=0.55,
        p_regulacao=0.04, queda_regulacao=0.40, p_choque_inflacao=0.15, choque_inflacao=0.07, p_pausa=0.10,
    ),
}
