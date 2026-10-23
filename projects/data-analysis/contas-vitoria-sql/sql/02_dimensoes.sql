-- =====================================================================
-- 02_dimensoes.sql : épocas, entidades e rubricas
-- =====================================================================

-- Épocas 2012/13 a 2025/26 geradas com uma CTE recursiva
WITH RECURSIVE anos(a) AS (
    SELECT 2012
    UNION ALL
    SELECT a + 1 FROM anos WHERE a < 2025
)
INSERT INTO epoca (epoca_id, ano_inicio, ano_fim)
SELECT a || '/' || substr(CAST(a + 1 AS TEXT), 3, 2), a, a + 1
FROM anos;

INSERT INTO entidade (entidade_id, nome, descricao) VALUES
('SAD',         'Vitória Sport Clube - Futebol, SAD',
                'Sociedade desportiva: futebol profissional, transferências, UEFA, direitos TV'),
('CLUBE',       'Vitória Sport Clube (associação)',
                'Associação-mãe: Estádio D. Afonso Henriques, Academia, modalidades, maioria da SAD'),
('CONSOLIDADO', 'Grupo Vitória SC (Clube + SAD)',
                'Contas consolidadas, com eliminações intra-grupo');

INSERT INTO rubrica (rubrica_id, nome, natureza, ordem) VALUES
('rendimentos_totais',        'Rendimentos Totais',                      'subtotal',    1),
('rendimentos_operacionais',  'Rendimentos Operacionais',                'subtotal',    2),
('vendas_servicos',           'Vendas e Serviços Prestados',             'rendimento',  3),
('subsidios_exploracao',      'Subsídios de Exploração',                 'rendimento',  4),
('cmvmc',                     'Custo das Mercadorias (CMVMC)',           'gasto',       5),
('fse',                       'Fornecimentos e Serviços Externos (FSE)', 'gasto',       6),
('gastos_pessoal',            'Gastos com Pessoal',                      'gasto',       7),
('imparidades',               'Imparidades',                             'gasto',       8),
('provisoes',                 'Provisões',                               'gasto',       9),
('defice_operacional',        'Défice Operacional',                      'subtotal',   10),
('outros_rendimentos',        'Outros Rendimentos e Ganhos',             'rendimento', 11),
('outros_gastos',             'Outros Gastos e Perdas',                  'gasto',      12),
('ganhos_mep',                'Ganhos MEP (participação na SAD)',        'rendimento', 13),
('ebitda',                    'EBITDA',                                  'subtotal',   14),
('ebitda_sem_transferencias', 'EBITDA sem Transferências',               'subtotal',   15),
('depreciacoes',              'Depreciações e Amortizações',             'gasto',      16),
('resultado_operacional',     'Resultado Operacional',                   'subtotal',   17),
('juros',                     'Juros e Gastos Similares',                'gasto',      18),
('imposto',                   'Imposto sobre o Rendimento',              'gasto',      19),
('resultado_liquido',         'Resultado Líquido do Período',            'subtotal',   20);
