-- =====================================================================
-- 04_analises.sql : perguntas sobre as contas do Vitória SC
-- Cada consulta começa com "-- @q" seguido do título (usado pelo
-- script scripts/correr_analises.py para gerar resultados.md).
-- =====================================================================


-- @q 1. Evolução do resultado líquido da SAD (variação face à época anterior)
-- Conceitos: função de janela LAG, ordenação temporal
SELECT
    epoca_id                                              AS epoca,
    resultado_liquido                                     AS rl,
    resultado_liquido - LAG(resultado_liquido) OVER w     AS variacao,
    CASE WHEN resultado_liquido >= 0 THEN 'lucro' ELSE 'prejuízo' END AS sinal
FROM v_dr
WHERE entidade_id = 'SAD'
WINDOW w AS (ORDER BY epoca_id)
ORDER BY epoca_id;


-- @q 2. Dependência das vendas de jogadores: resultado da SAD sem mais-valias
-- Conceitos: JOIN, coluna calculada, CASE
SELECT
    epoca_id                AS epoca,
    resultado_liquido       AS rl,
    mais_valias_liquidas    AS mais_valias,
    rl_sem_mais_valias,
    CASE WHEN resultado_liquido >= 0 AND rl_sem_mais_valias < 0
         THEN 'lucro só graças às vendas' ELSE '' END AS leitura
FROM v_kpis
WHERE entidade_id = 'SAD' AND mais_valias_liquidas IS NOT NULL
ORDER BY epoca_id;


-- @q 3. Peso dos gastos com pessoal nas receitas da SAD (ranking)
-- Conceitos: RANK, filtro de nulos. Nota: a regra da UEFA (custos do plantel
-- até 70%) usa uma base diferente; este rácio é uma aproximação simples.
SELECT
    epoca_id                AS epoca,
    vendas_servicos         AS receitas,
    gastos_pessoal          AS pessoal,
    pct_pessoal_receitas    AS pct,
    RANK() OVER (ORDER BY pct_pessoal_receitas DESC) AS ranking_pior
FROM v_kpis
WHERE entidade_id = 'SAD' AND vendas_servicos IS NOT NULL
ORDER BY epoca_id;


-- @q 4. EBITDA sem transferências da SAD
-- Conceitos: filtro por rubrica na tabela longa
SELECT
    dr.epoca_id AS epoca,
    dr.valor    AS ebitda_sem_transferencias
FROM demonstracao_resultados dr
WHERE dr.entidade_id = 'SAD' AND dr.rubrica_id = 'ebitda_sem_transferencias'
ORDER BY dr.epoca_id;


-- @q 5. Composição das receitas operacionais: peso de cada fonte (%)
-- Conceitos: SUM() OVER (PARTITION BY), pivot com CASE
WITH pct AS (
    SELECT
        epoca_id,
        categoria,
        100.0 * valor / SUM(valor) OVER (PARTITION BY epoca_id) AS p
    FROM receitas_composicao
)
SELECT
    epoca_id AS epoca,
    ROUND(MAX(CASE WHEN categoria = 'Direitos TV' THEN p END), 1)                  AS tv,
    ROUND(MAX(CASE WHEN categoria = 'Competições UEFA + Nacionais' THEN p END), 1) AS competicoes,
    ROUND(MAX(CASE WHEN categoria = 'Sócios e Camarotes' THEN p END), 1)           AS socios,
    ROUND(MAX(CASE WHEN categoria = 'Patrocínios e Publicidade' THEN p END), 1)    AS patrocinios,
    ROUND(MAX(CASE WHEN categoria = 'Bilhética' THEN p END), 1)                    AS bilhetica,
    ROUND(SUM(CASE WHEN categoria IN ('Merchandising', 'Mecanismo Solidariedade',
                                      'Subsídios', 'Outros') THEN p END), 1)      AS outras
FROM pct
GROUP BY epoca_id
ORDER BY epoca_id;


-- @q 6. Épocas com e sem competições europeias: receitas médias
-- Conceitos: CTE, agregação condicional, AVG
WITH uefa AS (
    SELECT epoca_id,
           MAX(CASE WHEN categoria = 'Competições UEFA + Nacionais' THEN valor END) AS competicoes,
           SUM(valor) AS total
    FROM receitas_composicao
    GROUP BY epoca_id
)
SELECT
    CASE WHEN competicoes > 2000000 THEN 'Com fase de grupos UEFA' ELSE 'Sem UEFA' END AS grupo,
    COUNT(*)                     AS epocas,
    GROUP_CONCAT(epoca_id, ', ') AS lista,
    CAST(AVG(total) AS INTEGER)  AS receita_media
FROM uefa
GROUP BY grupo;


-- @q 7. Capital próprio da SAD: épocas em falência técnica
-- Conceitos: CASE, contagem acumulada com SUM() OVER
SELECT
    epoca_id        AS epoca,
    ativo_total,
    passivo_total,
    capital_proprio,
    CASE WHEN capital_proprio < 0 THEN 'negativo' ELSE 'positivo' END AS situacao,
    SUM(CASE WHEN capital_proprio < 0 THEN 1 ELSE 0 END)
        OVER (ORDER BY epoca_id)                     AS epocas_negativas_acumuladas,
    ROUND(1.0 * passivo_total / ativo_total, 2)      AS passivo_sobre_ativo
FROM balanco
WHERE entidade_id = 'SAD'
ORDER BY epoca_id;


-- @q 8. Peso dos juros nas receitas da SAD
-- Conceitos: NULLIF para evitar divisão por zero; valores positivos de
-- "juros" (2014/15, 2016/17) são rendimentos financeiros líquidos
SELECT
    epoca_id                 AS epoca,
    vendas_servicos          AS receitas,
    -juros                   AS juros_pagos,
    ROUND(100.0 * -juros / NULLIF(vendas_servicos, 0), 1) AS pct_juros_sobre_receitas
FROM v_dr
WHERE entidade_id = 'SAD' AND juros IS NOT NULL
ORDER BY epoca_id;


-- @q 9. Crescimento dos juros da SAD nas últimas 5 épocas (taxa média anual)
-- Conceitos: subconsultas escalares, potência via exp/ln
WITH j AS (
    SELECT epoca_id, -valor AS juros
    FROM demonstracao_resultados
    WHERE entidade_id = 'SAD' AND rubrica_id = 'juros'
)
SELECT
    (SELECT juros FROM j WHERE epoca_id = '2019/20') AS juros_2019_20,
    (SELECT juros FROM j WHERE epoca_id = '2024/25') AS juros_2024_25,
    ROUND(100 * (exp(ln(1.0 * (SELECT juros FROM j WHERE epoca_id = '2024/25')
                          / (SELECT juros FROM j WHERE epoca_id = '2019/20')) / 5) - 1), 1)
                                                     AS crescimento_anual_pct;


-- @q 10. SAD, Clube e Grupo: resultado líquido lado a lado
-- Conceitos: vista com pivot, COALESCE, diferença de consolidação
SELECT
    epoca_id  AS epoca,
    rl_sad,
    rl_clube,
    rl_consolidado,
    rl_consolidado - (rl_sad + rl_clube) AS diferenca_consolidacao
FROM v_resultado_por_entidade
WHERE COALESCE(rl_sad, rl_clube, rl_consolidado) IS NOT NULL
ORDER BY epoca_id;


-- @q 11. Passivo do Clube vs passivo da SAD
-- Conceitos: self-join da tabela balanco
SELECT
    s.epoca_id                     AS epoca,
    c.passivo_total                AS passivo_clube,
    s.passivo_total                AS passivo_sad,
    ROUND(1.0 * s.passivo_total / c.passivo_total, 1) AS sad_vezes_clube
FROM balanco s
JOIN balanco c ON c.epoca_id = s.epoca_id AND c.entidade_id = 'CLUBE'
WHERE s.entidade_id = 'SAD'
ORDER BY s.epoca_id;


-- @q 12. Transferências: quanto das vendas brutas fica no clube
-- Conceitos: percentagem, filtro em subconsulta, média móvel de 3 épocas
SELECT
    epoca_id               AS epoca,
    vendas_brutas,
    mais_valias_liquidas,
    ROUND(100.0 * mais_valias_liquidas / vendas_brutas, 1) AS pct_retencao,
    CAST(AVG(mais_valias_liquidas) OVER (ORDER BY epoca_id
         ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS INTEGER) AS media_movel_3_epocas
FROM transferencias
WHERE entidade_id = 'SAD'
ORDER BY epoca_id;


-- @q 13. Gastos com pessoal do grupo: atletas vs restante pessoal
-- Conceitos: agregação condicional, crescimento face à 1.ª época
WITH p AS (
    SELECT epoca_id,
           SUM(CASE WHEN categoria = 'Atletas' THEN valor END) AS atletas,
           SUM(valor) AS total
    FROM gastos_pessoal_composicao
    GROUP BY epoca_id
)
SELECT
    epoca_id AS epoca,
    atletas,
    total,
    ROUND(100.0 * atletas / total, 1) AS pct_atletas,
    ROUND(1.0 * total / FIRST_VALUE(total) OVER (ORDER BY epoca_id), 2) AS indice_vs_2017_18
FROM p
ORDER BY epoca_id;


-- @q 14. Dívida financeira da SAD por maturidade (30/06/2025)
-- Conceitos: totais com UNION ALL, percentagens
SELECT credor, total, menos_1_ano,
       ROUND(100.0 * menos_1_ano / total, 1) AS pct_curto_prazo
FROM divida
WHERE tipo = 'financeira'
UNION ALL
SELECT 'TOTAL', SUM(total), SUM(menos_1_ano),
       ROUND(100.0 * SUM(menos_1_ano) / SUM(total), 1)
FROM divida
WHERE tipo = 'financeira';


-- @q 15. Fluxos de caixa da SAD: como se financiou cada época
-- Conceitos: CASE com várias condições
SELECT
    c.epoca_id     AS epoca,
    c.operacional,
    c.investimento,
    c.financiamento,
    b.caixa        AS caixa_final,
    CASE
        WHEN c.operacional >= 0                         THEN 'operação gerou caixa'
        WHEN c.investimento > ABS(c.financiamento)      THEN 'tapou o buraco com vendas/investimento'
        ELSE 'tapou o buraco com financiamento'
    END AS leitura
FROM cash_flow c
JOIN balanco b ON b.entidade_id = c.entidade_id AND b.epoca_id = c.epoca_id
ORDER BY c.epoca_id;


-- @q 16. Melhor e pior época de cada entidade
-- Conceitos: ROW_NUMBER com PARTITION BY
WITH r AS (
    SELECT entidade_id, epoca_id, resultado_liquido,
           ROW_NUMBER() OVER (PARTITION BY entidade_id ORDER BY resultado_liquido DESC) AS melhor,
           ROW_NUMBER() OVER (PARTITION BY entidade_id ORDER BY resultado_liquido ASC)  AS pior
    FROM v_dr
    WHERE resultado_liquido IS NOT NULL
)
SELECT entidade_id AS entidade,
       MAX(CASE WHEN melhor = 1 THEN epoca_id || ' (' || resultado_liquido || ')' END) AS melhor_epoca,
       MAX(CASE WHEN pior = 1   THEN epoca_id || ' (' || resultado_liquido || ')' END) AS pior_epoca
FROM r
GROUP BY entidade_id;


-- @q 17. Qualidade dos dados: cobertura por entidade
-- Conceitos: COUNT DISTINCT, LEFT JOIN, análise de lacunas
SELECT
    en.entidade_id                       AS entidade,
    COUNT(DISTINCT dr.epoca_id)          AS epocas_com_dados,
    COUNT(dr.rubrica_id)                 AS valores_dr,
    ROUND(1.0 * COUNT(dr.rubrica_id) / COUNT(DISTINCT dr.epoca_id), 1) AS rubricas_por_epoca
FROM entidade en
LEFT JOIN demonstracao_resultados dr ON dr.entidade_id = en.entidade_id
GROUP BY en.entidade_id;


-- @q 18. Qualidade dos dados: valores repetidos de época para época
-- Valores iguais em épocas diferentes podem ser marcadores e não dados reais.
SELECT categoria, valor, COUNT(*) AS n_epocas, GROUP_CONCAT(epoca_id, ', ') AS epocas
FROM receitas_composicao
GROUP BY categoria, valor
HAVING COUNT(*) > 1
ORDER BY n_epocas DESC;


-- @q 19. Qualidade dos dados: mais-valias SAD vs consolidadas
-- O site apresenta números diferentes em páginas diferentes.
SELECT s.epoca_id AS epoca,
       s.mais_valias_liquidas AS pagina_transferencias_sad,
       c.mais_valias_liquidas AS pagina_consolidado,
       s.mais_valias_liquidas - c.mais_valias_liquidas AS diferenca
FROM transferencias s
JOIN transferencias c ON c.epoca_id = s.epoca_id AND c.entidade_id = 'CONSOLIDADO'
WHERE s.entidade_id = 'SAD' AND s.mais_valias_liquidas <> c.mais_valias_liquidas;
