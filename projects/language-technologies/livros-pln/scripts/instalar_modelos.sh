#!/usr/bin/env bash
# Instala os modelos spaCy de requirements-modelos.txt.
# Tenta primeiro as releases do GitHub e depois o espelho no Hugging Face (com novas tentativas),
# porque o download de modelos falha por vezes com erros 5xx temporários.
set -euo pipefail
cd "$(dirname "$0")/.."
grep -v '^#' requirements-modelos.txt | grep -v '^\s*$' | while IFS='=' read -r nome _ versao; do
  if python -c "import $nome" 2>/dev/null; then echo "✓ $nome já instalado"; continue; fi
  fontes=(
    "https://github.com/explosion/spacy-models/releases/download/${nome}-${versao}/${nome}-${versao}-py3-none-any.whl"
    "https://huggingface.co/spacy/${nome}/resolve/main/${nome}-any-py3-none-any.whl"
  )
  instalado=0
  for tentativa in 1 2 3; do
    for url in "${fontes[@]}"; do
      if python -m pip install --quiet "$url"; then instalado=1; break 2; fi
      echo "… falhou: $url (tentativa $tentativa)"
    done
    sleep $((tentativa * 10))
  done
  [ "$instalado" = 1 ] || { echo "✗ não foi possível instalar $nome"; exit 1; }
  echo "✓ $nome"
done
