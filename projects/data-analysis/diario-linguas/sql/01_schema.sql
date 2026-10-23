-- =============================================================
--  Diário de Aprendizagem de Línguas — Esquema da base de dados
--  Motor: SQLite 3
-- =============================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS revisoes;
DROP TABLE IF EXISTS sessoes;
DROP TABLE IF EXISTS palavras;
DROP TABLE IF EXISTS idiomas;

-- Línguas em estudo
CREATE TABLE idiomas (
    id           INTEGER PRIMARY KEY,
    codigo       TEXT NOT NULL UNIQUE,          -- ISO 639-1: 'nl', 'fr', 'it'
    nome         TEXT NOT NULL,
    nivel_atual  TEXT CHECK (nivel_atual IN ('A1','A2','B1','B2','C1','C2')),
    objetivo     TEXT                           -- ex.: 'Manter o nível'
);

-- Vocabulário: uma linha por palavra ou expressão aprendida
CREATE TABLE palavras (
    id                INTEGER PRIMARY KEY,
    idioma_id         INTEGER NOT NULL REFERENCES idiomas(id),
    termo             TEXT NOT NULL,
    traducao_pt       TEXT NOT NULL,
    classe            TEXT CHECK (classe IN ('nome','verbo','adjetivo','advérbio','expressão','outro')),
    tema              TEXT,                     -- ex.: 'saudações', 'comida', 'trabalho'
    data_adicionada   DATE NOT NULL,
    UNIQUE (idioma_id, termo)
);

-- Sessões de estudo
CREATE TABLE sessoes (
    id            INTEGER PRIMARY KEY,
    idioma_id     INTEGER NOT NULL REFERENCES idiomas(id),
    data          DATE NOT NULL,
    duracao_min   INTEGER NOT NULL CHECK (duracao_min > 0),
    tipo          TEXT NOT NULL CHECK (tipo IN ('vocabulário','gramática','conversa','leitura','áudio/vídeo')),
    recurso       TEXT,                         -- ex.: 'Duolingo', 'podcast', 'Claude'
    notas         TEXT
);

-- Revisões: cada vez que testo uma palavra (acertei ou errei)
CREATE TABLE revisoes (
    id          INTEGER PRIMARY KEY,
    palavra_id  INTEGER NOT NULL REFERENCES palavras(id),
    sessao_id   INTEGER REFERENCES sessoes(id),
    data        DATE NOT NULL,
    acertou     INTEGER NOT NULL CHECK (acertou IN (0,1))
);

CREATE INDEX idx_palavras_idioma_data ON palavras(idioma_id, data_adicionada);
CREATE INDEX idx_sessoes_idioma_data  ON sessoes(idioma_id, data);
CREATE INDEX idx_revisoes_palavra     ON revisoes(palavra_id);

-- Vista auxiliar: estatísticas de revisão por palavra
DROP VIEW IF EXISTS v_desempenho_palavras;
CREATE VIEW v_desempenho_palavras AS
SELECT  p.id,
        i.nome                         AS idioma,
        p.termo,
        p.traducao_pt,
        p.tema,
        COUNT(r.id)                    AS revisoes,
        SUM(1 - r.acertou)             AS erros,
        ROUND(100.0 * SUM(1 - r.acertou) / NULLIF(COUNT(r.id),0), 1) AS taxa_erro_pct,
        MAX(r.data)                    AS ultima_revisao
FROM palavras p
JOIN idiomas  i ON i.id = p.idioma_id
LEFT JOIN revisoes r ON r.palavra_id = p.id
GROUP BY p.id;
