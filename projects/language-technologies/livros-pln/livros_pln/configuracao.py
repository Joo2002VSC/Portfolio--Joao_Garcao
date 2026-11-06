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
    # Sentimento (Hutto e Gilbert, 2014: compound ≥ 0,05 positivo; ≤ −0,05 negativo)
    sentimento_limiar: float = 0.05
    sentimento_minimo_palavras: int = 3     # frases mais curtas não são pontuadas
    # Leis do vocabulário
    zipf_frequencia_minima: int = 5         # o ajuste da lei de Zipf ignora formas mais raras (patamar dos hapax)
    # Colocações e palavras-chave
    colocacao_frequencia_minima: int = 5    # ocorrências mínimas de um bigrama
    palavras_chave_por_segmento: int = 5
    # Emoções (NRC EmoLex) e divisão em capítulos
    emocoes_janela_negacao: int = 3         # palavras depois de uma negação que não contam para as emoções
    capitulo_minimo_palavras: int = 300     # capítulos mais curtos juntam-se ao seguinte
    blocos_sem_capitulos: int = 20          # blocos iguais quando o texto não tem capítulos detetáveis
    # Tonalidade (classificação interpretativa; ver emocoes.tonalidade)
    tom_limiar: float = 0.05                # limiar convencional do VADER, aplicado à média dos segmentos
    tom_forte: float = 0.5                  # |compound| a partir do qual uma frase é fortemente polarizada
    tom_minimo_forte_pct: float = 10.0      # % mínima de frases fortes positivas E negativas para «misto»
    tom_minimo_frases: int = 300            # frases pontuadas mínimas
    tom_cobertura_minima: float = 3.0       # % mínima das palavras no léxico de sentimento
    tom_bootstrap: int = 2000               # reamostragens do intervalo de confiança


def pasta_lexicos(ficheiro: Path | None = None) -> Path:
    """Pasta dos léxicos descarregados (fora do repositório): `lexicos` em config/pastas.toml, ou `lexicos/`."""
    ficheiro = ficheiro or PASTAS
    if ficheiro.exists():
        dados = tomllib.loads(ficheiro.read_text(encoding="utf-8"))
        if "lexicos" in dados:
            return Path(dados["lexicos"]).expanduser()
    return FICHEIRO.parent.parent / "lexicos"


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

# Pastas de trabalho (opcional e local): config/pastas.toml, que não vai para o GitHub (.gitignore), permite guardar os
# livros e os resultados noutra pasta do computador. Sem esse ficheiro, usam-se livros/ e resultados/ do repositório.
PASTAS = FICHEIRO.parent / "pastas.toml"


def pastas(ficheiro: Path = PASTAS) -> tuple[Path, Path]:
    """Devolve (pasta dos livros, pasta dos resultados)."""
    livros, resultados = Path("livros"), Path("resultados")
    if ficheiro.exists():
        dados = tomllib.loads(ficheiro.read_text(encoding="utf-8"))
        desconhecidos = set(dados) - {"livros", "resultados", "lexicos"}
        if desconhecidos:
            raise ValueError(f"Chaves desconhecidas em {ficheiro.name}: {', '.join(sorted(desconhecidos))}")
        livros = Path(dados.get("livros", livros)).expanduser()
        resultados = Path(dados.get("resultados", resultados)).expanduser()
    return livros, resultados


def como_dicionario(p: Parametros = PARAMETROS) -> dict:
    return asdict(p)
