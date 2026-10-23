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
