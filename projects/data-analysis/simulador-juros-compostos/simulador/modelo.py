"""
Modelo Monte Carlo de um plano de investimento com aportes periódicos.

Cada cenário é simulado mês a mês (o mesmo algoritmo de web/js/modelo.js):

  Início de cada ano
    1. sorteia a inflação do ano (normal + possível choque) e a eventual pausa de 6 meses nos aportes;
    2. calcula o aporte-base do ano: aporte × (1 + crescimento)^ano (× índice de preços, se indexado).
  Cada mês
    3. entra o aporte no INÍCIO do mês (semanal = 52/12 por mês; anual = só em janeiro);
    4. ações e cripto rendem um retorno logarítmico normal ou Student-t, correlacionado;
    5. eventos exógenos: crise de mercado (queda nas duas classes) e regulação adversa (só cripto);
    6. custos de gestão: fator (1 − custo anual)^(1/12);
    7. atualiza o índice de preços e o valor da unidade de participação (para o drawdown).
  Fim de cada ano
    8. rebalanceamento opcional para a alocação alvo.

Convenções (ver METODOLOGIA.md):
  • "retorno_*" é a rentabilidade anual MEDIANA (= geométrica) antes de choques e custos;
  • as probabilidades de eventos são ANUAIS e convertidas em mensais com 1 − (1 − p)^(1/12);
  • valores reais = nominais ÷ índice de preços do próprio cenário;
  • o capital investido real deflaciona cada aporte pelo índice de preços do mês em que é feito.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, replace

import numpy as np

ANO_INICIAL = 2026
ANO_MAXIMO = 2086
MESES_PAUSA = 6
INFLACAO_MINIMA = -0.05
N_PERMITIDOS = (2000, 10000, 50000)
PERCENTIS = (5, 10, 25, 50, 75, 90, 95)


@dataclass(frozen=True)
class Parametros:
    # Plano
    capital_inicial: float = 2000.0
    ano_alvo: int = 2046
    aporte: float = 200.0
    frequencia: str = "mensal"          # "semanal" | "mensal" | "anual"
    crescimento_aporte: float = 0.02
    indexar_inflacao: bool = False
    peso_cripto: float = 0.20
    rebalancear: bool = True
    objetivo_real: float = 100_000.0

    # Mercados (anuais)
    retorno_acoes: float = 0.07         # mediana geométrica
    vol_acoes: float = 0.16
    retorno_cripto: float = 0.15
    vol_cripto: float = 0.65
    correlacao: float = 0.35
    custos: float = 0.0025
    distribuicao: str = "normal"        # "normal" (log-normal) | "t" (Student-t)
    graus_liberdade: int = 5

    # Inflação
    inflacao: float = 0.022
    vol_inflacao: float = 0.01

    # Eventos exógenos (probabilidade anual + impacto)
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

    def __post_init__(self):
        erros = validar(self)
        if erros:
            raise ValueError("Parâmetros inválidos: " + "; ".join(erros))

    @property
    def anos(self) -> int:
        return self.ano_alvo - ANO_INICIAL

    def com(self, **alteracoes) -> "Parametros":
        return replace(self, **alteracoes)

    def como_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}


def validar(p: Parametros) -> list[str]:
    """Lista de erros (vazia se tudo estiver certo). Mesmas regras que validar() em modelo.js."""
    e = []
    def intervalo(nome, v, lo, hi):
        if not (lo <= v <= hi):
            e.append(f"{nome} tem de estar entre {lo} e {hi} (recebido {v})")
    intervalo("ano_alvo", p.ano_alvo, ANO_INICIAL + 1, ANO_MAXIMO)
    intervalo("capital_inicial", p.capital_inicial, 0, 1e9)
    intervalo("aporte", p.aporte, 0, 1e8)
    intervalo("crescimento_aporte", p.crescimento_aporte, -0.5, 0.5)
    intervalo("peso_cripto", p.peso_cripto, 0, 1)
    intervalo("retorno_acoes", p.retorno_acoes, -0.5, 1)
    intervalo("retorno_cripto", p.retorno_cripto, -0.9, 3)
    intervalo("vol_acoes", p.vol_acoes, 0, 1.5)
    intervalo("vol_cripto", p.vol_cripto, 0, 3)
    intervalo("correlacao", p.correlacao, -1, 1)
    intervalo("custos", p.custos, 0, 0.05)
    intervalo("inflacao", p.inflacao, -0.05, 0.5)
    intervalo("vol_inflacao", p.vol_inflacao, 0, 0.2)
    for nome in ("p_crise", "p_regulacao", "p_choque_inflacao", "p_pausa"):
        intervalo(nome, getattr(p, nome), 0, 1)
    for nome in ("queda_crise_acoes", "queda_crise_cripto", "queda_regulacao"):
        intervalo(nome, getattr(p, nome), 0, 0.95)
    intervalo("choque_inflacao", p.choque_inflacao, 0, 0.5)
    intervalo("objetivo_real", p.objetivo_real, 0, 1e10)
    if p.frequencia not in ("semanal", "mensal", "anual"):
        e.append(f"frequencia desconhecida: {p.frequencia!r}")
    if p.distribuicao not in ("normal", "t"):
        e.append(f"distribuicao desconhecida: {p.distribuicao!r}")
    if p.distribuicao == "t":
        intervalo("graus_liberdade", p.graus_liberdade, 3, 30)
    if p.n_cenarios < 1:
        e.append("n_cenarios tem de ser positivo")
    return e


def prob_mensal(p_anual: float) -> float:
    """Probabilidade mensal que dá exatamente p_anual de pelo menos um evento em 12 meses."""
    return 1 - (1 - p_anual) ** (1 / 12)


def aporte_do_mes(base, frequencia: str, mes: int):
    if frequencia == "semanal":
        return base * 52 / 12
    if frequencia == "mensal":
        return base
    if frequencia == "anual":
        return base if mes == 0 else base * 0.0
    raise ValueError(f"Frequência desconhecida: {frequencia!r}")


def taxa_classica(p: Parametros) -> float:
    """Taxa anual da 'calculadora clássica': média ponderada das rentabilidades, líquida de custos."""
    bruta = (1 - p.peso_cripto) * p.retorno_acoes + p.peso_cripto * p.retorno_cripto
    return (1 + bruta) * (1 - p.custos) - 1


def valor_deterministico(p: Parametros) -> np.ndarray:
    """Calculadora clássica: uma só taxa constante, sem volatilidade, choques nem pausas.

    Usa exatamente o mesmo calendário de aportes e a mesma aplicação de custos do modelo
    estocástico, por isso coincide com ele quando a volatilidade e os choques são zero e a
    carteira tem um só ativo (teste A)."""
    fator = (1 + taxa_classica(p)) ** (1 / 12)
    valor, serie = p.capital_inicial, [p.capital_inicial]
    for ano in range(p.anos):
        base = p.aporte * (1 + p.crescimento_aporte) ** ano
        if p.indexar_inflacao:
            base *= (1 + p.inflacao) ** ano
        for mes in range(12):
            valor = (valor + aporte_do_mes(base, p.frequencia, mes)) * fator
        serie.append(valor)
    return np.array(serie)


@dataclass
class Resultado:
    parametros: Parametros
    anos: np.ndarray
    nominal: np.ndarray              # (anos+1, N) valor da carteira no fim de cada ano
    real: np.ndarray                 # idem, em € de hoje
    investido: np.ndarray            # (anos+1, N) aportes acumulados (nominais)
    investido_real: np.ndarray       # (anos+1, N) aportes acumulados, cada um em € de hoje
    precos: np.ndarray               # (anos+1, N) índice de preços (1 = hoje)
    drawdown_max: np.ndarray         # (N,) maior queda da unidade de participação
    retornos_anuais: np.ndarray      # (anos, N) rentabilidade anual da carteira (ponderada no tempo)
    crises: np.ndarray               # (N,) nº de crises
    aportes_mensais: np.ndarray      # (meses,) aporte médio em cada mês (nominal), mês 0 inclui o capital
    aportes_mensais_reais: np.ndarray
    deterministico: np.ndarray = field(default_factory=lambda: np.array([]))

    def percentis(self, real: bool = False, q=(10, 25, 50, 75, 90)) -> np.ndarray:
        return np.percentile(self.real if real else self.nominal, q, axis=1)

    def resumo_final(self) -> dict:
        from .risco import resumir
        return resumir(self)


def _choques(rng, n, p: Parametros):
    """Dois choques padronizados (variância 1) correlacionados: normais ou Student-t multivariada."""
    z1 = rng.standard_normal(n)
    z2 = p.correlacao * z1 + np.sqrt(1 - p.correlacao ** 2) * rng.standard_normal(n)
    if p.distribuicao == "t":
        nu = p.graus_liberdade
        w = rng.chisquare(nu, n)
        escala = np.sqrt((nu - 2) / w)  # mesmo fator nos dois ativos → dependência nas caudas
        z1, z2 = z1 * escala, z2 * escala
    return z1, z2


def simular(p: Parametros) -> Resultado:
    rng = np.random.default_rng(p.semente)
    n, anos, meses = p.n_cenarios, p.anos, p.anos * 12
    w_c = p.peso_cripto
    w_a = 1 - w_c

    mu_a, s_a = np.log(1 + p.retorno_acoes) / 12, p.vol_acoes / np.sqrt(12)
    mu_c, s_c = np.log(1 + p.retorno_cripto) / 12, p.vol_cripto / np.sqrt(12)
    pm_crise, pm_reg = prob_mensal(p.p_crise), prob_mensal(p.p_regulacao)
    fator_custos = (1 - p.custos) ** (1 / 12)

    cap = float(p.capital_inicial)
    acoes = np.full(n, cap * w_a)
    cripto = np.full(n, cap * w_c)
    precos = np.ones(n)
    pago = np.full(n, cap)
    pago_real = np.full(n, cap)
    pausa = np.zeros(n, dtype=int)
    crises = np.zeros(n, dtype=int)
    unidade = np.ones(n)
    pico = np.ones(n)
    dd_max = np.zeros(n)

    forma = (anos + 1, n)
    nominal, real, investido, investido_real, idx_precos = (np.empty(forma) for _ in range(5))
    nominal[0] = real[0] = investido[0] = investido_real[0] = p.capital_inicial
    idx_precos[0] = 1.0
    retornos_anuais = np.empty((anos, n))
    aportes_m = np.zeros(max(meses, 1))
    aportes_m_reais = np.zeros(max(meses, 1))

    for ano in range(anos):
        inf = p.inflacao + p.vol_inflacao * rng.standard_normal(n)
        inf = inf + np.where(rng.random(n) < p.p_choque_inflacao, p.choque_inflacao, 0.0)
        fator_inf = (1 + np.maximum(inf, INFLACAO_MINIMA)) ** (1 / 12)
        pausa += np.where(rng.random(n) < p.p_pausa, MESES_PAUSA, 0)

        base = float(p.aporte) * (1 + p.crescimento_aporte) ** ano
        base = base * precos if p.indexar_inflacao else np.full(n, base)
        unidade_inicio = unidade.copy()

        for mes in range(12):
            t = ano * 12 + mes
            a = aporte_do_mes(base, p.frequencia, mes) * (pausa == 0)
            pausa = np.maximum(pausa - 1, 0)
            acoes += a * w_a
            cripto += a * w_c
            pago += a
            pago_real += a / precos
            aportes_m[t] += a.mean()
            aportes_m_reais[t] += (a / precos).mean()
            antes = acoes + cripto

            z1, z2 = _choques(rng, n, p)
            acoes *= np.exp(mu_a + s_a * z1)
            cripto *= np.exp(mu_c + s_c * z2)

            crise = rng.random(n) < pm_crise
            acoes *= np.where(crise, 1 - p.queda_crise_acoes, 1.0)
            cripto *= np.where(crise, 1 - p.queda_crise_cripto, 1.0)
            crises += crise
            cripto *= np.where(rng.random(n) < pm_reg, 1 - p.queda_regulacao, 1.0)

            acoes *= fator_custos
            cripto *= fator_custos
            precos *= fator_inf

            depois = acoes + cripto
            unidade *= np.divide(depois, antes, out=np.ones(n), where=antes > 0)
            pico = np.maximum(pico, unidade)
            dd_max = np.maximum(dd_max, 1 - unidade / pico)

        if p.rebalancear:
            total = acoes + cripto
            acoes, cripto = total * w_a, total * w_c

        retornos_anuais[ano] = unidade / unidade_inicio - 1
        nominal[ano + 1] = acoes + cripto
        real[ano + 1] = (acoes + cripto) / precos
        investido[ano + 1] = pago
        investido_real[ano + 1] = pago_real
        idx_precos[ano + 1] = precos

    aportes_m[0] += p.capital_inicial
    aportes_m_reais[0] += p.capital_inicial

    return Resultado(
        parametros=p,
        anos=np.arange(ANO_INICIAL, p.ano_alvo + 1),
        nominal=nominal, real=real, investido=investido, investido_real=investido_real,
        precos=idx_precos, drawdown_max=dd_max, retornos_anuais=retornos_anuais, crises=crises,
        aportes_mensais=aportes_m, aportes_mensais_reais=aportes_m_reais,
        deterministico=valor_deterministico(p),
    )


def rentabilidade_implicita(p: Parametros) -> dict:
    """Rentabilidades anuais implícitas nos pressupostos, por classe de ativo.

    mediana       — o valor introduzido (geométrica, antes de choques e custos);
    media_aritm   — média aritmética anual antes de choques (só existe para a log-normal);
    efetiva       — rentabilidade geométrica esperada depois de crises, regulação e custos.
    """
    out = {}
    for nome, r, s, quedas in (
        ("acoes", p.retorno_acoes, p.vol_acoes, [(p.p_crise, p.queda_crise_acoes)]),
        ("cripto", p.retorno_cripto, p.vol_cripto, [(p.p_crise, p.queda_crise_cripto), (p.p_regulacao, p.queda_regulacao)]),
    ):
        log_g = np.log(1 + r) + np.log(1 - p.custos)
        for prob, queda in quedas:
            log_g += 12 * prob_mensal(prob) * np.log(1 - queda)
        out[nome] = {
            "mediana": r,
            "media_aritm": (1 + r) * np.exp(s ** 2 / 2) - 1 if p.distribuicao == "normal" else None,
            "efetiva": float(np.exp(log_g) - 1),
        }
    return out
