CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384),           -- E5-small-v2 embeddings (384 dimensions)
    metadata JSONB                   
);

CREATE INDEX ON recipes USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON recipes USING gin (metadata);