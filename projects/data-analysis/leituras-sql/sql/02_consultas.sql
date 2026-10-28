-- =============================================================
--  Análise das minhas leituras — consultas SQL (SQLite)
--  Cada bloco começa com "-- @ Título" para o script scripts/gerar_resultados.py
-- =============================================================

-- @ 1. Visão geral da biblioteca por estante
SELECT
    l.estante,
    COUNT(*)                         AS livros,
    SUM(b.paginas)                   AS paginas,
    ROUND(AVG(b.paginas))            AS media_paginas
FROM leituras l
JOIN livros b USING (livro_id)
GROUP BY l.estante
ORDER BY livros DESC;

-- @ 2. Livros e páginas lidos por ano
SELECT
    strftime('%Y', data_lida)        AS ano,
    COUNT(*)                         AS livros,
    SUM(b.paginas)                   AS paginas,
    ROUND(AVG(b.paginas))            AS media_paginas,
    ROUND(AVG(l.nota), 2)            AS nota_media
FROM leituras l
JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND l.data_lida IS NOT NULL
GROUP BY ano
ORDER BY ano;

-- @ 3. 2026 mês a mês (o mesmo período do blog)
SELECT
    strftime('%m', data_lida)        AS mes,
    COUNT(*)                         AS livros,
    SUM(b.paginas)                   AS paginas,
    GROUP_CONCAT(b.titulo, ' · ')    AS titulos
FROM leituras l
JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND strftime('%Y', data_lida) = '2026'
GROUP BY mes
ORDER BY mes;

-- @ 4. Ritmo acumulado: 2025 vs 2026 (window function)
WITH por_mes AS (
    SELECT strftime('%m', data_lida) AS mes,
           SUM(strftime('%Y', data_lida) = '2025') AS l2025,
           SUM(strftime('%Y', data_lida) = '2026') AS l2026
    FROM leituras
    WHERE estante = 'read' AND strftime('%Y', data_lida) IN ('2025','2026')
    GROUP BY mes
)
SELECT mes,
       SUM(l2025) OVER (ORDER BY mes) AS acumulado_2025,
       CASE WHEN mes <= strftime('%m', 'now')          -- meses de 2026 ainda por vir ficam vazios
            THEN SUM(l2026) OVER (ORDER BY mes) END AS acumulado_2026
FROM por_mes
ORDER BY mes;

-- @ 5. Distribuição das minhas notas
SELECT
    CASE
        WHEN nota >= 4.75 THEN '5 ★'
        WHEN nota >= 4    THEN '4 a 4,5 ★'
        WHEN nota >= 3    THEN '3 a 3,75 ★'
        ELSE                   'menos de 3 ★'
    END                              AS faixa,
    COUNT(*)                         AS livros,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percentagem
FROM leituras
WHERE estante = 'read' AND nota IS NOT NULL
GROUP BY faixa
ORDER BY MIN(nota) DESC;

-- @ 6. Autores mais lidos
SELECT
    a.nome                           AS autor,
    COUNT(*)                         AS livros_lidos,
    SUM(b.paginas)                   AS paginas,
    ROUND(AVG(l.nota), 2)            AS nota_media
FROM leituras l
JOIN livros  b USING (livro_id)
JOIN autores a USING (autor_id)
WHERE l.estante = 'read'
GROUP BY a.autor_id
HAVING COUNT(*) >= 2
ORDER BY livros_lidos DESC, nota_media DESC;

-- @ 7. Livros com nota máxima e favoritos
SELECT
    b.titulo, a.nome AS autor, l.nota,
    CASE l.favorito WHEN 1 THEN 'sim' ELSE '' END AS favorito
FROM leituras l
JOIN livros  b USING (livro_id)
JOIN autores a USING (autor_id)
WHERE l.estante = 'read' AND (l.nota = 5 OR l.favorito = 1)
ORDER BY l.nota DESC, b.titulo;

-- @ 8. De que época são os livros que leio? (ano da 1.ª publicação)
SELECT
    CASE
        WHEN ano_original < 1800 THEN 'Antes de 1800'
        WHEN ano_original < 1900 THEN 'Século XIX'
        WHEN ano_original < 1950 THEN '1900–1949'
        WHEN ano_original < 2000 THEN '1950–1999'
        WHEN ano_original < 2015 THEN '2000–2014'
        ELSE                          '2015 até hoje'
    END                              AS epoca,
    COUNT(*)                         AS livros,
    ROUND(AVG(l.nota), 2)            AS nota_media
FROM leituras l
JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND b.ano_original IS NOT NULL
GROUP BY epoca
ORDER BY MIN(ano_original);

-- @ 9. A extensão do livro influencia a nota?
SELECT
    CASE
        WHEN paginas < 150 THEN 'a) menos de 150'
        WHEN paginas < 300 THEN 'b) 150–299'
        WHEN paginas < 450 THEN 'c) 300–449'
        ELSE                    'd) 450 ou mais'
    END                              AS paginas,
    COUNT(*)                         AS livros,
    ROUND(AVG(l.nota), 2)            AS nota_media
FROM leituras l
JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND b.paginas IS NOT NULL AND l.nota IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- @ 10. Os extremos: livros mais longo e mais curto que li
SELECT 'mais longo' AS tipo, titulo, paginas FROM (
    SELECT b.titulo, b.paginas FROM leituras l JOIN livros b USING (livro_id)
    WHERE l.estante = 'read' AND b.paginas IS NOT NULL
    ORDER BY b.paginas DESC LIMIT 3)
UNION ALL
SELECT 'mais curto', titulo, paginas FROM (
    SELECT b.titulo, b.paginas FROM leituras l JOIN livros b USING (livro_id)
    WHERE l.estante = 'read' AND b.paginas IS NOT NULL
    ORDER BY b.paginas ASC LIMIT 3);

-- @ 11. Editoras que mais aparecem nas minhas leituras
SELECT
    -- junta variantes do mesmo nome ("Publicações Dom Quixote" = "Dom Quixote")
    TRIM(REPLACE(b.editora, 'Publicações ', '')) AS editora,
    COUNT(*)                         AS livros
FROM leituras l
JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND b.editora IS NOT NULL
GROUP BY 1
HAVING COUNT(*) >= 3
ORDER BY livros DESC;

-- @ 12. Quanto tempo esperam os livros na estante antes de serem lidos?
SELECT
    COUNT(*)                                            AS livros,
    ROUND(AVG(julianday(data_lida) - julianday(data_adicionado))) AS media_dias,
    SUM(julianday(data_lida) - julianday(data_adicionado) <= 30)  AS lidos_no_1o_mes
FROM leituras
WHERE estante = 'read'
  AND data_lida IS NOT NULL
  AND data_lida >= data_adicionado;   -- exclui livros adicionados depois de lidos

-- @ 13. A pilha "para ler": quanto tempo levaria a acabá-la?
WITH ritmo AS (
    SELECT COUNT(*) * 1.0 / 12 AS livros_por_mes
    FROM leituras
    WHERE estante = 'read'
      AND data_lida >= date('now', '-12 months')   -- últimos 12 meses
)
SELECT
    COUNT(*)                                 AS livros_para_ler,
    SUM(b.paginas)                           AS paginas,
    ROUND((SELECT livros_por_mes FROM ritmo), 1) AS ritmo_livros_mes,
    ROUND(COUNT(*) / (SELECT livros_por_mes FROM ritmo) / 12, 1) AS anos_necessarios
FROM leituras l
JOIN livros b USING (livro_id)
WHERE l.estante = 'to-read';
