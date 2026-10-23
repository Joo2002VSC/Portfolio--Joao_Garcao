-- =====================================================================
-- 03_vistas.sql : vistas reutilizáveis
-- =====================================================================

DROP VIEW IF EXISTS v_kpis;
DROP VIEW IF EXISTS v_resultado_por_entidade;
DROP VIEW IF EXISTS v_dr;

-- Demonstração de resultados em formato largo (pivot com CASE)
CREATE VIEW v_dr AS
SELECT
    entidade_id,
    epoca_id,
    MAX(CASE WHEN rubrica_id = 'vendas_servicos'           THEN valor END) AS vendas_servicos,
    MAX(CASE WHEN rubrica_id = 'rendimentos_operacionais'  THEN valor END) AS rendimentos_operacionais,
    MAX(CASE WHEN rubrica_id = 'outros_rendimentos'        THEN valor END) AS outros_rendimentos,
    MAX(CASE WHEN rubrica_id = 'fse'                       THEN valor END) AS fse,
    MAX(CASE WHEN rubrica_id = 'gastos_pessoal'            THEN valor END) AS gastos_pessoal,
    MAX(CASE WHEN rubrica_id = 'depreciacoes'              THEN valor END) AS depreciacoes,
    MAX(CASE WHEN rubrica_id = 'ebitda'                    THEN valor END) AS ebitda,
    MAX(CASE WHEN rubrica_id = 'ebitda_sem_transferencias' THEN valor END) AS ebitda_sem_transferencias,
    MAX(CASE WHEN rubrica_id = 'resultado_operacional'     THEN valor END) AS resultado_operacional,
    MAX(CASE WHEN rubrica_id = 'juros'                     THEN valor END) AS juros,
    MAX(CASE WHEN rubrica_id = 'resultado_liquido'         THEN valor END) AS resultado_liquido
FROM demonstracao_resultados
GROUP BY entidade_id, epoca_id;

-- Resultado líquido das três entidades lado a lado
CREATE VIEW v_resultado_por_entidade AS
SELECT
    e.epoca_id,
    MAX(CASE WHEN d.entidade_id = 'SAD'         THEN d.resultado_liquido END) AS rl_sad,
    MAX(CASE WHEN d.entidade_id = 'CLUBE'       THEN d.resultado_liquido END) AS rl_clube,
    MAX(CASE WHEN d.entidade_id = 'CONSOLIDADO' THEN d.resultado_liquido END) AS rl_consolidado
FROM epoca e
LEFT JOIN v_dr d ON d.epoca_id = e.epoca_id
GROUP BY e.epoca_id;

-- Indicadores principais por entidade e época
CREATE VIEW v_kpis AS
SELECT
    d.entidade_id,
    d.epoca_id,
    d.vendas_servicos,
    -d.gastos_pessoal                                   AS gastos_pessoal,
    d.resultado_liquido,
    t.mais_valias_liquidas,
    d.resultado_liquido - t.mais_valias_liquidas        AS rl_sem_mais_valias,
    ROUND(100.0 * -d.gastos_pessoal / d.vendas_servicos, 1) AS pct_pessoal_receitas,
    -d.juros                                            AS juros,
    b.ativo_total,
    b.passivo_total,
    b.capital_proprio,
    b.caixa
FROM v_dr d
LEFT JOIN balanco b
       ON b.entidade_id = d.entidade_id AND b.epoca_id = d.epoca_id
LEFT JOIN transferencias t
       ON t.entidade_id = d.entidade_id AND t.epoca_id = d.epoca_id;


-- Taxas de juro por época (julho a junho): referências de mercado e taxa
-- implícita da dívida da SAD. A taxa do BCE é ponderada pelos dias em vigor.
CREATE VIEW v_taxas_epoca AS
WITH bce AS (
    SELECT data_efeito AS inicio,
           LEAD(data_efeito, 1, '2099-12-31') OVER (ORDER BY data_efeito) AS fim,
           facilidade_deposito
    FROM bce_taxa
),
bce_epoca AS (
    SELECT e.epoca_id,
           SUM(b.facilidade_deposito *
               MAX(0, MIN(julianday(e.ano_fim || '-07-01'), julianday(b.fim))
                    - MAX(julianday(e.ano_inicio || '-07-01'), julianday(b.inicio))))
           / (julianday(e.ano_fim || '-07-01') - julianday(e.ano_inicio || '-07-01')) AS bce_deposito
    FROM epoca e, bce b
    GROUP BY e.epoca_id
),
mercado AS (
    SELECT CASE WHEN CAST(strftime('%m', data) AS INTEGER) >= 7
                THEN strftime('%Y', data) || '/' || substr(CAST(strftime('%Y', data) + 1 AS TEXT), 3)
                ELSE CAST(strftime('%Y', data) - 1 AS TEXT) || '/' || substr(strftime('%Y', data), 3)
           END AS epoca_id,
           indicador, taxa_pct
    FROM taxa_referencia
),
med AS (
    SELECT epoca_id,
           AVG(CASE WHEN indicador = 'euribor_12m' THEN taxa_pct END)         AS euribor_12m,
           AVG(CASE WHEN indicador = 'ot_portugal_10a' THEN taxa_pct END)     AS ot_portugal_10a,
           AVG(CASE WHEN indicador = 'credito_empresas_pt' THEN taxa_pct END) AS credito_empresas_pt,
           COUNT(CASE WHEN indicador = 'euribor_12m' THEN 1 END)              AS meses_euribor
    FROM mercado
    GROUP BY epoca_id
),
divida AS (
    SELECT epoca_id,
           juros_suportados,
           financiamentos_nc + financiamentos_c AS financiamentos,
           LAG(financiamentos_nc + financiamentos_c) OVER (ORDER BY epoca_id) AS fin_anterior
    FROM balanco_sad_rc
    WHERE financiamentos_nc IS NOT NULL
)
SELECT
    m.epoca_id,
    ROUND(b.bce_deposito, 2)                           AS bce_deposito,
    ROUND(m.euribor_12m, 2)                            AS euribor_12m,
    ROUND(m.ot_portugal_10a, 2)                        AS ot_portugal_10a,
    ROUND(m.credito_empresas_pt, 2)                    AS credito_empresas_pt,
    ROUND(100.0 * d.juros_suportados / ((d.financiamentos + d.fin_anterior) / 2.0), 2) AS vitoria_implicita,
    m.meses_euribor
FROM med m
JOIN bce_epoca b ON b.epoca_id = m.epoca_id
LEFT JOIN divida d ON d.epoca_id = m.epoca_id;
