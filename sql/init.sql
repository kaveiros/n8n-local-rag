-- Schema for the n8n PGVector node (table: documents)
-- Embedding model: bge-m3 (1024 dimensions)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content   text NOT NULL,
    metadata  jsonb DEFAULT '{}'::jsonb,
    embedding vector(1024)
);

-- Approximate nearest-neighbour index (cosine distance)
CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING hnsw (embedding vector_cosine_ops);

-- Optional: look up chunks by source file
CREATE INDEX IF NOT EXISTS documents_source_idx
    ON documents ((metadata->>'source'));

-- Reset before a full re-ingest:
-- TRUNCATE documents;
