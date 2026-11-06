"""Qualidade dos dados: verificações do texto e da anotação, e estado de cada indicador.

Estados de um indicador (guardados em `estados` no JSON; um indicador sem estado é válido):
  * «nao_aplicavel»: a métrica não se aplica (texto curto de mais, língua não suportada pela fórmula);
  * «desconhecido»: não foi possível determinar o valor (por exemplo, sem frases segmentadas);
  * «falha»: o cálculo produziu um valor inválido (NaN, infinito) ou uma exceção.
Um zero só é registado quando é um zero real. Valores em falta ficam `null`, nunca 0.
"""
from __future__ import annotations

import math
import re
from collections import Counter

NAO_APLICAVEL, DESCONHECIDO, FALHA = "nao_aplicavel", "desconhecido", "falha"
ROTULOS = {NAO_APLICAVEL: "não aplicável", DESCONHECIDO: "desconhecido", FALHA: "falha de processamento"}

# sequências típicas de UTF-8 lido como Latin-1/Windows-1252 («Ã©», «â€™») e o carácter de substituição
MOJIBAKE = re.compile(r"Ã[\x80-\xbf¡-ÿ]|â€[\x80-\xbf™œ“”˜]|�")


def aviso(nivel: str, codigo: str, mensagem: str) -> dict:
    return {"nivel": nivel, "codigo": codigo, "mensagem": mensagem}


def verificar_texto(paragrafos: list[str], pontuacao_lingua: dict[str, float], lingua: str,
                    lingua_declarada: str | None, minimo_texto: int) -> list[dict]:
    avisos = []
    texto = "\n".join(paragrafos)
    palavras = len(re.findall(r"[^\W\d_]+", texto))
    if palavras == 0:
        return [aviso("erro", "texto_vazio", "O texto não contém palavras: verificar a extração do ficheiro.")]
    if palavras < minimo_texto:
        avisos.append(aviso("aviso", "texto_curto", f"Texto curto ({palavras} palavras, menos de {minimo_texto}): os "
                                                    "indicadores agregados são instáveis."))
    estranhos = len(MOJIBAKE.findall(texto))
    if estranhos / max(palavras, 1) > 0.001:
        avisos.append(aviso("aviso", "codificacao", f"{estranhos} sequências típicas de erro de codificação "
                                                    "(«Ã©», «â€™», «�»): o ficheiro pode ter sido lido com a codificação "
                                                    "errada."))
    longos = [p for p in paragrafos if len(p) >= 80]
    if longos:
        repetidos = sum(n - 1 for n in Counter(longos).values() if n > 1)
        if repetidos / len(longos) > 0.02:
            avisos.append(aviso("aviso", "duplicacao", f"{repetidos} parágrafos repetidos ({100 * repetidos / len(longos):.1f} "
                                                       "% dos parágrafos com mais de 80 caracteres): possível conteúdo "
                                                       "duplicado na extração.".replace(".", ",", 1)))
    ordem = sorted(pontuacao_lingua.values(), reverse=True)
    if len(ordem) > 1 and ordem[0] - ordem[1] < 0.03:
        avisos.append(aviso("aviso", "lingua_incerta", "A deteção de língua tem uma margem pequena entre as duas línguas "
                                                       "mais prováveis; confirmar ou forçar a língua em metadados.csv."))
    declaradas = {"portuguese": "pt", "português": "pt", "pt": "pt", "french": "fr", "français": "fr", "fr": "fr",
                  "english": "en", "inglês": "en", "en": "en"}
    if lingua_declarada:
        d = declaradas.get(lingua_declarada.strip().lower().split("-")[0])
        if d and d != lingua:
            avisos.append(aviso("aviso", "lingua_divergente", f"A língua declarada nos metadados ({lingua_declarada}) "
                                                              f"difere da detetada ({lingua})."))
        elif not d:
            avisos.append(aviso("aviso", "lingua_nao_suportada", f"Língua declarada «{lingua_declarada}» não suportada; "
                                                                 f"o texto foi analisado como «{lingua}»."))
    return avisos


def verificar_anotacao(n_frases: int, comprimentos, n_palavras: int) -> list[dict]:
    avisos = []
    if n_frases == 0:
        return [aviso("erro", "sem_frases", "O analisador não segmentou nenhuma frase.")]
    muito_longas = int((comprimentos > 150).sum())
    if muito_longas and muito_longas / n_frases > 0.005:
        avisos.append(aviso("aviso", "segmentacao", f"{muito_longas} frases com mais de 150 palavras: provável falha "
                                                    "na segmentação de frases (pontuação invulgar ou texto sem "
                                                    "pontuação final)."))
    if n_palavras / n_frases > 60:
        avisos.append(aviso("aviso", "segmentacao_media", "Média superior a 60 palavras por frase: verificar a "
                                                          "segmentação."))
    return avisos


def aplicabilidade(n_palavras: int, lingua: str, p) -> dict[str, dict]:
    """Indicadores que não se aplicam a este texto, com o motivo."""
    e = {}
    if n_palavras < p.janela_mattr:
        e["mattr"] = {"estado": NAO_APLICAVEL, "motivo": f"texto com menos de {p.janela_mattr} palavras (janela do MATTR)"}
    if n_palavras < p.minimo_mtld:
        e["mtld"] = {"estado": NAO_APLICAVEL, "motivo": f"texto com menos de {p.minimo_mtld} palavras"}
    if n_palavras < p.amostra_hdd:
        e["hdd"] = {"estado": NAO_APLICAVEL, "motivo": f"texto com menos de {p.amostra_hdd} palavras (amostra do HD-D)"}
    if lingua != "en":
        e["flesch_kincaid"] = {"estado": NAO_APLICAVEL, "motivo": "fórmula calibrada apenas para inglês"}
    return e


def sanear(indicadores: dict, estados: dict) -> tuple[dict, dict]:
    """Converte NaN e infinitos em None e regista-os como falha (exceto se já tiverem estado)."""
    limpos = {}
    for k, v in indicadores.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            limpos[k] = None
            estados.setdefault(k, {"estado": FALHA, "motivo": "o cálculo produziu um valor inválido"})
        elif k in estados and estados[k]["estado"] in (NAO_APLICAVEL, DESCONHECIDO, FALHA):
            limpos[k] = None
        else:
            limpos[k] = v
    return limpos, estados


def dividir(a, b):
    """Divisão que devolve NaN (e não zero nem erro) quando o denominador é zero."""
    return a / b if b else float("nan")
