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


-- =====================================================================
-- FINANÇAS vs. DESEMPENHO DESPORTIVO E ENQUADRAMENTO REGULATÓRIO
-- =====================================================================


-- @q 20. Finanças e resultados desportivos da SAD, época a época
-- Conceitos: LEFT JOIN entre factos financeiros e desportivos, COALESCE
SELECT
    d.epoca_id                                         AS epoca,
    d.posicao_liga                                     AS lugar,
    COALESCE(d.competicao_europeia || ' · ' || d.fase_europeia, '—') AS europa,
    COALESCE(d.trofeu, '')                             AS trofeu,
    COALESCE(k.vendas_servicos, r.rendimentos_operacionais) AS receitas,
    k.gastos_pessoal                                   AS pessoal,
    r.resultado_liquido                                AS rl
FROM desempenho_desportivo d
LEFT JOIN v_kpis k ON k.epoca_id = d.epoca_id AND k.entidade_id = 'SAD'
LEFT JOIN v_dr   r ON r.epoca_id = d.epoca_id AND r.entidade_id = 'SAD'
ORDER BY d.epoca_id;


-- @q 21. Quanto vale a Europa: receitas e resultado médios por tipo de época
-- Conceitos: CASE para classificar, agregação, AVG
WITH e AS (
    SELECT
        d.epoca_id,
        CASE
            WHEN d.fase_europeia IN ('Fase de grupos', 'Oitavos de final') THEN '1. Fase de grupos ou mais'
            WHEN d.fase_europeia = 'Pré-eliminatória'                      THEN '2. Só pré-eliminatórias'
            ELSE                                                                '3. Sem Europa'
        END AS tipo,
        k.vendas_servicos,
        k.resultado_liquido
    FROM desempenho_desportivo d
    JOIN v_kpis k ON k.epoca_id = d.epoca_id AND k.entidade_id = 'SAD'
    WHERE k.vendas_servicos IS NOT NULL
)
SELECT tipo,
       COUNT(*)                                   AS epocas,
       GROUP_CONCAT(epoca_id, ', ')               AS lista,
       CAST(AVG(vendas_servicos) AS INTEGER)      AS receita_media,
       CAST(AVG(resultado_liquido) AS INTEGER)    AS rl_medio
FROM e
GROUP BY tipo
ORDER BY tipo;


-- @q 22. Gastar mais em salários garante melhor classificação?
-- Conceitos: correlação de Pearson calculada em SQL (AVG, SUM, sqrt).
-- Correlação negativa = mais gastos, lugar mais baixo (melhor) na tabela.
WITH x AS (
    SELECT k.gastos_pessoal AS g, d.posicao_liga AS p
    FROM v_kpis k
    JOIN desempenho_desportivo d ON d.epoca_id = k.epoca_id
    WHERE k.entidade_id = 'SAD' AND k.gastos_pessoal IS NOT NULL
),
m AS (SELECT AVG(g) AS mg, AVG(p) AS mp, COUNT(*) AS n FROM x)
SELECT
    m.n                                                         AS epocas,
    ROUND(SUM((g - mg) * (p - mp)) /
          (sqrt(SUM((g - mg) * (g - mg))) * sqrt(SUM((p - mp) * (p - mp)))), 2) AS correlacao,
    CAST(m.mg AS INTEGER)                                       AS pessoal_medio,
    ROUND(m.mp, 1)                                              AS lugar_medio
FROM x, m;


-- @q 23. Custo de cada lugar: gastos com pessoal por época e lugar obtido
-- Conceitos: ordenação por duas colunas, rácio
SELECT
    d.epoca_id        AS epoca,
    d.posicao_liga    AS lugar,
    k.gastos_pessoal  AS pessoal,
    RANK() OVER (ORDER BY k.gastos_pessoal DESC) AS ranking_gasto,
    RANK() OVER (ORDER BY d.posicao_liga ASC)    AS ranking_lugar
FROM desempenho_desportivo d
JOIN v_kpis k ON k.epoca_id = d.epoca_id AND k.entidade_id = 'SAD'
WHERE k.gastos_pessoal IS NOT NULL
ORDER BY d.epoca_id;


-- @q 24. Aproximação ao rácio de custos do plantel da UEFA (limite de 70% desde 2025/26)
-- (salários de atletas e treinadores + amortizações) / (receitas + mais-valias).
-- Aproximação: a UEFA usa definições próprias e só controla clubes nas suas provas.
WITH p AS (
    SELECT epoca_id,
           SUM(CASE WHEN categoria IN ('Atletas', 'Treinadores') THEN valor END) AS plantel
    FROM gastos_pessoal_composicao
    GROUP BY epoca_id
)
SELECT
    p.epoca_id                                   AS epoca,
    p.plantel + (-r.depreciacoes)                AS custos_plantel,
    r.vendas_servicos + t.mais_valias_liquidas   AS receitas_relevantes,
    ROUND(100.0 * (p.plantel - r.depreciacoes)
          / (r.vendas_servicos + t.mais_valias_liquidas), 1) AS racio_pct,
    ROUND(100.0 * (p.plantel - r.depreciacoes) / r.vendas_servicos, 1) AS racio_sem_vendas_pct,
    CASE WHEN 100.0 * (p.plantel - r.depreciacoes)
              / (r.vendas_servicos + t.mais_valias_liquidas) <= 70
         THEN 'cumpriria 70%' ELSE 'acima de 70%' END AS leitura
FROM p
JOIN v_dr r           ON r.epoca_id = p.epoca_id AND r.entidade_id = 'SAD'
JOIN transferencias t ON t.epoca_id = p.epoca_id AND t.entidade_id = 'SAD'
ORDER BY p.epoca_id;


-- @q 25. Ponto de equilíbrio 2025/26: quanto é preciso ganhar com jogadores
-- Valores do comunicado de contas 2025/26 (tabela evento). Para resultado
-- líquido zero, o resultado com direitos de atletas tem de cobrir o resto.
WITH v AS (
    SELECT
        (SELECT resultado_liquido FROM v_dr WHERE entidade_id = 'SAD' AND epoca_id = '2025/26') AS rl,
        (SELECT valor FROM evento WHERE epoca_id = '2025/26'
            AND descricao LIKE 'Resultado com direitos de atletas%')                          AS rda
)
SELECT
    rda                    AS resultado_com_jogadores_2025_26,
    rl                     AS resultado_liquido_2025_26,
    rda - rl               AS necessario_para_equilibrio,
    -rl                    AS falta_face_a_2025_26
FROM v;


-- @q 26. Centralização dos direitos TV (2028/29): parte igual estimada por clube
-- Parâmetros da proposta: 90% para a Liga Betclic (18 clubes), 33,2% em
-- partes iguais. Cenários para o valor total do contrato.
WITH cenarios(total) AS (VALUES (200000000), (250000000), (275000000)),
     atual AS (
        SELECT valor AS tv_atual FROM receitas_composicao
        WHERE categoria = 'Direitos TV' AND epoca_id = '2024/25'
     )
SELECT
    total                                        AS valor_total_contrato,
    CAST(total * 0.90 * 0.332 / 18 AS INTEGER)   AS parte_igual_por_clube,
    tv_atual                                     AS tv_vitoria_2024_25,
    ROUND(100.0 * (total * 0.90 * 0.332 / 18) / tv_atual, 1) AS parte_igual_em_pct_do_atual
FROM cenarios, atual;


-- =====================================================================
-- DÍVIDA, JUROS, RÁCIOS E FUNCIONÁRIOS (dados verificados nos R&C)
-- =====================================================================


-- @q 27. Custo da dívida: financiamentos, juros e taxa de juro implícita
-- Taxa implícita = juros suportados / média dos financiamentos no início e no fim.
-- Os juros incluem encargos de factoring e antecipação de receitas.
WITH f AS (
    SELECT epoca_id,
           financiamentos_nc + financiamentos_c                       AS financiamentos,
           juros_suportados,
           LAG(financiamentos_nc + financiamentos_c) OVER (ORDER BY epoca_id) AS fin_anterior
    FROM balanco_sad_rc
    WHERE financiamentos_nc IS NOT NULL
)
SELECT
    f.epoca_id                                           AS epoca,
    f.financiamentos,
    f.juros_suportados                                   AS juros,
    ROUND(100.0 * f.juros_suportados / ((f.financiamentos + f.fin_anterior) / 2.0), 1) AS taxa_implicita_pct,
    ROUND(100.0 * f.juros_suportados / k.vendas_servicos, 1)                          AS juros_em_pct_receitas
FROM f
LEFT JOIN v_kpis k ON k.epoca_id = f.epoca_id AND k.entidade_id = 'SAD'
ORDER BY f.epoca_id;


-- @q 28. Estrutura da dívida financeira: curto prazo e dívida líquida
SELECT
    epoca_id                                                     AS epoca,
    financiamentos_nc + financiamentos_c                         AS divida_financeira,
    ROUND(100.0 * financiamentos_c / (financiamentos_nc + financiamentos_c), 1) AS pct_curto_prazo,
    caixa,
    financiamentos_nc + financiamentos_c - caixa                 AS divida_financeira_liquida,
    passivo_total - (financiamentos_nc + financiamentos_c)       AS outro_passivo
FROM balanco_sad_rc
WHERE financiamentos_nc IS NOT NULL
ORDER BY epoca_id;


-- @q 29. Rácios de balanço da SAD (12 épocas)
-- Endividamento = passivo / ativo · Autonomia = capital próprio / ativo
-- Liquidez geral = ativo corrente / passivo corrente · Imediata = caixa / passivo corrente
SELECT
    epoca_id                                                 AS epoca,
    ROUND(1.0 * passivo_total / ativo_total, 2)              AS endividamento,
    ROUND(100.0 * capital_proprio / ativo_total, 1)          AS autonomia_pct,
    ROUND(1.0 * ativo_corrente / passivo_corrente, 2)        AS liquidez_geral,
    ROUND(100.0 * caixa / passivo_corrente, 1)               AS liquidez_imediata_pct,
    RANK() OVER (ORDER BY 1.0 * passivo_total / ativo_total DESC) AS ranking_endividamento
FROM balanco_sad_rc
ORDER BY epoca_id;


-- @q 30. Cobertura de juros: quantas vezes o EBITDA paga os juros
-- EBITDA = resultado operacional + depreciações (com vendas de jogadores).
SELECT
    b.epoca_id                                          AS epoca,
    r.resultado_operacional - r.depreciacoes            AS ebitda,
    b.juros_suportados                                  AS juros,
    ROUND(1.0 * (r.resultado_operacional - r.depreciacoes) / NULLIF(b.juros_suportados, 0), 1) AS cobertura,
    CASE
        WHEN b.juros_suportados IS NULL OR b.juros_suportados = 0 THEN 'sem juros'
        WHEN (r.resultado_operacional - r.depreciacoes) < 0       THEN 'EBITDA negativo'
        WHEN (r.resultado_operacional - r.depreciacoes) < 3 * b.juros_suportados THEN 'fraca (< 3x)'
        ELSE 'confortável'
    END                                                 AS leitura
FROM balanco_sad_rc b
JOIN v_dr r ON r.epoca_id = b.epoca_id AND r.entidade_id = 'SAD'
WHERE r.resultado_operacional IS NOT NULL
ORDER BY b.epoca_id;


-- @q 31. Funcionários da SAD por categoria
SELECT
    epoca_id                                             AS epoca,
    funcionarios,
    jogadores,
    COALESCE(treinadores_profissional, 0) + COALESCE(treinadores_formacao, 0) AS treinadores,
    COALESCE(apoio_futebol_profissional, 0) + COALESCE(outro_pessoal, 0)      AS staff,
    ROUND(100.0 * jogadores / funcionarios, 1)           AS pct_jogadores,
    funcionarios - LAG(funcionarios) OVER (ORDER BY epoca_id) AS variacao
FROM pessoal_sad
ORDER BY epoca_id;


-- @q 32. Custo médio por funcionário e por jogador
SELECT
    epoca_id                                                    AS epoca,
    CAST(total_gastos_pessoal / funcionarios AS INTEGER)        AS custo_por_funcionario,
    CAST(rem_jogadores / jogadores AS INTEGER)                  AS remuneracao_media_jogador,
    CAST(rem_treinadores /
         (treinadores_profissional + treinadores_formacao) AS INTEGER) AS remuneracao_media_treinador,
    ROUND(1.0 * total_gastos_pessoal /
          FIRST_VALUE(total_gastos_pessoal) OVER (ORDER BY epoca_id), 1) AS indice_gastos
FROM pessoal_sad
WHERE epoca_id >= '2013/14'
ORDER BY epoca_id;


-- @q 33. Estrutura cresceu mais do que a equipa? Staff não-jogador vs jogadores
WITH p AS (
    SELECT epoca_id, jogadores,
           funcionarios - jogadores AS nao_jogadores
    FROM pessoal_sad
)
SELECT
    epoca_id                                       AS epoca,
    jogadores,
    nao_jogadores,
    ROUND(1.0 * nao_jogadores / jogadores, 2)      AS nao_jogadores_por_jogador
FROM p
ORDER BY epoca_id;


-- @q 34. Funcionários, salários, espectadores e classificação
SELECT
    d.epoca_id                    AS epoca,
    d.posicao_liga                AS lugar,
    d.media_espectadores          AS espectadores,
    p.funcionarios,
    p.total_gastos_pessoal        AS gastos_pessoal,
    CAST(p.total_gastos_pessoal / NULLIF(d.media_espectadores, 0) AS INTEGER) AS gasto_pessoal_por_espectador
FROM desempenho_desportivo d
JOIN pessoal_sad p ON p.epoca_id = d.epoca_id
ORDER BY d.epoca_id;


-- @q 35. Auditoria das fontes: divergências face aos Relatórios e Contas
SELECT
    fonte,
    COUNT(*)                          AS divergencias,
    COUNT(DISTINCT epoca_id)          AS epocas_afetadas,
    GROUP_CONCAT(DISTINCT epoca_id)   AS epocas,
    CAST(MAX(ABS(diferenca)) AS INTEGER) AS maior_diferenca
FROM divergencia
GROUP BY fonte
ORDER BY divergencias DESC;


-- =====================================================================
-- APROFUNDAMENTO: CONCEITOS FINANCEIROS
-- =====================================================================


-- @q 36. Custo amortizado: o que mudou com a reexpressão de 2024/25
SELECT
    indicador,
    valor_original,
    valor_reexpresso,
    valor_reexpresso - valor_original                                   AS diferenca,
    ROUND(100.0 * (valor_reexpresso - valor_original) / ABS(valor_original), 1) AS variacao_pct
FROM reexpressao
WHERE epoca_id = '2024/25'
ORDER BY ABS(valor_reexpresso - valor_original) DESC;


-- @q 37. Dívida líquida / EBITDA: quantos anos de EBITDA pagariam a dívida
WITH base AS (
    SELECT
        b.epoca_id,
        b.financiamentos_nc + b.financiamentos_c - b.caixa  AS divida_liquida,
        r.resultado_operacional - r.depreciacoes             AS ebitda,
        r.ebitda_sem_transferencias
    FROM balanco_sad_rc b
    JOIN v_dr r ON r.epoca_id = b.epoca_id AND r.entidade_id = 'SAD'
    WHERE b.financiamentos_nc IS NOT NULL
)
SELECT
    epoca_id                                                 AS epoca,
    divida_liquida,
    ebitda,
    CASE WHEN ebitda > 0 THEN ROUND(1.0 * divida_liquida / ebitda, 1) END AS divida_liq_ebitda,
    ebitda_sem_transferencias,
    CASE WHEN ebitda <= 0 THEN 'EBITDA negativo: rácio sem leitura'
         WHEN 1.0 * divida_liquida / ebitda > 3 THEN 'acima de 3x: alavancagem elevada'
         ELSE 'até 3x' END                                   AS leitura
FROM base
ORDER BY epoca_id;


-- @q 38. Fundo de maneio e prazos médios
-- PMR: clientes (correntes e não correntes) em dias de receitas + vendas de passes.
-- PMP: fornecedores em dias de FSE e mercadorias. Outras contas a pagar inclui
-- dívidas a clubes, intermediários e pessoal.
WITH r AS (
    SELECT epoca_id,
           SUM(CASE WHEN lado = 'ativo' AND rubrica = 'clientes' THEN valor END)              AS clientes,
           SUM(CASE WHEN lado = 'passivo' AND rubrica = 'fornecedores' THEN valor END)        AS fornecedores,
           SUM(CASE WHEN lado = 'passivo' AND rubrica = 'outras_contas_pagar' THEN valor END) AS outras_contas_pagar
    FROM balanco_rubrica
    GROUP BY epoca_id
)
SELECT
    r.epoca_id                                               AS epoca,
    b.ativo_corrente - b.passivo_corrente                    AS fundo_maneio,
    r.clientes,
    CAST(365.0 * r.clientes / (d.vendas_servicos + t.vendas_brutas) AS INTEGER) AS pmr_dias,
    CAST(365.0 * r.fornecedores / -(d.fse + d.cmvmc) AS INTEGER)               AS pmp_dias,
    r.outras_contas_pagar,
    ROUND(100.0 * r.outras_contas_pagar / b.passivo_total, 1) AS outras_contas_pagar_pct_passivo
FROM r
JOIN balanco_sad_rc b ON b.epoca_id = r.epoca_id
JOIN (SELECT epoca_id,
             MAX(CASE WHEN rubrica_id = 'vendas_servicos' THEN valor END) AS vendas_servicos,
             MAX(CASE WHEN rubrica_id = 'fse' THEN valor END)             AS fse,
             MAX(CASE WHEN rubrica_id = 'cmvmc' THEN valor END)           AS cmvmc
      FROM demonstracao_resultados WHERE entidade_id = 'SAD' GROUP BY epoca_id) d
     ON d.epoca_id = r.epoca_id
LEFT JOIN transferencias t ON t.epoca_id = r.epoca_id AND t.entidade_id = 'SAD'
ORDER BY r.epoca_id;


-- @q 39. Factoring e composição da dívida financeira por instrumento
SELECT
    data_ref,
    instrumento,
    total,
    ROUND(100.0 * total / SUM(total) OVER (PARTITION BY data_ref), 1)  AS pct_da_divida,
    ROUND(100.0 * menos_1_ano / total, 1)                              AS pct_curto_prazo
FROM financiamento_detalhe
ORDER BY data_ref, total DESC;


-- @q 40. Passes de jogadores: investimento, amortizações e abates
SELECT
    epoca_id                                               AS epoca,
    aquisicoes,
    amortizacoes,
    aquisicoes - amortizacoes                              AS investimento_liquido,
    rescisoes_bruto - rescisoes_amort_acumuladas           AS perda_em_rescisoes,
    valor_liquido_fim                                      AS valor_contabilistico_plantel,
    ROUND(100.0 * amortizacoes / (valor_liquido_inicio + aquisicoes), 1) AS taxa_amortizacao_pct
FROM passes_jogadores
ORDER BY epoca_id;


-- @q 41. Valor contabilístico vs. valor de venda: as "reservas ocultas" do plantel
-- Valor contabilístico dos passes vendidos = valor bruto alienado - amortizações acumuladas.
SELECT
    p.epoca_id                                                       AS epoca,
    p.valor_bruto_alienado - p.amort_acumuladas_alienadas            AS valor_contabilistico_vendido,
    t.vendas_brutas,
    t.vendas_brutas - (p.valor_bruto_alienado - p.amort_acumuladas_alienadas) AS reserva_oculta_realizada,
    ROUND(1.0 * t.vendas_brutas /
          NULLIF(p.valor_bruto_alienado - p.amort_acumuladas_alienadas, 0), 1) AS multiplo_de_venda,
    p.valor_liquido_fim                                              AS plantel_no_balanco
FROM passes_jogadores p
JOIN transferencias t ON t.epoca_id = p.epoca_id AND t.entidade_id = 'SAD'
ORDER BY p.epoca_id;


-- @q 42. Alavancagem operacional: peso dos custos fixos
-- Custos fixos = pessoal + FSE + depreciações. Mostra quanto as receitas cobrem.
SELECT
    epoca_id                                                       AS epoca,
    vendas_servicos                                                AS receitas,
    -(gastos_pessoal + fse + depreciacoes)                         AS custos_fixos,
    ROUND(100.0 * vendas_servicos / -(gastos_pessoal + fse + depreciacoes), 1) AS cobertura_pct,
    vendas_servicos + (gastos_pessoal + fse + depreciacoes)        AS defice_antes_de_vendas
FROM v_dr
WHERE entidade_id = 'SAD' AND vendas_servicos IS NOT NULL
ORDER BY epoca_id;


-- @q 43. Artigo 35.º do CSC e continuidade: capital próprio vs. metade do capital social
SELECT
    b.epoca_id                                           AS epoca,
    b.capital_proprio,
    2250000                                              AS metade_capital_social,
    CASE WHEN b.capital_proprio < 2250000 THEN 'sim' ELSE 'não' END AS metade_do_capital_perdida,
    a.parecer_auditor
FROM balanco_sad_rc b
LEFT JOIN auditoria a ON a.epoca_id = b.epoca_id
ORDER BY b.epoca_id;


-- @q 44. Partes relacionadas: fluxos entre o Clube e a SAD
SELECT
    epoca_id                                                                     AS epoca,
    SUM(CASE WHEN sentido = 'receita da SAD' THEN valor ELSE 0 END)              AS sad_cobra_quotas_e_lugares,
    SUM(CASE WHEN rubrica LIKE 'Rendas%' THEN valor ELSE 0 END)                  AS rendas_pagas_ao_clube,
    SUM(CASE WHEN rubrica LIKE 'Cedência%' THEN valor ELSE 0 END)                AS cedencia_pessoal,
    SUM(CASE WHEN rubrica = 'Saldo: Clube deve à SAD' THEN valor ELSE 0 END)     AS clube_deve_a_sad
FROM partes_relacionadas
GROUP BY epoca_id
ORDER BY epoca_id;


-- =====================================================================
-- APROFUNDAMENTO: POLÍTICA DESPORTIVA
-- =====================================================================


-- @q 45. Rácio de custos do plantel da UEFA, versão mais próxima do regulamento
-- Numerador: remunerações de jogadores e treinadores + amortizações de passes.
-- Denominador: receitas + média de 3 épocas do resultado com vendas de jogadores.
WITH base AS (
    SELECT
        p.epoca_id,
        p.rem_jogadores + p.rem_treinadores + j.amortizacoes          AS custos_plantel,
        k.vendas_servicos,
        AVG(t.mais_valias_liquidas) OVER (ORDER BY p.epoca_id
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)                 AS mais_valias_media_3
    FROM pessoal_sad p
    JOIN passes_jogadores j ON j.epoca_id = p.epoca_id
    JOIN v_kpis k           ON k.epoca_id = p.epoca_id AND k.entidade_id = 'SAD'
    LEFT JOIN transferencias t ON t.epoca_id = p.epoca_id AND t.entidade_id = 'SAD'
    WHERE p.rem_jogadores IS NOT NULL
)
SELECT
    epoca_id                                       AS epoca,
    custos_plantel,
    CAST(vendas_servicos + mais_valias_media_3 AS INTEGER) AS receitas_relevantes,
    ROUND(100.0 * custos_plantel / (vendas_servicos + mais_valias_media_3), 1) AS racio_pct,
    CASE WHEN 100.0 * custos_plantel / (vendas_servicos + mais_valias_media_3) <= 70 THEN 'cumpre 70%'
         WHEN 100.0 * custos_plantel / (vendas_servicos + mais_valias_media_3) <= 80 THEN 'acima de 70%, até 80%'
         ELSE 'acima de 80%' END                   AS leitura
FROM base
ORDER BY epoca_id;


-- @q 46. Intermediários e terceiros: quanto das vendas não fica no clube
SELECT
    t.epoca_id                                                    AS epoca,
    t.vendas_brutas,
    t.custo_vendas,
    ROUND(100.0 * t.custo_vendas / t.vendas_brutas, 1)            AS custo_vendas_pct,
    ROUND(100.0 * t.mais_valias_liquidas / t.vendas_brutas, 1)    AS retencao_pct
FROM transferencias t
WHERE t.entidade_id = 'SAD' AND t.custo_vendas IS NOT NULL
UNION ALL
SELECT 'dívida 30/06/2025', NULL, total, NULL, NULL
FROM divida WHERE credor = 'Intermediários desportivos'
ORDER BY 1;


-- @q 47. Mecanismo de solidariedade e compensação por formação
SELECT
    epoca_id                                                   AS epoca,
    valor                                                      AS solidariedade,
    ROUND(100.0 * valor / SUM(valor) OVER (), 1)               AS pct_do_total_do_periodo,
    SUM(valor) OVER (ORDER BY epoca_id)                        AS acumulado
FROM receitas_composicao
WHERE categoria = 'Mecanismo Solidariedade'
ORDER BY epoca_id;


-- @q 48. Centralização dos direitos TV: simulação por lugar na tabela (ilustrativa)
-- Contrato de 250 M€; 90% para 18 clubes; 33,2% igual; 44,2% por mérito, aqui
-- repartido de forma linear pela classificação (pesos 18 a 1). Exclui audiências.
WITH RECURSIVE lugar(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM lugar WHERE n < 18),
p AS (SELECT 250000000 * 0.90 AS pote)
SELECT
    n                                                          AS lugar,
    CAST(pote * 0.332 / 18 AS INTEGER)                         AS parte_igual,
    CAST(pote * 0.442 * (19 - n) / 171.0 AS INTEGER)           AS merito_ilustrativo,
    CAST(pote * 0.332 / 18 + pote * 0.442 * (19 - n) / 171.0 AS INTEGER) AS total_sem_audiencias,
    CAST(pote * 0.332 / 18 + pote * 0.442 * (19 - n) / 171.0 - 6922619 AS INTEGER) AS vs_tv_atual
FROM lugar, p
WHERE n BETWEEN 3 AND 12
ORDER BY n;


-- @q 49. Eficiência desportiva: quanto custa cada ponto
SELECT
    d.epoca_id                                                   AS epoca,
    d.pontos,
    d.posicao_liga                                               AS lugar,
    p.total_gastos_pessoal                                       AS gastos_pessoal,
    CAST(p.total_gastos_pessoal / d.pontos AS INTEGER)           AS custo_por_ponto,
    RANK() OVER (ORDER BY 1.0 * p.total_gastos_pessoal / d.pontos) AS ranking_eficiencia
FROM desempenho_desportivo d
JOIN pessoal_sad p ON p.epoca_id = d.epoca_id
WHERE d.epoca_id >= '2013/14'
ORDER BY d.epoca_id;


-- @q 50. Rotação de treinadores desde 2015
SELECT
    COUNT(*)                                             AS mudancas_desde_2015,
    SUM(CASE WHEN tipo = 'interino' THEN 1 ELSE 0 END)   AS interinos,
    COUNT(DISTINCT nome)                                 AS treinadores_diferentes,
    ROUND(COUNT(*) / 11.0, 1)                            AS media_por_epoca_2015_16_a_2025_26
FROM treinador
WHERE periodo NOT LIKE '2011%';


-- @q 51. Painel de indicadores financeiros da SAD
-- Margem corrente sem vendas = (receitas - pessoal - FSE) / receitas: o que a operação
-- gera antes de vender jogadores. A margem operacional já inclui as mais-valias.
SELECT
    d.epoca_id                                                                  AS epoca,
    ROUND(100.0 * (d.vendas_servicos + d.fse + d.gastos_pessoal) / d.vendas_servicos, 1) AS margem_corrente_sem_vendas_pct,
    ROUND(100.0 * d.resultado_operacional / d.vendas_servicos, 1)               AS margem_operacional_com_vendas_pct,
    ROUND(100.0 * d.resultado_liquido / b.ativo_total, 1)                       AS rendibilidade_ativo_pct,
    ROUND(1.0 * d.vendas_servicos / b.ativo_total, 2)                           AS rotacao_ativo,
    ROUND(100.0 * -d.fse / d.vendas_servicos, 1)                                AS fse_receitas_pct,
    ROUND(1.0 * (r.financiamentos_nc + r.financiamentos_c) / d.vendas_servicos, 2) AS divida_fin_receitas,
    ROUND(100.0 * c.operacional / d.vendas_servicos, 1)                         AS cash_flow_operacional_pct
FROM v_dr d
JOIN balanco b         ON b.entidade_id = 'SAD' AND b.epoca_id = d.epoca_id
LEFT JOIN balanco_sad_rc r ON r.epoca_id = d.epoca_id
LEFT JOIN cash_flow c  ON c.entidade_id = 'SAD' AND c.epoca_id = d.epoca_id
WHERE d.entidade_id = 'SAD' AND d.vendas_servicos IS NOT NULL AND d.epoca_id >= '2016/17'
ORDER BY d.epoca_id;


-- @q 52. Taxas de juro: o que o Vitória paga vs. referências de mercado
-- Médias por época (julho a junho). Spread = taxa implícita do Vitória - referência.
SELECT
    epoca_id                                            AS epoca,
    bce_deposito,
    euribor_12m,
    ot_portugal_10a,
    credito_empresas_pt,
    vitoria_implicita,
    ROUND(vitoria_implicita - euribor_12m, 1)           AS spread_vs_euribor,
    ROUND(vitoria_implicita - ot_portugal_10a, 1)       AS spread_vs_estado_portugues,
    ROUND(vitoria_implicita / NULLIF(ot_portugal_10a, 0), 1) AS vezes_estado_portugues
FROM v_taxas_epoca
WHERE epoca_id BETWEEN '2016/17' AND '2025/26'
ORDER BY epoca_id;


-- @q 53. Despesas da SAD vs. classificação: regressão linear (mínimos quadrados)
-- Despesas = gastos com pessoal + FSE + depreciações e amortizações.
-- Lugar previsto = a + b × despesas (em M€). O resíduo mostra quem ficou acima
-- (negativo = melhor lugar do que o previsto) ou abaixo do esperado.
WITH x AS (
    SELECT d.epoca_id,
           -(d.gastos_pessoal + d.fse + d.depreciacoes) / 1e6 AS despesas_m,
           s.posicao_liga AS lugar
    FROM v_dr d
    JOIN desempenho_desportivo s ON s.epoca_id = d.epoca_id
    WHERE d.entidade_id = 'SAD' AND d.gastos_pessoal IS NOT NULL AND d.fse IS NOT NULL
),
m AS (SELECT AVG(despesas_m) mx, AVG(lugar) my, COUNT(*) n FROM x),
reta AS (
    SELECT SUM((despesas_m - mx) * (lugar - my)) / SUM((despesas_m - mx) * (despesas_m - mx)) AS b,
           mx, my, n
    FROM x, m
),
ajuste AS (
    SELECT x.*, r.my - r.b * r.mx + r.b * x.despesas_m AS previsto, r.b, r.mx, r.my, r.n
    FROM x, reta r
),
r2 AS (
    SELECT 1 - SUM((lugar - previsto) * (lugar - previsto)) / SUM((lugar - my) * (lugar - my)) AS r2
    FROM ajuste
)
SELECT
    a.epoca_id                                   AS epoca,
    ROUND(a.despesas_m, 1)                       AS despesas_m,
    a.lugar,
    ROUND(a.previsto, 1)                         AS lugar_previsto,
    ROUND(a.lugar - a.previsto, 1)               AS residuo,
    ROUND(a.my - a.b * a.mx, 2)                  AS a_ordenada,
    ROUND(a.b, 3)                                AS b_declive_por_m,
    ROUND(r2.r2, 2)                              AS r_quadrado,
    a.n
FROM ajuste a, r2
ORDER BY a.epoca_id;


-- @q 54. Vendas de jogadores face às receitas, ao longo do tempo
-- Quanto valem as vendas (brutas) e as mais-valias em comparação com as receitas
-- da operação (vendas e serviços).
SELECT
    t.epoca_id                                                         AS epoca,
    d.vendas_servicos                                                  AS receitas_operacao,
    t.vendas_brutas,
    t.mais_valias_liquidas,
    ROUND(1.0 * t.vendas_brutas / d.vendas_servicos, 2)                AS vendas_por_euro_de_receita,
    ROUND(100.0 * t.mais_valias_liquidas
          / (d.vendas_servicos + t.mais_valias_liquidas), 1)           AS peso_mais_valias_no_total_pct,
    ROUND(AVG(1.0 * t.vendas_brutas / d.vendas_servicos)
          OVER (ORDER BY t.epoca_id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS media_movel_3_epocas
FROM transferencias t
JOIN v_dr d ON d.epoca_id = t.epoca_id AND d.entidade_id = 'SAD'
WHERE t.entidade_id = 'SAD' AND d.vendas_servicos IS NOT NULL
ORDER BY t.epoca_id;


-- @q 55. Centralização dos direitos TV: quanto reduz a dependência das vendas
-- Défice antes de vendas = média das três últimas épocas (2022/23 a 2024/25) do
-- resultado líquido sem mais-valias. Cenários de contrato (200, 250, 300 M€) e de
-- lugar (4.º, 6.º, 9.º), com a mesma repartição ilustrativa da consulta 48.
WITH base AS (
    SELECT AVG(rl_sem_mais_valias) AS defice
    FROM v_kpis
    WHERE entidade_id = 'SAD' AND epoca_id BETWEEN '2022/23' AND '2024/25'
),
tv AS (SELECT valor AS tv_atual FROM receitas_composicao
       WHERE categoria = 'Direitos TV' AND epoca_id = '2024/25'),
cenario(contrato) AS (VALUES (200000000), (250000000), (300000000)),
lugar(n) AS (VALUES (4), (6), (9)),
sim AS (
    SELECT contrato, n,
           contrato * 0.90 * 0.332 / 18 + contrato * 0.90 * 0.442 * (19 - n) / 171.0 AS tv_centralizada
    FROM cenario, lugar
)
SELECT
    CAST(contrato / 1e6 AS INTEGER) || ' M€'                       AS contrato,
    n || '.º'                                                      AS lugar,
    CAST(tv_centralizada AS INTEGER)                               AS tv_centralizada,
    CAST(tv_centralizada - tv_atual AS INTEGER)                    AS ganho_vs_atual,
    CAST(base.defice AS INTEGER)                                   AS defice_antes_vendas,
    CAST(-(base.defice + tv_centralizada - tv_atual) AS INTEGER)   AS mais_valias_necessarias,
    ROUND(100.0 * (tv_centralizada - tv_atual) / -base.defice, 1)  AS pct_do_defice_coberto
FROM sim, base, tv
ORDER BY contrato, n;
