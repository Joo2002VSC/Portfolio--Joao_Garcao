"""Deteção da língua (português, francês ou inglês) por frequência de palavras funcionais.

Não depende de serviços externos e é determinística. Para textos literários com
milhares de palavras, as palavras funcionais distinguem estas três línguas com
uma margem muito grande.
"""
from __future__ import annotations

import re
from collections import Counter

FUNCIONAIS = {
    "pt": {"o", "a", "os", "as", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "um", "uma",
           "que", "e", "é", "não", "com", "para", "por", "se", "mas", "como", "mais", "ao", "à", "lhe", "ele",
           "ela", "elle", "ella", "isso", "já", "também", "muito", "seu", "sua", "pelo", "pela", "eram", "foi"},
    "fr": {"le", "la", "les", "de", "des", "du", "un", "une", "et", "est", "que", "qui", "ne", "pas", "en",
           "dans", "pour", "sur", "au", "aux", "il", "elle", "ils", "nous", "vous", "je", "ce", "cette", "mais",
           "avec", "son", "sa", "ses", "était", "été", "plus", "comme", "tout", "bien", "où", "lui", "leur"},
    "en": {"the", "and", "of", "to", "a", "in", "is", "it", "that", "was", "he", "she", "for", "on", "with",
           "as", "his", "her", "at", "by", "had", "not", "but", "be", "this", "they", "you", "from", "which",
           "or", "have", "were", "an", "said", "would", "there", "been", "what", "when", "who", "all"},
}
MODELOS = {"pt": "pt_core_news_md", "fr": "fr_core_news_md", "en": "en_core_web_md"}
NOMES = {"pt": "português", "fr": "francês", "en": "inglês"}


def detetar(texto: str, amostra: int = 50_000) -> tuple[str, dict[str, float]]:
    palavras = Counter(re.findall(r"[^\W\d_]+", texto[:amostra * 8].lower())[:amostra])
    total = sum(palavras.values()) or 1
    pontuacao = {lg: sum(palavras[w] for w in funcionais) / total for lg, funcionais in FUNCIONAIS.items()}
    return max(pontuacao, key=pontuacao.get), pontuacao
