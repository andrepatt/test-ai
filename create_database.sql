-- Crea il database (se non esiste già)
CREATE DATABASE aru_database;

-- Usa il database
\c aru_database;

-- Crea la tabella per le ARU
CREATE TABLE arus (
    id SERIAL PRIMARY KEY,
    original_aru TEXT,
    revised_aru TEXT,
    aru_summary TEXT,
    ufp_results TEXT,
    supervisor_report TEXT,
    metadata JSONB
);
