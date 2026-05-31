-- Document metadata and audit trail
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500),
    source VARCHAR(255),
    content_hash VARCHAR(64),
    chunk_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_source ON documents(source);
CREATE INDEX idx_documents_created_at ON documents(created_at);

-- Query audit log for evaluation and compliance
CREATE TABLE IF NOT EXISTS query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    response_text TEXT,
    retrieved_chunk_ids TEXT[],
    latency_ms INTEGER,
    token_count INTEGER,
    estimated_cost_usd NUMERIC(10, 6),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_query_logs_created_at ON query_logs(created_at);

-- Evaluation scorecards
CREATE TABLE IF NOT EXISTS evaluation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_name VARCHAR(255) NOT NULL,
    metrics JSONB NOT NULL,
    sample_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
