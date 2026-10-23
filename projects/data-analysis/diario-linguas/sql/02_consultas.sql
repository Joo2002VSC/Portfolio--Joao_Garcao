-- =============================================================
--  Diário de Aprendizagem de Línguas — Consultas de análise
--  Executar com:  sqlite3 dados/diario.db < sql/02_consultas.sql
--  (ou abrir no DB Browser for SQLite e correr uma a uma)
-- =============================================================

.headers on
.mode column


-- -------------------------------------------------------------
-- P1. Quantas palavras novas aprendo por semana, em cada língua?
--     Semana começa à segunda-feira.
-- -------------------------------------------------------------
SELECT  date(p.data_adicionada, 'weekday 0', '-6 days') AS semana,
        i.nome                                          AS idioma,
        COUNT(*)                                        AS palavras_novas
FROM palavras p
JOIN idiomas  i ON i.id = p.idioma_id
GROUP BY semana, i.nome
ORDER BY semana, i.nome;


-- Média semanal por língua — conta TODAS as semanas do período,
-- incluindo as semanas sem palavras novas (senão a média fica inflacionada)
WITH semanas AS (
    SELECT COUNT(DISTINCT date(data, 'weekday 0', '-6 days')) AS n
    FROM sessoes
)
SELECT  i.nome                                   AS idioma,
        COUNT(p.id)                              AS total_palavras,
        ROUND(1.0 * COUNT(p.id) / semanas.n, 1)  AS media_por_semana
FROM idiomas i
LEFT JOIN palavras p ON p.idioma_id = i.id
CROSS JOIN semanas
GROUP BY i.id
ORDER BY media_por_semana DESC;


-- -------------------------------------------------------------
-- P2. Que língua tenho negligenciado?
--     Dias desde a última sessão + minutos nos últimos 30 dias
--     comparados com a média mensal do período inteiro.
-- -------------------------------------------------------------
WITH hoje AS (SELECT MAX(data) AS d FROM sessoes),
resumo AS (
    SELECT  s.idioma_id,
            MAX(s.data)                                              AS ultima_sessao,
            SUM(CASE WHEN s.data > date(hoje.d, '-30 days')
                     THEN s.duracao_min ELSE 0 END)                  AS min_ultimos_30d,
            ROUND(SUM(s.duracao_min) * 30.0 /
                  (julianday(hoje.d) - julianday(MIN(s.data)) + 1))  AS media_30d_historica
    FROM sessoes s CROSS JOIN hoje
    GROUP BY s.idioma_id
)
SELECT  i.nome                                                     AS idioma,
        r.ultima_sessao,
        CAST(julianday(hoje.d) - julianday(r.ultima_sessao) AS INT) AS dias_sem_estudar,
        r.min_ultimos_30d,
        r.media_30d_historica,
        CASE
            WHEN julianday(hoje.d) - julianday(r.ultima_sessao) > 14 THEN '🔴 abandonada'
            WHEN r.min_ultimos_30d < 0.5 * r.media_30d_historica      THEN '🟠 a abrandar'
            ELSE '🟢 em dia'
        END                                                        AS estado
FROM resumo r
JOIN idiomas i ON i.id = r.idioma_id
CROSS JOIN hoje
ORDER BY dias_sem_estudar DESC;


-- -------------------------------------------------------------
-- P3. Que palavras erro mais vezes?
--     Mínimo de 4 revisões para a taxa de erro ser significativa.
-- -------------------------------------------------------------
SELECT  idioma, termo, traducao_pt, tema, revisoes, erros, taxa_erro_pct
FROM v_desempenho_palavras
WHERE revisoes >= 4
ORDER BY taxa_erro_pct DESC, erros DESC
LIMIT 15;


-- =============================================================
--  Consultas extra
-- =============================================================

-- E1. Temas mais difíceis por língua (taxa de erro média)
SELECT  idioma,
        tema,
        SUM(revisoes)                                   AS revisoes,
        ROUND(100.0 * SUM(erros) / SUM(revisoes), 1)    AS taxa_erro_pct
FROM v_desempenho_palavras
WHERE revisoes > 0
GROUP BY idioma, tema
HAVING SUM(revisoes) >= 15
ORDER BY idioma, taxa_erro_pct DESC;


-- E2. Minutos por mês e por língua
SELECT  strftime('%Y-%m', s.data) AS mes,
        i.nome                    AS idioma,
        SUM(s.duracao_min)        AS minutos,
        COUNT(*)                  AS sessoes
FROM sessoes s
JOIN idiomas i ON i.id = s.idioma_id
GROUP BY mes, i.nome
ORDER BY mes, i.nome;


-- E3. Como uso o tempo? Distribuição por tipo de sessão
SELECT  i.nome AS idioma,
        s.tipo,
        SUM(s.duracao_min) AS minutos,
        ROUND(100.0 * SUM(s.duracao_min) /
              SUM(SUM(s.duracao_min)) OVER (PARTITION BY i.nome), 1) AS pct_do_idioma
FROM sessoes s
JOIN idiomas i ON i.id = s.idioma_id
GROUP BY i.nome, s.tipo
ORDER BY i.nome, minutos DESC;


-- E4. Vocabulário acumulado ao longo do tempo (função de janela)
SELECT  i.nome AS idioma,
        p.data_adicionada AS data,
        COUNT(*) AS novas_no_dia,
        SUM(COUNT(*)) OVER (PARTITION BY i.nome ORDER BY p.data_adicionada) AS total_acumulado
FROM palavras p
JOIN idiomas i ON i.id = p.idioma_id
GROUP BY i.nome, p.data_adicionada
ORDER BY i.nome, data;


-- E5. Maior sequência de dias seguidos a estudar (qualquer língua)
--     Técnica "gaps and islands": data - nº da linha = constante numa sequência
WITH dias AS (
    SELECT DISTINCT data FROM sessoes
),
grupos AS (
    SELECT data,
           julianday(data) - ROW_NUMBER() OVER (ORDER BY data) AS grupo
    FROM dias
)
SELECT  MIN(data) AS inicio,
        MAX(data) AS fim,
        COUNT(*)  AS dias_seguidos
FROM grupos
GROUP BY grupo
ORDER BY dias_seguidos DESC
LIMIT 5;


-- E6. A revisão funciona? Taxa de erro conforme o nº de vezes que a palavra já foi revista
WITH numeradas AS (
    SELECT  r.*,
            ROW_NUMBER() OVER (PARTITION BY r.palavra_id ORDER BY r.data, r.id) AS n_revisao
    FROM revisoes r
)
SELECT  CASE WHEN n_revisao >= 8 THEN '8+' ELSE CAST(n_revisao AS TEXT) END AS revisao_n,
        COUNT(*)                                      AS tentativas,
        ROUND(100.0 * SUM(1 - acertou) / COUNT(*), 1) AS taxa_erro_pct
FROM numeradas
GROUP BY revisao_n
ORDER BY MIN(n_revisao);
