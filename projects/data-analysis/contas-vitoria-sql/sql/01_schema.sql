-- =====================================================================
-- VSC Contas — Base de dados das contas do Vitória Sport Clube
-- 01_schema.sql : estrutura das tabelas (SQLite)
-- Valores monetários em euros (inteiros). Gastos com sinal negativo,
-- tal como aparecem nas demonstrações de resultados.
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS treinador;
DROP TABLE IF EXISTS reexpressao;
DROP TABLE IF EXISTS financiamento_detalhe;
DROP TABLE IF EXISTS auditoria;
DROP TABLE IF EXISTS partes_relacionadas;
DROP TABLE IF EXISTS passes_jogadores;
DROP TABLE IF EXISTS balanco_rubrica;
DROP TABLE IF EXISTS divergencia;
DROP TABLE IF EXISTS pessoal_sad;
DROP TABLE IF EXISTS balanco_sad_rc;
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
    media_espectadores  INTEGER,                -- média em casa na Liga (0 = COVID)
    competicao_europeia TEXT,                   -- NULL = sem Europa
    fase_europeia       TEXT CHECK (fase_europeia IN
                        ('Pré-eliminatória', 'Fase de grupos', 'Oitavos de final')),
    trofeu              TEXT,
    nota                TEXT
);

-- Balanço detalhado da SAD tal como publicado nos Relatórios e Contas,
-- com dívida financeira e juros (verificado documento a documento)
CREATE TABLE balanco_sad_rc (
    epoca_id             TEXT PRIMARY KEY REFERENCES epoca(epoca_id),
    ativo_nao_corrente   INTEGER NOT NULL,
    ativo_corrente       INTEGER NOT NULL,
    ativo_total          INTEGER NOT NULL,
    passivo_nao_corrente INTEGER NOT NULL,
    passivo_corrente     INTEGER NOT NULL,
    passivo_total        INTEGER NOT NULL,
    capital_proprio      INTEGER NOT NULL,
    caixa                INTEGER,
    financiamentos_nc    INTEGER,               -- financiamentos obtidos não correntes
    financiamentos_c     INTEGER,               -- financiamentos obtidos correntes
    juros_suportados     INTEGER,               -- valor bruto, positivo
    juros_obtidos        INTEGER,
    documento            TEXT,
    CHECK (ABS(ativo_total - ativo_nao_corrente - ativo_corrente) <= 1),
    CHECK (ABS(passivo_total - passivo_nao_corrente - passivo_corrente) <= 1),
    CHECK (ABS(ativo_total - passivo_total - capital_proprio) <= 1)
);

-- Número médio de funcionários e gastos com pessoal da SAD (nota "Benefícios dos empregados")
CREATE TABLE pessoal_sad (
    epoca_id                   TEXT PRIMARY KEY REFERENCES epoca(epoca_id),
    funcionarios               INTEGER NOT NULL,
    jogadores                  INTEGER,
    treinadores_profissional   INTEGER,
    treinadores_formacao       INTEGER,
    apoio_futebol_profissional INTEGER,          -- categoria autónoma desde 2021/22
    outro_pessoal              INTEGER,
    rem_administracao          INTEGER,
    rem_pessoal_administrativo INTEGER,
    rem_treinadores            INTEGER,
    rem_jogadores              INTEGER,
    rem_apoio_futebol          INTEGER,
    encargos_remuneracoes      INTEGER,
    seguro_acidentes           INTEGER,
    outros_gastos              INTEGER,
    total_gastos_pessoal       INTEGER NOT NULL,
    documento                  TEXT
);

-- Divergências encontradas entre fontes secundárias e os Relatórios e Contas
CREATE TABLE divergencia (
    divergencia_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fonte          TEXT NOT NULL,
    epoca_id       TEXT NOT NULL REFERENCES epoca(epoca_id),
    indicador      TEXT NOT NULL,
    valor_fonte    REAL NOT NULL,
    valor_rc       REAL NOT NULL,
    diferenca      REAL NOT NULL,
    nota           TEXT
);

-- Balanço da SAD por rubrica (formato longo), 2016/17 a 2024/25
CREATE TABLE balanco_rubrica (
    epoca_id TEXT NOT NULL REFERENCES epoca(epoca_id),
    lado     TEXT NOT NULL CHECK (lado IN ('ativo', 'passivo')),
    prazo    TEXT NOT NULL CHECK (prazo IN ('corrente', 'nao_corrente')),
    rubrica  TEXT NOT NULL,
    valor    INTEGER NOT NULL,
    PRIMARY KEY (epoca_id, lado, prazo, rubrica)
);

-- Movimentos dos passes de jogadores (ativos intangíveis), nota 7 dos R&C
CREATE TABLE passes_jogadores (
    epoca_id                    TEXT PRIMARY KEY REFERENCES epoca(epoca_id),
    valor_liquido_inicio        INTEGER,
    aquisicoes                  INTEGER,
    amortizacoes                INTEGER,
    valor_bruto_alienado        INTEGER,
    amort_acumuladas_alienadas  INTEGER,
    rescisoes_bruto             INTEGER,
    rescisoes_amort_acumuladas  INTEGER,
    valor_liquido_fim           INTEGER,
    documento                   TEXT
);

-- Transações e saldos entre a SAD e o Clube (partes relacionadas)
CREATE TABLE partes_relacionadas (
    epoca_id TEXT NOT NULL REFERENCES epoca(epoca_id),
    rubrica  TEXT NOT NULL,
    sentido  TEXT NOT NULL CHECK (sentido IN ('receita da SAD', 'gasto da SAD', 'saldo')),
    valor    INTEGER NOT NULL,
    documento TEXT,
    PRIMARY KEY (epoca_id, rubrica)
);

-- Parecer do auditor (certificação legal de contas) e artigo 35.º do CSC
CREATE TABLE auditoria (
    epoca_id               TEXT PRIMARY KEY REFERENCES epoca(epoca_id),
    parecer_auditor        TEXT NOT NULL,
    artigo_35_no_relatorio INTEGER CHECK (artigo_35_no_relatorio IN (0, 1)),
    nota                   TEXT
);

-- Dívida financeira por instrumento e maturidade
CREATE TABLE financiamento_detalhe (
    data_ref       TEXT NOT NULL,
    instrumento    TEXT NOT NULL,
    total          INTEGER NOT NULL,
    menos_1_ano    INTEGER,
    entre_1_3_anos INTEGER,
    documento      TEXT,
    PRIMARY KEY (data_ref, instrumento)
);

-- Valores de 2024/25 reexpressos nas contas de 2025/26 (custo amortizado)
CREATE TABLE reexpressao (
    epoca_id         TEXT NOT NULL REFERENCES epoca(epoca_id),
    indicador        TEXT NOT NULL,
    valor_original   INTEGER NOT NULL,
    valor_reexpresso INTEGER NOT NULL,
    documento        TEXT,
    PRIMARY KEY (epoca_id, indicador)
);

-- Treinadores principais e interinos (fonte: Wikipédia)
CREATE TABLE treinador (
    treinador_id INTEGER PRIMARY KEY AUTOINCREMENT,
    periodo      TEXT NOT NULL,
    nome         TEXT NOT NULL,
    tipo         TEXT NOT NULL CHECK (tipo IN ('principal', 'interino'))
);

-- Taxas de juro de referência (mercado e crédito), em percentagem.
CREATE TABLE taxa_referencia (
    data       TEXT NOT NULL,                  -- AAAA-MM-DD (mês da observação)
    indicador  TEXT NOT NULL CHECK (indicador IN ('euribor_12m', 'ot_portugal_10a', 'credito_empresas_pt')),
    taxa_pct   REAL NOT NULL,
    fonte      TEXT NOT NULL,
    PRIMARY KEY (data, indicador)
);

-- Alterações das taxas diretoras do BCE (em vigor a partir de data_efeito).
CREATE TABLE bce_taxa (
    data_efeito          TEXT PRIMARY KEY,
    facilidade_deposito  REAL NOT NULL,
    refinanciamento      REAL NOT NULL
);

CREATE INDEX idx_dr_rubrica ON demonstracao_resultados (rubrica_id, epoca_id);
