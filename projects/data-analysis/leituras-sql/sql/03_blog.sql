-- =============================================================
--  Consultas que alimentam a página "Em Números" do blog
--  Cada bloco "-- @ chave" vira uma entrada em assets/dados/estatisticas.js
--  (scripts/exportar_blog.py). A data de referência é a do registo mais
--  recente no CSV, para que os números não mudem só porque o tempo passou.
-- =============================================================

-- @ referencia
SELECT MAX(d)                          AS data,
       CAST(strftime('%Y', MAX(d)) AS INT) AS ano,
       CAST(strftime('%m', MAX(d)) AS INT) AS mes
FROM (SELECT data_lida AS d FROM leituras UNION ALL SELECT data_adicionado FROM leituras);

-- @ resumo
WITH ref AS (SELECT strftime('%Y', MAX(d)) AS ano
             FROM (SELECT data_lida AS d FROM leituras UNION ALL SELECT data_adicionado FROM leituras))
SELECT
    COUNT(*)                                                    AS livros_lidos,
    SUM(b.paginas)                                              AS paginas,
    COUNT(DISTINCT b.autor_id)                                  AS autores,
    ROUND(AVG(l.nota), 2)                                       AS nota_media,
    SUM(strftime('%Y', l.data_lida) = (SELECT ano FROM ref))    AS lidos_ano_atual,
    SUM(strftime('%Y', l.data_lida) = CAST((SELECT ano FROM ref) - 1 AS TEXT)) AS lidos_ano_anterior,
    SUM(CASE WHEN strftime('%Y', l.data_lida) = (SELECT ano FROM ref)
             THEN b.paginas END)                                AS paginas_ano_atual
FROM leituras l
JOIN livros b USING (livro_id)
WHERE l.estante = 'read';

-- @ por_ano
SELECT CAST(strftime('%Y', data_lida) AS INT) AS ano,
       COUNT(*)                               AS livros,
       SUM(b.paginas)                         AS paginas
FROM leituras l JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND l.data_lida IS NOT NULL
GROUP BY ano ORDER BY ano;

-- @ por_mes
-- livros lidos por mês nos dois últimos anos, com os títulos (para o tooltip)
SELECT CAST(strftime('%Y', data_lida) AS INT) AS ano,
       CAST(strftime('%m', data_lida) AS INT) AS mes,
       COUNT(*)                               AS livros,
       GROUP_CONCAT(b.livro_id, ',')          AS ids
FROM leituras l JOIN livros b USING (livro_id)
WHERE l.estante = 'read'
  AND strftime('%Y', data_lida) >= (SELECT CAST(strftime('%Y', MAX(data_lida)) - 1 AS TEXT) FROM leituras)
GROUP BY ano, mes ORDER BY ano, mes;

-- @ notas
-- as notas fracionadas do Goodreads arredondadas à meia estrela (4,25 -> 4,5), como no blog
SELECT CAST(nota AS INT) + CASE WHEN nota - CAST(nota AS INT) >= 0.25 THEN 0.5 ELSE 0 END AS estrelas,
       COUNT(*) AS livros
FROM leituras
WHERE estante = 'read' AND nota IS NOT NULL
GROUP BY estrelas ORDER BY estrelas;

-- @ autores
SELECT a.nome AS autor, COUNT(*) AS livros, ROUND(AVG(l.nota), 2) AS nota_media
FROM leituras l JOIN livros b USING (livro_id) JOIN autores a USING (autor_id)
WHERE l.estante = 'read'
GROUP BY a.autor_id
HAVING COUNT(*) >= 2
ORDER BY livros DESC, nota_media DESC
LIMIT 10;

-- @ epocas
SELECT CASE
         WHEN ano_original < 1800 THEN 'Antes de 1800'
         WHEN ano_original < 1900 THEN 'Século XIX'
         WHEN ano_original < 1950 THEN '1900–1949'
         WHEN ano_original < 2000 THEN '1950–1999'
         WHEN ano_original < 2015 THEN '2000–2014'
         ELSE '2015 até hoje' END       AS epoca,
       COUNT(*)                         AS livros,
       ROUND(AVG(l.nota), 2)            AS nota_media
FROM leituras l JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND b.ano_original IS NOT NULL
GROUP BY epoca ORDER BY MIN(ano_original);

-- @ extensao
SELECT CASE WHEN paginas < 150 THEN 'Menos de 150'
            WHEN paginas < 300 THEN '150–299'
            WHEN paginas < 450 THEN '300–449'
            ELSE '450 ou mais' END     AS paginas,
       COUNT(*)                        AS livros,
       ROUND(AVG(l.nota), 2)           AS nota_media
FROM leituras l JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND b.paginas IS NOT NULL AND l.nota IS NOT NULL
GROUP BY 1 ORDER BY MIN(paginas);

-- @ favoritos
SELECT b.livro_id AS id, l.nota, l.favorito
FROM leituras l JOIN livros b USING (livro_id)
WHERE l.estante = 'read' AND (l.nota = 5 OR l.favorito = 1)
ORDER BY l.nota DESC, l.data_lida DESC;

-- @ a_ler
SELECT b.livro_id AS id
FROM leituras l JOIN livros b USING (livro_id)
WHERE l.estante = 'currently-reading'
ORDER BY l.data_adicionado DESC;

-- @ pilha
WITH ref AS (SELECT MAX(data_lida) AS d FROM leituras),
     ritmo AS (SELECT COUNT(*) / 12.0 AS por_mes FROM leituras
               WHERE estante = 'read' AND data_lida > date((SELECT d FROM ref), '-12 months'))
SELECT COUNT(*)                                       AS livros,
       SUM(b.paginas)                                 AS paginas,
       ROUND((SELECT por_mes FROM ritmo), 1)          AS ritmo_mes,
       ROUND(COUNT(*) / (SELECT por_mes FROM ritmo) / 12, 1) AS anos
FROM leituras l JOIN livros b USING (livro_id)
WHERE l.estante = 'to-read';

-- @ espera
SELECT ROUND(AVG(julianday(data_lida) - julianday(data_adicionado))) AS media_dias,
       ROUND(100.0 * SUM(julianday(data_lida) - julianday(data_adicionado) <= 30) / COUNT(*)) AS pct_primeiro_mes
FROM leituras
WHERE estante = 'read' AND data_lida IS NOT NULL AND data_lida >= data_adicionado;

-- @ extremos
SELECT * FROM (SELECT 'mais longo' AS tipo, b.livro_id AS id, b.paginas
               FROM leituras l JOIN livros b USING (livro_id)
               WHERE l.estante = 'read' AND b.paginas IS NOT NULL ORDER BY b.paginas DESC LIMIT 1)
UNION ALL
SELECT * FROM (SELECT 'mais curto', b.livro_id, b.paginas
               FROM leituras l JOIN livros b USING (livro_id)
               WHERE l.estante = 'read' AND b.paginas IS NOT NULL ORDER BY b.paginas ASC LIMIT 1);

-- @ lista
-- todos os livros lidos, para a página "Todas as Leituras"
SELECT b.livro_id AS id, b.titulo, a.nome AS autor, b.ano_original, b.ano_edicao,
       CAST(strftime('%Y', l.data_lida) AS INT) AS ano_lido, l.data_lida, l.nota, b.paginas
FROM leituras l JOIN livros b USING (livro_id) JOIN autores a USING (autor_id)
WHERE l.estante = 'read'
ORDER BY l.data_lida IS NULL, l.data_lida DESC, b.titulo;
