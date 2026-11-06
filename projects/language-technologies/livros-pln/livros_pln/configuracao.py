"""Parâmetros metodológicos centralizados.

Os valores por omissão estão aqui; `config/parametros.toml` (opcional) altera-os sem mexer
no código. Os parâmetros fazem parte da impressão digital do código: mudá-los obriga a
reprocessar os livros.
"""
from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass, fields
from pathlib import Path

FICHEIRO = Path(__file__).resolve().parent.parent / "config" / "parametros.toml"


@dataclass(frozen=True)
class Parametros:
    # Diversidade lexical
    janela_mattr: int = 500           # Covington e McFall (2010)
    limiar_mtld: float = 0.72         # McCarthy e Jarvis (2010)
    minimo_fator_mtld: int = 10       # comprimento mínimo de um fator completo (convenção de Kyle, lexical_diversity)
    amostra_hdd: int = 42             # McCarthy e Jarvis (2007, 2010)
    # Extensão mínima (em palavras) para um indicador ser considerado aplicável
    minimo_mtld: int = 100
    minimo_texto: int = 1000          # abaixo disto, os indicadores agregados são instáveis
    # Sintaxe
    frase_longa: int = 30             # limiar de «frase longa», em palavras
    # Evolução ao longo do livro
    segmentos: int = 10
    # Leitura (Brysbaert, 2019: 238 palavras/min em não ficção, 260 em ficção, leitura silenciosa em inglês)
    palavras_por_minuto: int = 238
    # Estilometria
    delta_palavras_frequentes: int = 150
    delta_minimo_textos: int = 3
    # Rede de personagens
    rede_minimo_mencoes: int = 5
    rede_maximo_personagens: int = 40


def carregar(ficheiro: Path = FICHEIRO) -> Parametros:
    if not ficheiro.exists():
        return Parametros()
    dados = tomllib.loads(ficheiro.read_text(encoding="utf-8"))
    validos = {f.name for f in fields(Parametros)}
    desconhecidos = set(dados) - validos
    if desconhecidos:
        raise ValueError(f"Parâmetros desconhecidos em {ficheiro.name}: {', '.join(sorted(desconhecidos))}")
    return Parametros(**dados)


PARAMETROS = carregar()


def como_dicionario(p: Parametros = PARAMETROS) -> dict:
    return asdict(p)
