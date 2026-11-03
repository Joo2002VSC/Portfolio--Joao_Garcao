-- =====================================================================
-- indicadores_dashboard.sql : consultas complementares do painel
-- Correm sobre a mesma base (vsc_contas.db) que as consultas do projeto
-- contas-vitoria-sql. Não alteram dados: calculam rácios e comparações
-- que o painel apresenta. Cada consulta começa com "-- @d D<n>. Título".
-- Divisões protegidas com NULLIF; valores em falta ficam NULL.
-- =====================================================================


-- @d D1. Rácios de estrutura da SAD: autonomia, solvabilidade e endividamento
-- Conceitos: NULLIF contra divisões por zero, CASE, colunas calculadas
-- Autonomia financeira = capitais próprios / ativo
-- Solvabilidade        = capitais próprios / passivo
-- Endividamento        = passivo / ativo
SELECT
    epoca_id                                                      AS epoca,
    ativo_total,
    passivo_total,
    capital_proprio,
    ROUND(100.0 * capital_proprio / NULLIF(ativo_total, 0), 1)    AS autonomia_pct,
    ROUND(100.0 * capital_proprio / NULLIF(passivo_total, 0), 1)  AS solvabilidade_pct,
    ROUND(1.0 * passivo_total / NULLIF(ativo_total, 0), 2)        AS endividamento,
    CASE WHEN capital_proprio < 0 THEN 'capitais próprios negativos'
         WHEN capital_proprio IS NULL THEN 'sem dados'
         ELSE 'capitais próprios positivos' END                      AS leitura
FROM balanco
WHERE entidade_id = 'SAD' AND ativo_total IS NOT NULL AND passivo_total IS NOT NULL
ORDER BY epoca_id;


-- @d D2. Resultado operacional e resultado líquido da SAD, com e sem mais-valias
-- Conceitos: LEFT JOIN entre vista e tabela, colunas calculadas
-- Resultado operacional sem mais-valias = resultado operacional - mais-valias líquidas
SELECT
    d.epoca_id                                              AS epoca,
    d.resultado_operacional,
    d.resultado_liquido,
    t.mais_valias_liquidas,
    d.resultado_operacional - t.mais_valias_liquidas        AS ro_sem_mais_valias,
    d.resultado_liquido - d.resultado_operacional           AS financeiro_e_impostos
FROM v_dr d
LEFT JOIN transferencias t ON t.entidade_id = d.entidade_id AND t.epoca_id = d.epoca_id
WHERE d.entidade_id = 'SAD' AND d.resultado_operacional IS NOT NULL
ORDER BY d.epoca_id;


-- @d D3. Peso dos gastos com pessoal nos rendimentos operacionais da SAD
-- Conceitos: CTE, agregação condicional SUM(CASE ...), NULLIF
-- Rendimentos operacionais = vendas e serviços prestados + subsídios à exploração + outros rendimentos
-- (a rubrica agregada só existe numa época, por isso soma-se como na consulta 57).
-- "Outros rendimentos" inclui os ganhos com a alienação de passes.
WITH r AS (
    SELECT epoca_id,
           SUM(CASE WHEN rubrica_id = 'vendas_servicos' THEN valor END)                 AS vendas_servicos,
           SUM(CASE WHEN rubrica_id IN ('vendas_servicos', 'subsidios_exploracao',
                                        'outros_rendimentos') THEN valor END)           AS rendimentos_operacionais,
           -SUM(CASE WHEN rubrica_id = 'gastos_pessoal' THEN valor END)                 AS pessoal
    FROM demonstracao_resultados
    WHERE entidade_id = 'SAD'
    GROUP BY epoca_id
)
SELECT
    epoca_id                                                         AS epoca,
    pessoal,
    vendas_servicos,
    rendimentos_operacionais,
    ROUND(100.0 * pessoal / NULLIF(vendas_servicos, 0), 1)           AS pessoal_sobre_vendas_pct,
    ROUND(100.0 * pessoal / NULLIF(rendimentos_operacionais, 0), 1)  AS pessoal_sobre_rendimentos_pct
FROM r
WHERE pessoal IS NOT NULL AND vendas_servicos IS NOT NULL
ORDER BY epoca_id;


-- @d D4. Variação face à época anterior, por indicador (SAD)
-- Conceitos: UNION ALL para formato longo, LAG com PARTITION BY, NULLIF
WITH longo AS (
    SELECT epoca_id, 'Ativo' AS indicador, ativo_total AS valor FROM balanco WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Passivo', passivo_total FROM balanco WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Capitais próprios', capital_proprio FROM balanco WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Resultado líquido', resultado_liquido FROM v_dr WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Vendas e serviços prestados', vendas_servicos FROM v_dr WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Gastos com pessoal', -gastos_pessoal FROM v_dr WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Mais-valias com jogadores', mais_valias_liquidas FROM transferencias WHERE entidade_id = 'SAD'
),
com_anterior AS (
    SELECT epoca_id, indicador, valor,
           LAG(valor)    OVER (PARTITION BY indicador ORDER BY epoca_id) AS anterior,
           LAG(epoca_id) OVER (PARTITION BY indicador ORDER BY epoca_id) AS epoca_anterior
    FROM longo
    WHERE valor IS NOT NULL
)
SELECT
    epoca_id                                                      AS epoca,
    indicador,
    valor,
    anterior,
    epoca_anterior,
    valor - anterior                                              AS variacao,
    ROUND(100.0 * (valor - anterior) / NULLIF(ABS(anterior), 0), 1) AS variacao_pct
FROM com_anterior
ORDER BY indicador, epoca_id;


-- @d D5. Máximos e mínimos históricos por indicador (SAD)
-- Conceitos: CTE, ROW_NUMBER com PARTITION BY, COUNT() OVER
WITH longo AS (
    SELECT epoca_id, 'Ativo' AS indicador, ativo_total AS valor FROM balanco WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Passivo', passivo_total FROM balanco WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Capitais próprios', capital_proprio FROM balanco WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Resultado líquido', resultado_liquido FROM v_dr WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Vendas e serviços prestados', vendas_servicos FROM v_dr WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Gastos com pessoal', -gastos_pessoal FROM v_dr WHERE entidade_id = 'SAD'
    UNION ALL SELECT epoca_id, 'Mais-valias com jogadores', mais_valias_liquidas FROM transferencias WHERE entidade_id = 'SAD'
),
ordenado AS (
    SELECT indicador, epoca_id, valor,
           ROW_NUMBER() OVER (PARTITION BY indicador ORDER BY valor DESC) AS pos_max,
           ROW_NUMBER() OVER (PARTITION BY indicador ORDER BY valor ASC)  AS pos_min,
           COUNT(*)     OVER (PARTITION BY indicador)                     AS n_epocas
    FROM longo
    WHERE valor IS NOT NULL
)
SELECT
    indicador,
    n_epocas,
    MAX(CASE WHEN pos_max = 1 THEN epoca_id END)        AS epoca_maximo,
    MAX(CASE WHEN pos_max = 1 THEN valor END)           AS maximo,
    MAX(CASE WHEN pos_min = 1 THEN epoca_id END)        AS epoca_minimo,
    MAX(CASE WHEN pos_min = 1 THEN valor END)           AS minimo
FROM ordenado
GROUP BY indicador, n_epocas
ORDER BY indicador;


-- @d D6. Rentabilidade da SAD: resultado antes de impostos e margens
-- Conceitos: CTE, agregação condicional SUM(CASE ...), NULLIF, colunas calculadas
-- Resultado antes de impostos = resultado líquido - imposto (o imposto é registado com sinal negativo)
-- Margem operacional = resultado operacional / rendimentos operacionais
-- Margem líquida     = resultado líquido / rendimentos operacionais
WITH r AS (
    SELECT epoca_id,
           SUM(CASE WHEN rubrica_id IN ('vendas_servicos', 'subsidios_exploracao',
                                        'outros_rendimentos') THEN valor END)   AS rendimentos_operacionais,
           SUM(CASE WHEN rubrica_id = 'resultado_operacional' THEN valor END)   AS resultado_operacional,
           SUM(CASE WHEN rubrica_id = 'imposto' THEN valor END)                 AS imposto,
           SUM(CASE WHEN rubrica_id = 'resultado_liquido' THEN valor END)       AS resultado_liquido
    FROM demonstracao_resultados
    WHERE entidade_id = 'SAD'
    GROUP BY epoca_id
)
SELECT
    epoca_id                                                                     AS epoca,
    rendimentos_operacionais,
    resultado_operacional,
    resultado_liquido - imposto                                                  AS resultado_antes_impostos,
    resultado_liquido,
    ROUND(100.0 * resultado_operacional / NULLIF(rendimentos_operacionais, 0), 1) AS margem_operacional_pct,
    ROUND(100.0 * resultado_liquido / NULLIF(rendimentos_operacionais, 0), 1)     AS margem_liquida_pct
FROM r
WHERE rendimentos_operacionais IS NOT NULL AND resultado_operacional IS NOT NULL
ORDER BY epoca_id;
