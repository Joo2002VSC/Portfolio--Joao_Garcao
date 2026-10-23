-- =====================================================================
-- VSC Contas — Base de dados das contas do Vitória Sport Clube
-- 01_schema.sql : estrutura das tabelas (SQLite)
-- Valores monetários em euros (inteiros). Gastos com sinal negativo,
-- tal como aparecem nas demonstrações de resultados.
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS desempenho_desportivo;
DROP TABLE IF EXISTS evento;
DROP TABLE IF EXISTS fonte;
DROP TABLE IF EXISTS divida;
DROP TABLE IF EXISTS operacao_jogador;
DROP TABLE IF EXISTS transferencias;
DROP TABLE IF EXISTS gastos_pessoal_composicao;
DROP TABLE IF EXISTS receitas_composicao;
DROP TABLE IF EXISTS cash_flow;
DROP TABLE IF EXISTS balanco;
DROP TABLE IF EXISTS demonstracao_resultados;
DROP TABLE IF EXISTS rubrica;
DROP TABLE IF EXISTS entidade;
DROP TABLE IF EXISTS epoca;

-- ---------------------------------------------------------------------
-- Dimensões
-- ---------------------------------------------------------------------

-- Época desportiva (o exercício fecha a 30 de junho do ano_fim)
CREATE TABLE epoca (
    epoca_id    TEXT PRIMARY KEY,               -- '2024/25'
    ano_inicio  INTEGER NOT NULL,
    ano_fim     INTEGER NOT NULL,
    CHECK (ano_fim = ano_inicio + 1)
);

-- As três "vistas" do Vitória: SAD, Clube e Grupo consolidado
CREATE TABLE entidade (
    entidade_id TEXT PRIMARY KEY,               -- 'SAD' | 'CLUBE' | 'CONSOLIDADO'
    nome        TEXT NOT NULL,
    descricao   TEXT
);

-- Linhas da demonstração de resultados
CREATE TABLE rubrica (
    rubrica_id  TEXT PRIMARY KEY,
    nome        TEXT NOT NULL,
    natureza    TEXT NOT NULL CHECK (natureza IN ('rendimento', 'gasto', 'subtotal')),
    ordem       INTEGER NOT NULL
);

-- ---------------------------------------------------------------------
-- Factos
-- ---------------------------------------------------------------------

-- Demonstração de resultados em formato longo (uma linha por rubrica)
CREATE TABLE demonstracao_resultados (
    entidade_id TEXT NOT NULL REFERENCES entidade(entidade_id),
    epoca_id    TEXT NOT NULL REFERENCES epoca(epoca_id),
    rubrica_id  TEXT NOT NULL REFERENCES rubrica(rubrica_id),
    valor       INTEGER NOT NULL,
    PRIMARY KEY (entidade_id, epoca_id, rubrica_id)
);

-- Balanço a 30/06 de cada época (NULL = não disponível)
CREATE TABLE balanco (
    entidade_id     TEXT NOT NULL REFERENCES entidade(entidade_id),
    epoca_id        TEXT NOT NULL REFERENCES epoca(epoca_id),
    ativo_total     INTEGER,
    passivo_total   INTEGER,
    capital_proprio INTEGER,                    -- no Clube: fundos patrimoniais
    caixa           INTEGER,
    PRIMARY KEY (entidade_id, epoca_id)
);

-- Fluxos de caixa (só SAD)
CREATE TABLE cash_flow (
    entidade_id   TEXT NOT NULL REFERENCES entidade(entidade_id),
    epoca_id      TEXT NOT NULL REFERENCES epoca(epoca_id),
    operacional   INTEGER,
    investimento  INTEGER,
    financiamento INTEGER,
    PRIMARY KEY (entidade_id, epoca_id)
);

-- Composição das receitas operacionais (os totais coincidem com os
-- rendimentos operacionais consolidados, por isso ficam no CONSOLIDADO)
CREATE TABLE receitas_composicao (
    entidade_id TEXT NOT NULL REFERENCES entidade(entidade_id),
    epoca_id    TEXT NOT NULL REFERENCES epoca(epoca_id),
    categoria   TEXT NOT NULL,
    valor       INTEGER NOT NULL,
    PRIMARY KEY (entidade_id, epoca_id, categoria)
);

-- Composição dos gastos com pessoal (valores consolidados)
CREATE TABLE gastos_pessoal_composicao (
    entidade_id TEXT NOT NULL REFERENCES entidade(entidade_id),
    epoca_id    TEXT NOT NULL REFERENCES epoca(epoca_id),
    categoria   TEXT NOT NULL CHECK (categoria IN ('Atletas', 'Treinadores', 'Outro Pessoal')),
    valor       INTEGER NOT NULL,
    PRIMARY KEY (entidade_id, epoca_id, categoria)
);

-- Transferências de jogadores (resumo por época)
CREATE TABLE transferencias (
    entidade_id          TEXT NOT NULL REFERENCES entidade(entidade_id),
    epoca_id             TEXT NOT NULL REFERENCES epoca(epoca_id),
    vendas_brutas        INTEGER,
    custo_vendas         INTEGER,               -- intermediários, terceiros, solidariedade
    mais_valias_liquidas INTEGER,
    PRIMARY KEY (entidade_id, epoca_id)
);

-- Principais vendas e aquisições individuais
CREATE TABLE operacao_jogador (
    operacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
    epoca_id    TEXT NOT NULL REFERENCES epoca(epoca_id),
    jogador     TEXT NOT NULL,
    tipo        TEXT NOT NULL CHECK (tipo IN ('venda', 'aquisicao')),
    clube       TEXT                            -- clube de destino (vendas)
);

-- Dívida da SAD por credor e maturidade
CREATE TABLE divida (
    data_ref      TEXT NOT NULL,                -- 'AAAA-MM-DD'
    credor        TEXT NOT NULL,
    tipo          TEXT NOT NULL CHECK (tipo IN ('financeira', 'operacional')),
    total         INTEGER NOT NULL,
    menos_1_ano   INTEGER,
    entre_1_3_anos INTEGER,
    mais_3_anos   INTEGER,
    nota          TEXT,
    PRIMARY KEY (data_ref, credor)
);

-- Proveniência e estado dos dados de cada página/época
CREATE TABLE fonte (
    entidade_id TEXT NOT NULL REFERENCES entidade(entidade_id),
    epoca_id    TEXT NOT NULL REFERENCES epoca(epoca_id),
    estado      TEXT,
    documentos  TEXT,
    PRIMARY KEY (entidade_id, epoca_id)
);

-- Acontecimentos e observações relevantes de cada época
CREATE TABLE evento (
    evento_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    entidade_id TEXT NOT NULL REFERENCES entidade(entidade_id),
    epoca_id    TEXT NOT NULL REFERENCES epoca(epoca_id),
    tipo        TEXT NOT NULL CHECK (tipo IN ('evento', 'observacao')),
    descricao   TEXT NOT NULL,
    valor       INTEGER
);

-- Desempenho desportivo da equipa principal em cada época
CREATE TABLE desempenho_desportivo (
    epoca_id            TEXT PRIMARY KEY REFERENCES epoca(epoca_id),
    posicao_liga        INTEGER NOT NULL CHECK (posicao_liga BETWEEN 1 AND 18),
    pontos              INTEGER,
    competicao_europeia TEXT,                   -- NULL = sem Europa
    fase_europeia       TEXT CHECK (fase_europeia IN
                        ('Pré-eliminatória', 'Fase de grupos', 'Oitavos de final')),
    trofeu              TEXT,
    nota                TEXT
);

CREATE INDEX idx_dr_rubrica ON demonstracao_resultados (rubrica_id, epoca_id);
