"""
Modelo Monte Carlo de um plano de investimento com aportes periódicos.

Cada cenário é simulado mês a mês:
  1. entra o aporte do mês (semanal = 52/12 por mês; anual = só em janeiro);
  2. ações e cripto valorizam com retornos log-normais correlacionados;
  3. podem ocorrer choques exógenos (crise de mercado, regulação cripto);
  4. descontam-se os custos (TER) e atualiza-se o índice de preços.
No fim de cada ano a carteira pode ser rebalanceada para a alocação alvo.

O "retorno" introduzido é o crescimento anual MEDIANO de cada ativo antes
dos choques, por isso, sem volatilidade nem choques, o modelo reduz-se à
fórmula clássica de juros compostos (ver valor_deterministico e testes.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np

ANO_INICIAL = 2026
MESES_PAUSA = 6  # duração de uma interrupção de aportes


@dataclass(frozen=True)
class Parametros:
    # Plano
    capital_inicial: float = 2000.0
    ano_alvo: int = 2046
    aporte: float = 200.0
    frequencia: str = "mensal"          # "semanal" | "mensal" | "anual"
    crescimento_aporte: float = 0.02    # aumento anual do aporte
    indexar_inflacao: bool = False      # aporte acompanha a inflação simulada
    peso_cripto: float = 0.20
    rebalancear: bool = True
    objetivo_real: float = 100_000.0    # objetivo em € de hoje

    # Mercados (valores anuais)
    retorno_acoes: float = 0.07
    vol_acoes: float = 0.16
    retorno_cripto: float = 0.15
    vol_cripto: float = 0.65
    correlacao: float = 0.35
    custos: float = 0.0025

    # Inflação
    inflacao: float = 0.022
    vol_inflacao: float = 0.01

    # Fatores exógenos (probabilidade anual + impacto)
    p_crise: float = 0.06
    queda_crise_acoes: float = 0.25
    queda_crise_cripto: float = 0.50
    p_regulacao: float = 0.03
    queda_regulacao: float = 0.40
    p_choque_inflacao: float = 0.05
    choque_inflacao: float = 0.05
    p_pausa: float = 0.05

    # Simulação
    n_cenarios: int = 2000
    semente: int = 20261103

    @property
    def anos(self) -> int:
        return self.ano_alvo - ANO_INICIAL

    def com(self, **alteracoes) -> "Parametros":
        return replace(self, **alteracoes)


@dataclass
class Resultado:
    parametros: Parametros
    anos: np.ndarray                 # 2026 … ano alvo
    nominal: np.ndarray              # (anos+1, cenários)
    real: np.ndarray                 # idem, em € de hoje
    investido: np.ndarray            # (anos+1, cenários) total aportado
    crises: np.ndarray               # nº de crises de mercado por cenário
    deterministico: np.ndarray = field(default_factory=lambda: np.array([]))

    def percentis(self, real: bool = False, q=(10, 25, 50, 75, 90)) -> np.ndarray:
        """Matriz (len(q), anos+1) com os percentis pedidos."""
        return np.percentile(self.real if real else self.nominal, q, axis=1)

    def resumo_final(self) -> dict:
        p = self.parametros
        nom, real, inv = self.nominal[-1], self.real[-1], self.investido[-1]
        return {
            "investido_medio": float(inv.mean()),
            "p10": float(np.percentile(nom, 10)),
            "mediana": float(np.median(nom)),
            "p90": float(np.percentile(nom, 90)),
            "mediana_real": float(np.median(real)),
            "prob_objetivo": float((real >= p.objetivo_real).mean()),
            "prob_ganho": float((nom >= inv).mean()),
            "prob_bater_inflacao": float((real >= inv / (1 + p.inflacao) ** p.anos).mean()),
            "prob_crise": float((self.crises > 0).mean()),
            "deterministico": float(self.deterministico[-1]),
        }


def aporte_do_mes(base, frequencia: str, mes: int):
    """Valor aportado num mês (0 = janeiro) dado o aporte-base do período."""
    if frequencia == "semanal":
        return base * 52 / 12
    if frequencia == "mensal":
        return base
    if frequencia == "anual":
        return base if mes == 0 else 0.0 * base
    raise ValueError(f"Frequência desconhecida: {frequencia!r}")


def valor_deterministico(p: Parametros) -> np.ndarray:
    """A 'calculadora clássica': retorno médio ponderado, sem volatilidade nem choques."""
    taxa = (1 - p.peso_cripto) * p.retorno_acoes + p.peso_cripto * p.retorno_cripto - p.custos
    fator = (1 + taxa) ** (1 / 12)
    valor, serie = p.capital_inicial, [p.capital_inicial]
    for ano in range(p.anos):
        base = p.aporte * (1 + p.crescimento_aporte) ** ano
        if p.indexar_inflacao:
            base *= (1 + p.inflacao) ** ano
        for mes in range(12):
            valor = (valor + aporte_do_mes(base, p.frequencia, mes)) * fator
        serie.append(valor)
    return np.array(serie)


def simular(p: Parametros) -> Resultado:
    if p.anos < 1:
        raise ValueError("O ano alvo tem de ser posterior a %d." % ANO_INICIAL)
    rng = np.random.default_rng(p.semente)
    n, anos = p.n_cenarios, p.anos
    w_c = p.peso_cripto
    w_a = 1 - w_c

    mu_a, s_a = np.log(1 + p.retorno_acoes) / 12, p.vol_acoes / np.sqrt(12)
    mu_c, s_c = np.log(max(0.01, 1 + p.retorno_cripto)) / 12, p.vol_cripto / np.sqrt(12)
    rho_comp = np.sqrt(1 - p.correlacao ** 2)

    acoes = np.full(n, p.capital_inicial * w_a)
    cripto = np.full(n, p.capital_inicial * w_c)
    precos = np.ones(n)
    pago = np.full(n, p.capital_inicial)
    pausa = np.zeros(n, dtype=int)
    crises = np.zeros(n, dtype=int)

    nominal = np.empty((anos + 1, n))
    real = np.empty((anos + 1, n))
    investido = np.empty((anos + 1, n))
    nominal[0] = real[0] = investido[0] = p.capital_inicial

    for ano in range(anos):
        # Inflação do ano (com possível choque) e possível pausa nos aportes
        inf = p.inflacao + p.vol_inflacao * rng.standard_normal(n)
        inf += np.where(rng.random(n) < p.p_choque_inflacao, p.choque_inflacao, 0.0)
        fator_inf = (1 + np.maximum(inf, -0.05)) ** (1 / 12)
        pausa += np.where(rng.random(n) < p.p_pausa, MESES_PAUSA, 0)

        base = p.aporte * (1 + p.crescimento_aporte) ** ano
        base = base * precos if p.indexar_inflacao else np.full(n, base)

        for mes in range(12):
            a = aporte_do_mes(base, p.frequencia, mes) * (pausa == 0)
            pausa = np.maximum(pausa - 1, 0)
            acoes += a * w_a
            cripto += a * w_c
            pago += a

            z1 = rng.standard_normal(n)
            z2 = p.correlacao * z1 + rho_comp * rng.standard_normal(n)
            acoes *= np.exp(mu_a + s_a * z1)
            cripto *= np.exp(mu_c + s_c * z2)

            crise = rng.random(n) < p.p_crise / 12
            acoes *= np.where(crise, 1 - p.queda_crise_acoes, 1.0)
            cripto *= np.where(crise, 1 - p.queda_crise_cripto, 1.0)
            crises += crise
            cripto *= np.where(rng.random(n) < p.p_regulacao / 12, 1 - p.queda_regulacao, 1.0)

            acoes *= 1 - p.custos / 12
            cripto *= 1 - p.custos / 12
            precos *= fator_inf

        if p.rebalancear:
            total = acoes + cripto
            acoes, cripto = total * w_a, total * w_c

        nominal[ano + 1] = acoes + cripto
        real[ano + 1] = (acoes + cripto) / precos
        investido[ano + 1] = pago

    return Resultado(
        parametros=p,
        anos=np.arange(ANO_INICIAL, p.ano_alvo + 1),
        nominal=nominal,
        real=real,
        investido=investido,
        crises=crises,
        deterministico=valor_deterministico(p),
    )
