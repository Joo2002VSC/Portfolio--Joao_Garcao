-- =============================================================
--  Esquema da base de dados de leituras (SQLite)
--  Fonte: exportação da biblioteca do Goodreads
-- =============================================================

DROP TABLE IF EXISTS leituras;
DROP TABLE IF EXISTS livros;
DROP TABLE IF EXISTS autores;

CREATE TABLE autores (
    autor_id       INTEGER PRIMARY KEY,
    nome           TEXT NOT NULL UNIQUE,
    nome_ordenado  TEXT              -- "Apelido, Nome"
);

CREATE TABLE livros (
    livro_id       INTEGER PRIMARY KEY,   -- Book Id do Goodreads
    titulo         TEXT NOT NULL,
    autor_id       INTEGER NOT NULL REFERENCES autores(autor_id),
    outros_autores TEXT,                  -- tradutores, coautores
    isbn13         TEXT,
    editora        TEXT,
    formato        TEXT,                  -- Paperback, Hardcover, ebook...
    paginas        INTEGER,
    ano_edicao     INTEGER,
    ano_original   INTEGER                -- ano da 1.ª publicação da obra
);

CREATE TABLE leituras (
    livro_id        INTEGER PRIMARY KEY REFERENCES livros(livro_id),
    estante         TEXT NOT NULL CHECK (estante IN
                     ('read','currently-reading','to-read','did-not-finish')),
    nota            REAL CHECK (nota BETWEEN 0.5 AND 5),  -- NULL = sem nota; aceita frações (ex.: 4.25)
    data_lida       DATE,
    data_adicionado DATE,
    num_leituras    INTEGER DEFAULT 0,
    favorito        INTEGER DEFAULT 0 CHECK (favorito IN (0,1))
);

CREATE INDEX idx_livros_autor     ON livros(autor_id);
CREATE INDEX idx_leituras_estante ON leituras(estante);
CREATE INDEX idx_leituras_data    ON leituras(data_lida);
