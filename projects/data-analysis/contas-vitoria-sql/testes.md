# Testes de qualidade e reconciliação

Gerado por `scripts/testes.py`. Corre-o depois de `build_db.py`.

**33 testes aprovados · 0 falhados · 7 avisos**

Python 3.13.17 · SQLite 3.45.1 · Linux

## 1. Integridade da base de dados

| Resultado | Teste | Detalhe |
|:---:|:---|:---|
| ✓ | Ficheiro SQLite íntegro (`PRAGMA integrity_check`) | ok |
| ✓ | Chaves estrangeiras válidas (`PRAGMA foreign_key_check`) | 0 referências inválidas |
| ✓ | Épocas contínuas de 2012/13 a 2025/26 | 14 épocas |
| ✓ | Todas as linhas da DR têm rubrica conhecida | 0 sem correspondência |

## 2. Coerência contabilística

| Resultado | Teste | Detalhe |
|:---:|:---|:---|
| ✓ | Ativo = passivo + capital próprio (todas as entidades e épocas) | diferença ≤ 1 € em todas |
| ✓ | Corrente + não corrente = total (balanço dos R&C) | 13 épocas |
| ✓ | Tabela `balanco` (SAD) igual ao balanço dos R&C | sem diferenças |
| ✓ | Soma das categorias de pessoal = nº de funcionários | todas as épocas |
| ✓ | Soma das rubricas de gastos com pessoal = total | épocas com remunerações decompostas (2016/17 em diante) |
| ⚠ | Remunerações sem decomposição por categoria | 2012/13, 2013/14, 2014/15, 2015/16: os R&C dessas épocas só dão o total |
| ✓ | Passes: valor inicial + aquisições − amortizações − saídas = valor final | todas as épocas (tolerância de 4 €: oito valores arredondados ao euro) |
| ✓ | Passes: valor final de uma época = valor inicial da seguinte | sem quebras |
| ✓ | Resultado sem mais-valias = resultado líquido − mais-valias | todas as épocas |
| ✓ | Dívida por instrumento: parte de curto prazo ≤ total | sem incoerências |
| ⚠ | `rec_2025_26`: linhas do comunicado somam o resultado líquido | -11 062 106 € vs -11 063 044 € · diferença de 938 € não discriminada no comunicado |
| ⚠ | `rec_2025_26`: EBITDA publicado ≠ rendimentos − gastos | diferença de 0,79 M€: depreciações de ativos não desportivos (deduzida) |

## 3. Reconciliação: números citados nos relatórios vs. base de dados

| Resultado | Teste | Detalhe |
|:---:|:---|:---|
| ✓ | Resultado líquido da SAD 2024/25 (M€) | publicado 7,6 · calculado 7,610 |
| ✓ | Resultado sem mais-valias 2024/25 (M€) | publicado -19,9 · calculado -19,931 |
| ✓ | Resultado sem mais-valias 2023/24 (M€) | publicado -21,4 · calculado -21,389 |
| ✓ | Mais-valias 2024/25 (M€) | publicado 27,5 · calculado 27,541 |
| ✓ | Resultado líquido da SAD 2025/26 (M€) | publicado -11,1 · calculado -11,063 |
| ✓ | Capital próprio da SAD a 30/06/2026 (M€) | publicado -36,8 · calculado -36,832 |
| ✓ | Passivo da SAD a 30/06/2026 (M€) | publicado 85,3 · calculado 85,299 |
| ✓ | Rácio de endividamento 2023/24 | publicado 1,87 · calculado 1,871 |
| ✓ | Dívida financeira a 30/06/2025 (M€) | publicado 34,6 · calculado 34,584 |
| ✓ | Juros suportados 2024/25 (M€) | publicado 5 · calculado 5,007 |
| ✓ | Taxa de juro implícita 2024/25 (%) | publicado 14,6 · calculado 14,610 |
| ✓ | Euribor a 12 meses, média 2024/25 (%) | publicado 2,6 · calculado 2,620 |
| ✓ | Funcionários da SAD 2024/25 | publicado 229 · calculado 229,000 |
| ✓ | Vendas brutas por euro de receita 2024/25 | publicado 2,19 · calculado 2,193 |
| ✓ | Défice antes de vendas, média 2022/23–2024/25 (M€) | publicado -20,9 · calculado -20,932 |
| ✓ | Rácio UEFA de custos do plantel 2024/25 (%) · consulta 45 | publicado 44,7 · calculado 44,700 |
| ✓ | R² da regressão despesas vs. lugar · consulta 53 | publicado 0,09 · calculado 0,090 |

## 4. Consultas de análise

| Resultado | Teste | Detalhe |
|:---:|:---|:---|
| ✓ | As 55 consultas correm sem erros |  |
| ✓ | Todas as consultas devolvem pelo menos uma linha |  |
| ✓ | Nenhuma consulta usa funções que não existem no SQLite do browser (ln, log, pow) |  |

## 5. Avisos de qualidade (não bloqueiam)

| Resultado | Teste | Detalhe |
|:---:|:---|:---|
| ⚠ | Valor repetido em 4 épocas: Direitos TV | 6 922 619 € |
| ⚠ | Valor repetido em 3 épocas: Direitos TV | 7 000 000 € |
| ⚠ | Vendas brutas = mais-valias em 2020/21 | a fonte só indica as mais-valias; o rácio de mais-valias sobre vendas dá 100% |
| ⚠ | Épocas da SAD sem receitas detalhadas | 2012/13, 2025/26 |
